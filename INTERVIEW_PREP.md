# Face Recognition Attendance System — Backend Interview Preparation Guide

> **Scope:** Backend · Computer Vision · SQLite · System Design · Performance
> **Excluded:** CSS, widgets, sidebar, routing UI — your interviewer does NOT care about these.

---

## SECTION 1 — PROJECT ARCHITECTURE

### Overview

The system is a monolithic, locally-deployed AI attendance system with strict internal
layering. Despite running in a single Python process the code enforces clean separation:
presentation, business logic, and data storage never mix.

```
+----------------------------------------------+
|          Streamlit Browser Client            |
|     (User interaction / Frame display)       |
+------------------+---------------------------+
                   | calls
+------------------v---------------------------+
|              streamlit_app.py                |
|          (Entry point / SPA router)          |
+------------------+---------------------------+
                   | imports
+------------------v---------------------------+
|             backend_api.py                   |
|  +-----------+  +----------+  +-----------+  |
|  |Model Layer|  | DB Layer |  |Cam Layer  |  |
|  |(InsightFace  | (SQLite) |  | (OpenCV)  |  |
|  +-----------+  +----------+  +-----------+  |
+----+----------------+----------------+-------+
     | uses           | uses           | uses
+----v------+  +------v-------+  +----v------+
| utils.py  |  |  faces.db    |  |attendance |
|(math fns) |  |(embeddings)  |  |   .db     |
+-----------+  +--------------+  +-----------+
     |
+----v------+
| config.py |
|(constants)|
+-----------+
```

### Complete Execution Flow

```
1. streamlit run streamlit_app.py
        |
2. Python imports backend_api.py
        |
3. backend_api._init_databases()  [runs at MODULE LEVEL, before any user action]
   -> Creates faces.db      (table: faces)
   -> Creates attendance.db (table: attendance)
        |
4. User navigates to Recognition page, clicks START
        |
5. api.open_camera() -> cv2.VideoCapture(0)
        |
6. LOOP per frame:
   a. api.capture_single_frame()   -> BGR NumPy array
   b. api.recognize_faces_in_frame(frame)
       +-- get_face_app()          -> InsightFace model (cached after first load)
       +-- get_all_embeddings()    -> (N,512) matrix (cached from DB)
       +-- app.get(frame)          -> detect + embed all faces in frame
       +-- normalize_embedding()   -> L2 normalize each live query vector
       +-- np.dot(matrix, vec)    -> ALL N similarity scores in one BLAS call
       +-- compare to threshold   -> recognized vs Unknown
       +-- draw bounding boxes    -> annotate frame with names + scores
        |
7. api.mark_attendance(name)
   -> is_attendance_marked(name, today)? NO -> INSERT into attendance.db
        |
8. User clicks STOP -> api.release_camera() -> cap.release()
```

---

## SECTION 2 — IMPORTANT FILES

### config.py   [ESSENTIAL — 5/5]

Purpose: Single source of truth for ALL system constants.
When executed: Immediately on any import of backend_api or utils.
Called by: backend_api.py, utils.py, ui/pages/recognition.py.

```python
DB_NAME              = "faces.db"            # SQLite: registered embeddings
ATTENDANCE_DB        = "attendance.db"       # SQLite: attendance log
SIMILARITY_THRESHOLD = 89                   # recognition score cutoff (0-100)
MODEL_NAME           = "buffalo_l"           # InsightFace model (largest, best)
CAMERA_ID            = 0                    # Index of default system webcam
REGISTRATIONS_DIR    = "data/registrations" # Raw registration photos on disk
LOG_LEVEL            = "INFO"               # Python logging verbosity
```

Why a config file? Hardcoding 89 inside backend_api.py means hunting through
code to change the threshold. One edit in config.py propagates everywhere.

---

### utils.py   [ESSENTIAL — 5/5]

Purpose: Pure math and logging functions shared by all modules.
The math here IS the recognition engine. Know every function cold.

---

### backend_api.py   [ESSENTIAL — 5/5]

Purpose: Entire business logic — DB access, camera, ML inference, attendance.
When executed: On first import. Module-level code (_init_databases) runs immediately.
Called by: All UI pages and streamlit_app.py.
THIS IS WHAT YOUR INTERVIEWER WILL ASK ABOUT.

---

### ui/pages/recognition.py   [GOOD TO KNOW — 3/5]

Only the frame loop and attendance marking call matter for interview purposes.
Ignore all Streamlit widget/column/layout code.

---

### ui/pages/register_user.py   [GOOD TO KNOW — 3/5]

Know the data flow: validate -> save to disk -> extract -> average -> store.
Ignore form widgets and preview thumbnails.

---

### Files SAFE TO IGNORE in interview

| File | Why |
|---|---|
| ui/styles.py | 900+ lines of CSS. Zero logic. |
| ui/components.py | HTML f-string template functions. |
| ui/pages/dashboard.py | Thin wrapper over get_dashboard_stats(). |
| ui/pages/settings.py | UI form, no backend writes. |
| ui/pages/about.py | Static text. |
| ui/pages/attendance_page.py | Thin wrapper over get_attendance_records(). |
| streamlit_app.py | SPA router. No business logic. |
| patch_delete.py | One-off maintenance script, not runtime. |


---

## SECTION 3 — EVERY IMPORTANT FUNCTION

### utils.normalize_embedding(embedding)

Purpose: Convert raw face embedding to unit vector (L2 norm = 1.0).

Key insight: For unit vectors, dot product = cosine similarity.
This identity makes fast vectorized similarity search possible.

- Input:  1-D NumPy float32 array, shape (512,), raw output from InsightFace.
- Output: 1-D NumPy float32 array, shape (512,), with ||output|| == 1.0.

```python
return embedding / np.linalg.norm(embedding)
```

`np.linalg.norm` computes: `sqrt(x1^2 + x2^2 + ... + x512^2)`
Dividing every element by this scalar -> length becomes exactly 1.0.

- **Time:** O(d) where d=512
- **Space:** O(d)

What if skipped? Dot product still executes but produces arbitrary-range values.
The threshold of 89 becomes meaningless — raw vectors have inconsistent magnitudes.
Normalization makes scores comparable across all images and sessions.

---

### utils.cosine_similarity(a, b)

Purpose: Compute similarity between two normalized face vectors.

```python
return float(np.dot(a, b))
```

Since both `a` and `b` are L2-normalized (norm=1), the cosine formula:
```
cos(theta) = (a . b) / (|a| x |b|)
```
simplifies to just `a . b` because |a| = |b| = 1.

- Output range: -1.0 to 1.0 (in practice 0.0 to 1.0 for face embeddings)
- In backend_api.py: multiplied by 100 -> percentage (0-100%)
- SIMILARITY_THRESHOLD = 89 means the score must be >= 89%
- **Time:** O(d) — single dot product over 512 elements

Note: backend_api.py uses vectorized `np.dot(matrix, vector)` for batch
comparisons — approximately 100x faster than calling this function per pair.

---

### backend_api._init_databases()

Purpose: Create both SQLite databases and tables if they do not exist.
When called: Module-level — before any user interaction, on first import.

```python
with sqlite3.connect(DB_NAME) as conn:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS faces "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, embedding BLOB NOT NULL)"
    )
with sqlite3.connect(ATTENDANCE_DB) as conn:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS attendance "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, date TEXT NOT NULL, time TEXT NOT NULL)"
    )
```

`CREATE TABLE IF NOT EXISTS` is **idempotent**: safe on every startup, no data destroyed.

The `with sqlite3.connect()` context manager:
- On success: auto-calls `conn.commit()`
- On exception: auto-calls `conn.rollback()`
- **Does NOT auto-close** the connection. `conn.close()` must be called explicitly.

---

### backend_api.get_face_app()

Purpose: Load InsightFace AI model exactly ONCE. Return cached instance.
Design pattern: **Lazy Initialization (Singleton via global variable).**

```python
global _face_app
if _face_app is None:
    from insightface.app import FaceAnalysis
    _face_app = FaceAnalysis(name=MODEL_NAME)   # "buffalo_l"
    _face_app.prepare(ctx_id=0, det_size=(320, 320))
return _face_app
```

- `ctx_id=0`: Request GPU 0. ONNX Runtime falls back to CPU silently if no GPU.
- `det_size=(320,320)`: Internal detection resolution. Balances speed vs recall.
- Import inside function: InsightFace takes 2-4 seconds to load. Deferring the
  import means the app starts instantly — model loads only on first recognition.
- **Time:** First call O(model_size) ~ 2-4 seconds. All subsequent calls O(1).

Why not load at module level? `streamlit run` would hang 3-4 seconds before the UI appeared.

---

### backend_api.get_all_embeddings()

Purpose: Return all registered users as an in-memory NumPy matrix.
Cache the result — the database is read only ONCE per session.

- **Outputs:** Tuple `(names_list, embs_matrix)` where:
  - `names_list` = `["Alice", "Bob", "Charlie"]` (Python list)
  - `embs_matrix` = NumPy float32 array, shape `(N, 512)` (N = num registered users)

```python
global _embeddings_cache
if _embeddings_cache is not None:
    return _embeddings_cache     # O(1), zero DB access

cursor.execute("SELECT name, embedding FROM faces")
rows   = cursor.fetchall()
names  = [r[0] for r in rows]
embs   = np.array([normalize_embedding(np.frombuffer(r[1], dtype=np.float32))
                   for r in rows])
_embeddings_cache = (names, embs)
return _embeddings_cache
```

Key detail — `np.frombuffer(r[1], dtype=np.float32)`:
BLOB bytes reinterpreted as float32 array **WITHOUT COPYING** (zero-copy).
2048 raw bytes -> 512 float32 values.

Why normalize on read? Defensive: re-normalizing guarantees unit norm even if
float precision was lost during BLOB serialization.

Why a matrix? `np.dot(matrix, query)` is ONE BLAS operation computing all N scores
simultaneously. Python loop per vector ~100x slower for 100 users.

Cache invalidation: `_embeddings_cache = None` after every write to faces.db.
Next `get_all_embeddings()` call re-queries DB and rebuilds the matrix.

- **Time:** First call O(N x 512). Subsequent: O(1).
- **Space:** O(N x 512) in RAM.

---

### backend_api.recognize_faces_in_frame(frame)

Purpose: Core recognition. Detect all faces in one video frame, compare to DB,
annotate frame with colored bounding boxes and labels.

- **Input:** BGR NumPy array `(H x W x 3)` from OpenCV.
- **Output:** Tuple `(annotated_frame, results_list)`.

Step-by-step:

```
Step 1: app = get_face_app()                   <- cached model, O(1)
Step 2: names_list, embs_matrix = get_all_embeddings() <- cached, O(1)
Step 3: detected = app.get(frame)              <- MOST EXPENSIVE: 2 CNNs
        Each Face: .bbox [x1,y1,x2,y2], .embedding (512-D raw), .det_score
Step 4: query_emb = normalize(face.embedding)  <- O(512)
Step 5: sims = np.dot(embs_matrix, query_emb) * 100  <- O(N x 512), one BLAS call
        embs_matrix (N,512) . query_emb (512,) -> output shape (N,)
Step 6: best_idx = np.argmax(sims)             <- O(N)
        best_sim = sims[best_idx]
        best_name = names_list[best_idx]
Step 7: recognized = (best_sim >= SIMILARITY_THRESHOLD)
        if not recognized: best_name = "Unknown"
Step 8: Draw GREEN (recognized) or RED (unknown) bounding box + label
```

**Time per frame:** O(H x W) detection + O(N x 512) similarity + O(N) argmax

Why BGR not RGB?
OpenCV historical convention from Windows BITMAPINFOHEADER byte ordering.
InsightFace also expects BGR. PIL/browser expects RGB.
`cv2.cvtColor(frame, BGR2RGB)` is applied before display.

---

### backend_api.update_user_faces(person_name, new_images, delete_paths)

Purpose: Full registration pipeline. Validate, save to disk, re-extract all
embeddings, average them, store single averaged vector in DB.

Why average? Single photo = one lighting/angle/expression. Averaged embedding
is a centroid in 512-D space, robust to variation. More photos = better accuracy.

```
1. validate_face_image() for each new image
2. final_count = len(existing) - len(delete_paths) + len(new_images)
   Reject if final_count < 3
3. Delete old images from disk (os.remove)
4. Save new images: data/registrations/<name>/<uuid>.jpg
5. Re-read ALL images for this user from disk (glob.glob)
6. For each image:
   cv2.imread -> BGR array
   app.get    -> detect faces
   Filter: det_score >= 0.6
   Select: LARGEST face by bounding box area
   normalize_embedding -> unit vector
   Append to embeddings list
7. avg_emb = normalize_embedding(np.mean(all_embeddings, axis=0))
8. User in DB? UPDATE faces SET embedding = ? WHERE name = ?
   New user?   INSERT INTO faces (name, embedding) VALUES (?, ?)
9. _embeddings_cache = None
```

- **UUID filenames:** `uuid.uuid4().hex` = random 128-bit ID. Collision-proof. No sequential exposure.
- **Largest face:** Filters out background faces when user uploads group photos.
- **Double normalize:** `np.mean` of unit vectors is NOT unit. Must re-normalize the average.
- **Time:** O(K x H x W) dominated by InsightFace inference on every stored image.

---

### backend_api.validate_face_image(img_bgr)

Purpose: Gate-keeper that rejects bad images before saving to disk.

Four validation rules (all must pass):
```
Rule 1: >= 1 face detected       else "No face detected."
Rule 2: exactly 1 face           else "Multiple faces detected."
Rule 3: det_score >= 0.6        else "Confidence too low."
Rule 4: bbox area >= 4000 px^2  else "Face too small or blurry."
```

- **Why 4000 px^2?** Below ~63x63 pixels, faces lack detail for reliable embeddings.
- **Why reject multiple faces?** Registration is 1-to-1. Two faces = ambiguous.

---

### backend_api.mark_attendance(name)

Purpose: Record attendance once per calendar day per person.

```python
now      = datetime.now()
date_str = now.strftime("%Y-%m-%d")
time_str = now.strftime("%H:%M:%S")

if is_attendance_marked(name, date_str):
    return False, "Already marked for {name} today."

cursor.execute(
    "INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
    (name, date_str, time_str),
)
conn.commit()
```

**Idempotency:** Calling 100 times for same person same day = exactly ONE record.

Why separate date and time columns?
Primary filter is `WHERE date = ?` (simple, fast, indexable).
A combined datetime would need `LIKE` or `date()` function — slower and harder to index.

Parameterized queries: `?` placeholders prevent SQL injection.
NEVER: `cursor.execute(f"...WHERE name = '{name}'")`

---

### Camera Lifecycle: open_camera / release_camera / capture_single_frame

```python
_camera_cap = None  # module-level persistent handle

def open_camera() -> bool:
    if _camera_cap is not None and _camera_cap.isOpened():
        return True   # Already open, zero overhead
    _camera_cap = cv2.VideoCapture(CAMERA_ID)
    return _camera_cap.isOpened()

def release_camera():
    if _camera_cap is not None:
        _camera_cap.release()
        _camera_cap = None

def capture_single_frame() -> Optional[np.ndarray]:
    ret, frame = _camera_cap.read()
    return frame if ret else None
```

**Why persistent handle?**
`cv2.VideoCapture(0)` takes ~500ms (driver init + resolution negotiation + buffer allocation).
Per-frame open/close = ~2 FPS max. Persistent handle = 30 FPS native rate. ~15x faster.

**Why `cap.release()`?**
OS holds hardware lock on webcam device. Without releasing:
- Camera unusable by any other application.
- Webcam LED stays on (privacy concern).


---

## SECTION 4 — DATABASE

### Schema

**faces.db**

| Column | Type | Purpose |
|---|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Unique auto-incrementing row ID |
| name | TEXT NOT NULL | Registered person full name |
| embedding | BLOB NOT NULL | 512 x float32 = 2048 raw bytes |

ONE ROW = ONE PERSON. Updates use `UPDATE` (not DELETE + INSERT).

---

**attendance.db**

| Column | Type | Purpose |
|---|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Unique auto-incrementing row ID |
| name | TEXT NOT NULL | Person name from recognition result |
| date | TEXT NOT NULL | YYYY-MM-DD format |
| time | TEXT NOT NULL | HH:MM:SS format |

ONE ROW = ONE ATTENDANCE EVENT. One row per person per day.

---

### Embedding Storage

Storing (NumPy -> SQLite BLOB):
```python
avg_emb.tobytes()  # 512 float32 values x 4 bytes = 2048 bytes
```

Retrieving (SQLite BLOB -> NumPy):
```python
np.frombuffer(row[1], dtype=np.float32)  # ZERO-COPY: no data duplication
```

`np.frombuffer` creates a NumPy array that reads directly from the bytes object in memory.

---

### Complete SQL Query Reference

| Function | SQL |
|---|---|
| `_init_databases` | `CREATE TABLE IF NOT EXISTS faces (id INTEGER PK, name TEXT, embedding BLOB)` |
| `_init_databases` | `CREATE TABLE IF NOT EXISTS attendance (id INTEGER PK, name TEXT, date TEXT, time TEXT)` |
| `get_all_users` | `SELECT id, name FROM faces ORDER BY id` |
| `get_all_embeddings` | `SELECT name, embedding FROM faces` |
| `user_exists` | `SELECT id FROM faces WHERE name = ?` |
| `delete_user` | `DELETE FROM faces WHERE name = ?` |
| `update_user_faces` (update) | `UPDATE faces SET embedding = ? WHERE name = ?` |
| `update_user_faces` (insert) | `INSERT INTO faces (name, embedding) VALUES (?, ?)` |
| `is_attendance_marked` | `SELECT id FROM attendance WHERE name = ? AND date = ?` |
| `mark_attendance` | `INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)` |
| `get_attendance_records` | `SELECT id, name, date, time FROM attendance WHERE date = ? ORDER BY time DESC` |
| `get_dashboard_stats` (1) | `SELECT COUNT(*) FROM faces` |
| `get_dashboard_stats` (2) | `SELECT COUNT(*) FROM attendance WHERE date = ?` |
| `get_dashboard_stats` (3) | `SELECT COUNT(*) FROM attendance` |
| `get_dashboard_stats` (4) | `SELECT date, COUNT(*) FROM attendance GROUP BY date ORDER BY date ASC LIMIT 14` |
| `get_dashboard_stats` (5) | `SELECT name, date, time FROM attendance ORDER BY date DESC, time DESC LIMIT 10` |
| `clear_all_attendance` | `DELETE FROM attendance` |

---

### Why SQLite?

| Criterion | SQLite | PostgreSQL |
|---|---|---|
| Setup | Zero, file-based, no server | Requires server process |
| Dependencies | Python stdlib built-in | psycopg2 + server |
| Concurrency | Single-writer, multi-reader | Full ACID multi-writer |
| Scale | < 100k rows ideal | Millions of rows |
| Portability | Single .db file | Requires pg_dump |

For a local, single-user system SQLite is the correct choice. PostgreSQL is overengineering.

---

### Cache Mechanism (Write-Through Invalidation)

```
First call to get_all_embeddings():
  DB read -> deserialize all BLOBs with np.frombuffer (zero-copy)
  normalize_embedding() on each vector
  Build (N, 512) NumPy matrix
  Store in _embeddings_cache

All subsequent calls (same session):
  Return _embeddings_cache immediately (zero DB access, zero deserialization)

User registered / updated / deleted:
  _embeddings_cache = None   [INVALIDATED]

Next call after invalidation:
  Full rebuild from DB
```

**Strategy: Write-Through Invalidation.**
When source of truth (DB) changes, wipe the cache entirely.
Rebuild on next read. Simpler than in-place updates. Always guaranteed correct.

---

## SECTION 5 — FACE RECOGNITION PIPELINE

### Registration Pipeline

```
User provides >= 3 images (camera or file upload)
        |
For each image: validate_face_image()
  Reject: 0 faces detected      -> "No face detected"
  Reject: >1 face detected      -> "Multiple faces detected"
  Reject: det_score < 0.6       -> "Confidence too low"
  Reject: bbox area < 4000 px   -> "Face too small or blurry"
        |
final_count = existing - deletes + new images
Reject if final_count < 3
        |
Delete selected images from disk (os.remove)
        |
Save new images: data/registrations/<name>/<uuid>.jpg
        |
Re-read ALL disk images for this user (glob.glob)
        |
For each image:
  cv2.imread -> BGR NumPy array
  app.get    -> detect faces
  Filter:      det_score >= 0.6
  Select:      LARGEST face by (bbox[2]-bbox[0]) x (bbox[3]-bbox[1])
  normalize_embedding -> unit vector
  Append to embeddings list
        |
avg_emb = normalize_embedding( np.mean(all_embeddings, axis=0) )
        |
User exists? UPDATE faces SET embedding = ?
New user?    INSERT INTO faces (name, embedding)
        |
_embeddings_cache = None
```

---

### Live Recognition Pipeline

```
Webcam -> cv2.VideoCapture.read() -> BGR NumPy array (H x W x 3)
        |
InsightFace app.get(frame):
  Internal resize to det_size = (320, 320)
  RetinaFace: finds all face bounding boxes + confidence scores
  ArcFace:    generates 512-D raw embedding for each detected face
  Returns:    list of Face objects
        |
For each Face object:
  bbox      = face.bbox.astype(int)        -> [x1, y1, x2, y2]
  query_emb = normalize(face.embedding)    -> live unit vector (512-D)
        |
If registered users exist:
  sims      = np.dot(embs_matrix, query_emb)  -> shape (N,)
  sims      = sims * 100                       -> percentage scale
  best_idx  = np.argmax(sims)
  best_score = sims[best_idx]
  best_name  = names_list[best_idx]
        |
Threshold decision:
  best_score >= 89 -> recognized=True,  label="{name}  {score:.1f}%"
  best_score < 89  -> recognized=False, best_name="Unknown"
        |
Draw GREEN (recognized) or RED (unknown) bounding box + label text on frame
        |
Return (annotated_frame, results_list)
        |
For each recognized person:
  api.mark_attendance(name)
  -> is_attendance_marked(name, today)? NO -> INSERT into attendance.db
```

---

### InsightFace buffalo_l: Two Models Inside

| Component | Model | Backbone | Task |
|---|---|---|---|
| Face Detector | RetinaFace | ResNet-50 + FPN | Bounding boxes + 5 landmarks |
| Face Recognizer | ArcFace | ResNet-100 | 512-D embedding generation |

**ArcFace explained:**
Standard softmax: trains for classification. ArcFace: adds angular margin penalty.
Forces different identities to be **angularly separated** in embedding space.
Result: embeddings are geometrically discriminative face fingerprints.
Trained on MS-Celeb-1M + VGGFace2. Accuracy: ~99.8% on LFW benchmark.

**Why 512 dimensions?**
Empirically validated in ArcFace research paper. Too few (64) = insufficient detail.
Too many (2048) = diminishing accuracy returns + higher compute cost.
512 = established sweet spot.

**Face alignment:**
5 landmarks (eye centers, nose tip, mouth corners)
-> affine transformation -> canonical 112x112 front-facing crop.
CRITICAL: Without alignment, same face at different angles = different embeddings.
InsightFace handles this automatically before embedding generation.

---

### The 89% Threshold

`cos(theta) = 0.89` means vectors ~27 degrees apart in 512-D space.
Same person: typically 90-99%. Different people: typically 40-80%.

| Setting | False Positives | False Negatives | Use Case |
|---|---|---|---|
| 95% (strict) | Very low | High — real users often rejected | High-security access |
| 89% (current) | Low | Low — balanced for indoor webcam | Attendance tracking |
| 70% (permissive) | High | Very low — wrong person may be marked | Not recommended |

No universal correct threshold. Tuned empirically for specific hardware + lighting.

---

### Cosine Similarity vs Euclidean Distance

| Property | Cosine Similarity | Euclidean Distance |
|---|---|---|
| Sensitive to magnitude | No (angle only) | Yes |
| Intuition | Angle between vectors | Straight-line distance |
| Range | -1 to 1 | 0 to infinity |
| After L2 normalization | Both produce same ranking | — |

After L2 normalization: `d_euclidean = sqrt(2 - 2*cos(theta))`.
Monotonically related — same ranking either way.
This project uses cosine (dot product) because it is numerically simpler (no sqrt, no denominator).

---

### Duplicate Attendance Prevention

```python
def is_attendance_marked(name, date_str):
    cursor.execute(
        "SELECT id FROM attendance WHERE name = ? AND date = ?",
        (name, date_str),
    )
    return cursor.fetchone() is not None
```

Current: **Check-then-Insert** (application-level enforcement).

Better production approach (mention in interview):
```sql
ALTER TABLE attendance ADD UNIQUE(name, date);
-- Then use:
INSERT OR IGNORE INTO attendance (name, date, time) VALUES (?, ?, ?)
```
DB enforces uniqueness at storage level. Eliminates pre-check. Race-condition safe.

Race condition in current code: Two threads could both pass `is_attendance_marked()`
simultaneously and both INSERT. Python's GIL prevents this in single-process Streamlit,
but critical issue in multi-worker deployment.


---

## SECTION 6 — PERFORMANCE OPTIMIZATIONS

### Optimization 1: In-Memory Embedding Cache

**Problem:** 30 FPS x 50 users = 1,500 DB query cycles/second without caching.
Each cycle: open connection, SELECT all rows, deserialize BLOBs, normalize, close.

**Solution:** Cache `(names_list, embs_matrix)` in `_embeddings_cache` after first load.
Subsequent calls return cached result in O(1) — zero DB access.

**Gain:** ~50ms/frame (I/O bound) → ~0.1ms/frame (memory bound).
**Tradeoff:** Stale if another process modifies the DB externally. Acceptable for local system.

---

### Optimization 2: Vectorized Similarity Search

**Problem (naive loop):**
```python
for name, emb in registered:
    score = cosine_similarity(emb, query_emb)  # Python interpreter overhead per call
```

**Solution (vectorized):**
```python
sims = np.dot(embs_matrix, query_emb)  # Single BLAS operation
```

NumPy dispatches to BLAS (Basic Linear Algebra Subprograms) — C/Fortran routines
compiled to use SIMD instructions (AVX, SSE). All N×512 multiply-adds run in parallel.

**Gain:** ~100x faster than Python loop for 100 users.

---

### Optimization 3: Lazy Model Loading

**Problem:** InsightFace loads ~500MB of ONNX model weights. Takes 2-4 seconds.
**Solution:** Load inside `get_face_app()` guarded by `if _face_app is None`.
**Gain:** App startup instant. Model loads only on first recognition trigger.

---

### Optimization 4: Persistent Camera Handle

**Problem:** `cv2.VideoCapture(0)` takes ~500ms per call (driver init + buffer allocation).
Per-frame open/close = ~2 FPS maximum.

**Solution:** `_camera_cap` opened once in `open_camera()`, reused in `capture_single_frame()`,
released only when user clicks Stop in `release_camera()`.

**Gain:** Frame capture 500ms → 33ms (30 FPS native rate). ~15x faster.

---

### Optimization 5: Pre-normalized Embeddings

**Problem:** Full cosine formula needs two `np.linalg.norm()` calls + one dot product.
**Solution:** Normalize before storing. At runtime only `a . b` needed (divide by 1.0×1.0 = free).
**Gain:** ~30% fewer floating-point operations per similarity comparison.

---

### Remaining Bottlenecks (mention these to show senior-level thinking)

| Bottleneck | Root Cause | Production Fix |
|---|---|---|
| Synchronous detection | `app.get(frame)` blocks thread ~150ms | Background thread + frame queue |
| No DB index on date | Full table scan for `WHERE date=?` | `CREATE INDEX idx_date ON attendance(date)` |
| Linear similarity search | `np.dot` is O(N × 512) | FAISS HNSW for N > 10,000 |
| Single SQLite writer | File-level write lock | PostgreSQL + connection pool |
| No UNIQUE constraint | Application-level check can race in multi-thread | `UNIQUE(name, date)` + `INSERT OR IGNORE` |

---

## SECTION 7 — IMPORTANT LIBRARIES

### OpenCV (cv2)

| Method | Purpose |
|---|---|
| `cv2.VideoCapture(id)` | Open webcam via OS driver |
| `cap.read()` | Read one BGR NumPy frame |
| `cap.release()` | Release OS hardware lock on camera |
| `cv2.imencode(".jpg", frame)` | Compress frame to JPEG bytes for browser transfer |
| `cv2.cvtColor(f, BGR2RGB)` | Color space conversion at BGR/RGB boundary |
| `cv2.rectangle()` | Draw bounding box on annotated frame |
| `cv2.putText()` | Draw label text on annotated frame |
| `cv2.imread(path)` | Load image from disk as BGR NumPy array |
| `cv2.imwrite(path, img)` | Save NumPy array as image file |

**Why BGR?** OpenCV historical convention from Windows BITMAPINFOHEADER byte ordering.
InsightFace also expects BGR. PIL/browser expect RGB.
`cv2.cvtColor()` applied at every framework boundary.

---

### InsightFace

Provides RetinaFace detection + ArcFace embedding in a single `app.get()` call.

**Chosen because:**
- Local-only — no API key, no network, no data leaves machine
- State-of-the-art accuracy (~99.8% LFW)
- ONNX format — hardware-agnostic (CPU or GPU transparent)
- Handles detection, alignment, and embedding in one call

---

### NumPy

| Operation | Purpose |
|---|---|
| `np.dot(matrix, vector)` | Vectorized batch similarity search |
| `np.linalg.norm(v)` | Compute L2 norm for normalization |
| `np.frombuffer(bytes, float32)` | Zero-copy BLOB deserialization |
| `np.mean(embeddings, axis=0)` | Element-wise average across registration photos |
| `np.argmax(sims)` | Index of best-matching registered user |
| `np.array([...])` | Build (N, 512) embeddings matrix |
| `.tobytes()` | Serialize NumPy array to raw bytes for BLOB storage |
| `.astype(np.float32)` | Ensure correct dtype (defensive programming) |

**Why not Python lists?** NumPy uses C extensions with SIMD instructions.
512-element dot in Python: 512 object lookups + multiplications + additions.
NumPy: single vectorized instruction sequence. Orders of magnitude faster.

---

### SQLite3 (Python stdlib)

Zero installation. File-based. ACID compliant even for local files.

Key patterns:
```python
# Parameterized query (SQL injection safe):
cursor.execute("SELECT ... WHERE name = ?", (name,))

# NEVER use f-strings with user input:
# cursor.execute(f"SELECT ... WHERE name = '{name}'")  <- DANGEROUS

# Commit DML, skip for SELECT:
conn.commit()  # after INSERT / UPDATE / DELETE only
```

---

### ONNX Runtime

Inference engine for InsightFace `.onnx` models. Not called directly — InsightFace manages it.

Auto-selects execution provider:
1. `CUDAExecutionProvider` (NVIDIA GPU)
2. `DirectMLExecutionProvider` (Windows GPU)
3. `CPUExecutionProvider` (always available fallback)

`ctx_id=0` in `_face_app.prepare()` requests GPU 0. Falls back to CPU silently.

---

### Pillow (PIL)

Decodes Streamlit file uploads (raw bytes) into NumPy arrays for OpenCV:
```python
img     = Image.open(io.BytesIO(uploaded_bytes))  # bytes -> PIL Image
bgr_img = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
```
Chain: raw bytes → PIL Image → NumPy RGB → NumPy BGR

---

### UUID

```python
filename = f"{uuid.uuid4().hex}.jpg"
```
`uuid.uuid4()` = cryptographically random 128-bit identifier.
`.hex` = 32-character lowercase hex string.
Guarantees unique filenames. No sequential IDs that expose registration order.

---

### Streamlit (one paragraph only — ignore the rest)

Web framework that reruns entire Python script on every widget interaction.
In this project it is a **thin presentation layer only**. All business logic lives in
`backend_api.py` which contains **zero Streamlit imports**.

---

## SECTION 8 — MUST-KNOW CONCEPTS CHECKLIST

- [ ] **Face Detection** — RetinaFace, bounding boxes, det_score confidence
- [ ] **Face Embeddings** — 512-D float32, ArcFace, angular margin loss training
- [ ] **L2 Normalization** — divide by Euclidean length → unit vector (magnitude = 1.0)
- [ ] **Cosine Similarity** — angle between vectors; dot product = cosine for unit vectors
- [ ] **89% Threshold** — recognition cutoff; false positive vs false negative tradeoff
- [ ] **In-Memory Embedding Cache** — (N,512) matrix cached, invalidated on writes
- [ ] **Vectorized Dot Product** — `np.dot(matrix, vec)` = one BLAS call, not N Python calls
- [ ] **Average Embedding** — N photos → `np.mean` → re-normalize → robust centroid
- [ ] **SQLite Schema** — faces.db (1 row/person), attendance.db (1 row/event)
- [ ] **Parameterized SQL** — `?` placeholders prevent SQL injection
- [ ] **Idempotent Attendance** — check-then-insert; same result on repeated calls
- [ ] **Cache Invalidation** — `_embeddings_cache = None` after every write to faces.db
- [ ] **BGR vs RGB** — OpenCV+InsightFace=BGR, PIL+Streamlit=RGB, `cv2.cvtColor` at boundary
- [ ] **ONNX Runtime** — ctx_id=0 = GPU, silent CPU fallback
- [ ] **Persistent Camera Handle** — open once, reuse per frame, release on stop
- [ ] **UUID Filenames** — random 128-bit IDs, collision-proof, no sequential exposure
- [ ] **Face Alignment** — 5 landmarks → affine transform → canonical 112×112 crop
- [ ] **Minimum 3 Registration Images** — ensures averaged embedding has variance coverage
- [ ] **Detection Score Threshold (0.6)** — reject low-confidence face regions
- [ ] **Largest Face Selection** — max bbox area when multiple faces in registration photo
- [ ] **`np.frombuffer` zero-copy** — interprets BLOB bytes as float32 without copying
- [ ] **Dead Code in `get_all_embeddings`** — lines 122-132 unreachable (refactoring artifact)

---

## SECTION 9 — THINGS YOU CAN SAFELY IGNORE

| File / Code | Why Irrelevant |
|---|---|
| `ui/styles.py` | 900+ lines of CSS. Zero Python logic. |
| `ui/components.py` | HTML f-string template functions. |
| `ui/pages/dashboard.py` | Calls `get_dashboard_stats()` and renders. Thin wrapper. |
| `ui/pages/settings.py` | UI form, no backend writes. |
| `ui/pages/about.py` | Static text only. |
| `ui/pages/attendance_page.py` | Calls `get_attendance_records()` and renders. Thin wrapper. |
| `streamlit_app.py` | SPA router. No business logic. |
| `patch_delete.py` | One-off maintenance script. Not part of runtime. |
| All `st.markdown()` calls | HTML rendering. Not Python logic. |
| All `st.button/st.columns/st.container` | Streamlit layout widgets. |
| `recognition.py` lines 49-155 | Column layout, status badges. |
| `register_user.py` lines 95-246 | File uploader, thumbnail grid, tips panel. |
| `streamlit_app.py` lines 76-91 | CSS sidebar visibility toggle hack. |


---

## SECTION 10 — 100 INTERVIEW QUESTIONS & ANSWERS

### Computer Vision & Face Recognition (Q1–Q25)

**Q1. What is a face embedding and why 512-dimensional?**
A 512-element float32 vector representing a face numerically in high-dimensional space.
Similar faces produce vectors pointing in nearly the same direction.
512 is empirically validated in the ArcFace paper as the accuracy vs. efficiency sweet spot.

**Q2. Two models inside InsightFace buffalo_l?**
RetinaFace (ResNet-50 backbone) for detection (bounding boxes + landmarks).
ArcFace (ResNet-100 backbone) for embedding generation. Both ONNX format.

**Q3. What is ArcFace? How does it differ from standard softmax?**
ArcFace adds an angular margin penalty to the softmax loss.
Standard softmax: trains for class correctness only.
ArcFace: forces different identities to be angularly SEPARATED in embedding space.
Result: more discriminative embeddings. ~99.8% accuracy on LFW benchmark.

**Q4. What is face alignment and why is it critical?**
Detects 5 landmarks, applies affine transform to canonical 112x112 front-facing crop.
Without it: same face at different angles produces different embeddings → broken similarity.

**Q5. Why does app.get(frame) expect BGR not RGB?**
OpenCV historical convention from Windows BITMAPINFOHEADER byte ordering.
InsightFace is built on OpenCV and follows the same convention.

**Q6. What does det_size=(320,320) control?**
Internal resolution for RetinaFace detection pass.
320x320: fast enough for real-time, large enough to catch medium-sized faces.
Smaller = faster but misses distant faces. Larger = better recall but higher latency.

**Q7. What is RetinaFace?**
Multi-task face detector using Feature Pyramid Network (FPN).
Detects faces at multiple scales in one forward pass.
Returns bounding boxes, det_score confidence, and 5-point facial landmarks.

**Q8. Difference between det_score and similarity score?**
det_score (0–1): how confident InsightFace is that a region IS a face.
similarity (0–100): how closely a detected face MATCHES a registered person.

**Q9. Why minimum bounding box area of 4000 px²?**
Below ~63×63 pixels faces lack detail for reliable ArcFace embeddings.
Pores, iris texture, micro-expressions lost at low resolution → noisy embeddings.

**Q10. Why average multiple registration embeddings?**
Single photo = one lighting/angle/expression.
Averaged embedding = centroid in 512-D space, robust to natural variation.
More registration photos = more accurate recognition.

**Q11. Why re-normalize after np.mean?**
Mean of unit vectors is not a unit vector (magnitude < 1).
Re-normalizing with `normalize_embedding()` restores unit norm property.

**Q12. What does score of 88.9% mean at threshold 89%?**
Face labeled "Unknown." False negative: correct person not recognized.

**Q13. False positive vs false negative in this system?**
False positive: wrong person recognized as someone else (incorrect attendance marked).
False negative: correct person not recognized, labeled Unknown (attendance missed).

**Q14. Write cosine similarity formula. Simplify for unit vectors.**
General: `cos(theta) = (a · b) / (|a| × |b|)`
Unit vectors: `cos(theta) = a · b` (because |a| = |b| = 1)

**Q15. Relationship between Euclidean distance and cosine similarity for unit vectors?**
`d_euclidean(a,b) = sqrt(2 - 2*cos(theta))`
They are monotonically related. Minimizing Euclidean distance = maximizing cosine similarity.

**Q16. What if embeddings stored without normalization?**
Scores dominated by vector magnitude not direction.
Same person at different lighting → different magnitudes → inconsistent scores.
Threshold of 89 becomes meaningless.

**Q17. How does ONNX Runtime execute InsightFace models?**
Loads .onnx files and runs inference via best available execution provider:
CUDA GPU → DirectML (Windows) → CPU fallback.
`ctx_id=0` requests GPU 0.

**Q18. What is ONNX and why is it used?**
Open Neural Network Exchange. Open format for ML models.
Allows PyTorch/TensorFlow models to run on any hardware without the original framework.

**Q19. Shape and memory size for 75 registered users?**
Shape: `(75, 512)`. Memory: 75 × 512 × 4 bytes = 153,600 bytes ≈ 150 KB.

**Q20. What does np.argmax(sims) do? Time complexity?**
Returns index of maximum value in array. Time: O(N) linear scan.

**Q21. Full pixel journey from webcam to browser display.**
Webcam hardware → BGR frame → `cap.read()` → NumPy BGR array →
InsightFace annotation (boxes + text drawn in-place) → `cv2.imencode(".jpg")` →
JPEG bytes → `session_state.current_frame_jpeg` → `st.image()` → browser display.

**Q22. How is embedding search different from SQL LIKE text search?**
SQL LIKE does pattern matching in string space (textual).
Embedding search measures geometric proximity in continuous 512-D float space.
Different photos of the same person have no textual similarity but embeddings are angularly close.

**Q23. What for 1 million registered faces instead of np.dot?**
FAISS HNSW or HNSWlib for Approximate Nearest Neighbor (ANN) search.
`np.dot` is O(N×512). FAISS HNSW is O(log N) at small accuracy tradeoff.

**Q24. Which 5 landmarks does InsightFace detect and why?**
Left eye center, right eye center, nose tip, left mouth corner, right mouth corner.
These 5 points define sufficient geometry for a robust affine pose normalization.

**Q25. buffalo_l accuracy on LFW benchmark?**
~99.77% verification accuracy. EER (Equal Error Rate) ≈ 0.3%.

---

### Database & SQL (Q26–Q50)

**Q26. Why two separate SQLite files instead of one?**
faces.db = identity store (slow-changing, small).
attendance.db = transactional log (fast-growing, append-only).
Separation prevents large attendance table affecting identity lookup performance.
Separate files also cannot be JOINed without ATTACH DATABASE — enforces the boundary.

**Q27. What does CREATE TABLE IF NOT EXISTS do?**
Creates table only if it does not already exist. Idempotent: safe on every startup.
Without IF NOT EXISTS: second startup throws "table already exists" error.

**Q28. What is INTEGER PRIMARY KEY AUTOINCREMENT?**
Alias for SQLite internal rowid. AUTOINCREMENT ensures IDs only ever increase.
Without AUTOINCREMENT: SQLite may reuse a deleted row's ID.

**Q29. What is a BLOB and why use it for embeddings?**
Binary Large Object: raw bytes stored without interpretation.
No array-of-floats type in SQL. BLOB preserves exact float32 binary representation.

**Q30. What does np.frombuffer(blob, dtype=np.float32) do exactly?**
Interprets 2048 raw bytes as 512 IEEE 754 single-precision floats.
ZERO-COPY: creates NumPy view over bytes without duplicating data in memory.

**Q31. What is SQL injection and how is it prevented here?**
Attacker inserts SQL commands via user input to manipulate queries.
Prevention: `cursor.execute(sql, (name,))` with `?` placeholders.
SQLite driver escapes all special characters before execution.
NEVER: `cursor.execute(f"SELECT ... WHERE name = '{name}'")`

**Q32. Difference between fetchone() and fetchall()?**
`fetchone()`: first matching row as tuple, or None. Stops after first match.
`fetchall()`: all matching rows as list of tuples. Full scan.
Use `fetchone()` for existence checks to avoid unnecessary full-table traversal.

**Q33. Why commit() after INSERT/DELETE but not SELECT?**
`commit()` persists DML changes to disk. SELECT reads data; nothing to commit.
Without `commit()` after INSERT: transaction rolls back on connection close.

**Q34. What is cursor.rowcount?**
Number of rows affected by the last DML statement.
Used in `delete_user()`: if `rowcount == 0` after DELETE, user was not found.

**Q35. Why no conn.commit() in get_all_embeddings()?**
Only SELECT queries. No modifications. Nothing to persist.

**Q36. Why two separate connections in get_dashboard_stats()?**
faces.db and attendance.db are separate files.
SQLite cannot JOIN across separate files without ATTACH DATABASE.
Two connections is the correct, clean approach.

**Q37. SQL to add UNIQUE constraint preventing duplicate attendance.**
```sql
CREATE UNIQUE INDEX idx_name_date ON attendance(name, date);
-- Then use:
INSERT OR IGNORE INTO attendance (name, date, time) VALUES (?, ?, ?)
```

**Q38. Time complexity of SELECT COUNT(*) WHERE date = ??**
Without index: O(N) full table scan.
With `CREATE INDEX idx_date ON attendance(date)`: O(log N).

**Q39. What does ORDER BY date DESC, time DESC do?**
Compound sort: most recent date first, then most recent time within the same date.
Produces strictly chronological descending order.

**Q40. What does GROUP BY date do in dashboard query?**
Collapses all attendance rows with the same date into one output row.
Allows COUNT(*) to count entries per individual day.

**Q41. What happens when clear_all_attendance() is called?**
`DELETE FROM attendance` (no WHERE = all rows deleted).
Returns `cursor.rowcount` = total deleted.
`_embeddings_cache` is unaffected (that is the face embedding cache, not attendance).

**Q42. Why does get_user_count() call get_all_embeddings() instead of SELECT COUNT(*)?**
Reuses the warm cache: O(1) vs O(disk I/O) for a fresh DB query.
`len(names_list)` == number of registered users.

**Q43. Why LIMIT 14 in the dashboard query?**
Restricts chart to 14 rows (2 weeks). Without LIMIT: months of data returned,
bloating response and confusing the chart.

**Q44. Risk of sqlite3.connect() inside a 30 FPS frame loop?**
Each connect: OS file open, lock acquisition, SQLite state init = ~50ms overhead.
30 FPS × ~50ms = 1,500ms overhead/second. Completely unacceptable.

**Q45. How to add indexes for better attendance performance?**
```sql
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_attendance_name ON attendance(name);
```

**Q46. What does shutil.rmtree(user_dir, ignore_errors=True) do?**
Recursively deletes directory and all contents.
`ignore_errors=True`: no exception if directory does not exist.

**Q47. SQLite and concurrent writes from multiple processes?**
Database-level write lock: only one writer at a time. Multiple readers coexist.
Acceptable for local single-user. Bottleneck for multi-server deployment.

**Q48. How does with sqlite3.connect() context manager work?**
On exit without exception: `conn.commit()` auto-called.
On exit with exception: `conn.rollback()` auto-called.
IMPORTANT: Does NOT call `conn.close()`. File lock held until garbage collection.

**Q49. What does TEXT NOT NULL enforce?**
NOT NULL prevents inserting NULL into that column.
A NULL name or date would be meaningless and break query filtering.

**Q50. Why store date as TEXT 'YYYY-MM-DD' instead of Unix timestamp?**
ISO 8601 strings sort lexicographically = chronologically.
Simple `WHERE date = ?` with no conversion functions.
Human-readable. No timezone confusion risk.

---

### System Design & Architecture (Q51–Q70)

**Q51. Why does backend_api.py have zero Streamlit imports?**
Separation of concerns. Business logic must be testable independently of UI.
Allows replacing Streamlit with FastAPI or CLI without touching backend code.

**Q52. How would you convert this to a REST API?**
Replace `streamlit_app.py` with FastAPI server. Each backend_api function → endpoint.
`recognize_faces_in_frame()` accepts multipart image, returns JSON.
Zero changes to `backend_api.py` needed.

**Q53. Design pattern in get_face_app()?**
Lazy Initialization (Singleton variant via global variable).
Expensive object created once on first demand, cached globally for all future calls.

**Q54. Purpose of _embeddings_cache = None after every write?**
Write-through cache invalidation. When source of truth changes, wipe cache.
Next read rebuilds from fresh DB state. Simpler and always correct.

**Q55. How to scale to 10,000 registered users?**
1. FAISS HNSW ANN index (O(log N) instead of O(N×512) brute-force).
2. PostgreSQL with pgvector extension.
3. CREATE INDEX on attendance table.
4. Async processing queue for ML inference.

**Q56. Main performance bottleneck?**
InsightFace inference: `app.get(frame)` runs two CNNs, blocks the Streamlit thread.
~100-200ms per frame. Cannot be parallelized within one frame.
Solution: move to background thread with frame queue.

**Q57. How to add liveness detection to prevent photo spoofing?**
1. ToF depth sensors (detect flat printed photo surface).
2. Blink detection (Eye Aspect Ratio tracked across frames).
3. Challenge-response (turn head left/right, smile on prompt).
4. Anti-spoofing model trained on real face vs printed photo.

**Q58. Why BLOB not 512 separate float columns?**
512 columns = schema pollution, nightmare ALTER TABLE, meaningless SQL operations.
BLOB is semantically correct: embedding is an opaque binary artifact from SQL's view.

**Q59. Multi-camera support architecture?**
Change `_camera_cap` to `Dict[int, cv2.VideoCapture] = {}`.
Add `camera_id` parameter to `open_camera()`, `capture_single_frame()`, `recognize_faces_in_frame()`.

**Q60. Where is separation of concerns applied?**
`config.py`=constants, `utils.py`=pure math, `backend_api.py`=business logic, `ui/`=presentation.
No module crosses into another's domain. `backend_api.py` has zero Streamlit imports.

**Q61. What does patch_delete.py suggest about the codebase?**
A schema migration was needed at some point (stale column cleanup, data fix).
In production: use Alembic (SQLAlchemy) or Flyway for systematic migrations.

**Q62. How to add an audit log for user deletions?**
New table: `audit_log (id, action TEXT, target TEXT, ts TEXT)`.
In `delete_user()`: INSERT into audit_log after DELETE FROM faces.
Creates immutable record of administrative actions.

**Q63. This system vs cloud face recognition API (AWS Rekognition)?**
This: local-first, free, low latency, no internet, limited to one machine, privacy-preserving.
Cloud: elastic scale, pay-per-call, internet required, data processed externally.

**Q64. Multiple embeddings per user instead of one average?**
New schema: `users (id, name)` + `face_embeddings (id, user_id FK, embedding BLOB)`.
Recognition: max similarity across all embeddings per user. Take the best match.
Supports multiple appearance modes (glasses vs no glasses, beard vs no beard).

**Q65. Privacy implications of storing face embeddings?**
Biometric identifiers — cannot be changed if compromised unlike passwords.
Subject to GDPR Article 9, BIPA (Illinois), CCPA, and similar laws.
Should be encrypted at rest, access-controlled, with explicit retention policies.
This project has NONE of these protections currently.

**Q66. Advantage of storing raw images on disk alongside DB embedding?**
Model upgrade path: regenerate embeddings from stored photos without re-registering users.
Files = durable source of truth. DB embedding = derived, regeneratable artifact.

**Q67. How to unit test recognize_faces_in_frame() without a camera?**
`cv2.imread()` a test image. Mock `get_face_app()` and `get_all_embeddings()`.
Pass NumPy array directly. Assert results match expected names and score ranges.

**Q68. Three production architectural improvements. Justify each.**
1. Vector DB (pgvector/FAISS): `np.dot` O(N×512) → sub-linear ANN at 10K+ users.
2. Async queue (Redis/Kafka): `app.get()` blocks thread → background worker = responsive UI.
3. JWT auth + encryption: anyone with network access currently has full admin rights.

**Q69. _camera_available_cache vs _camera_cap?**
`_camera_cap`: open VideoCapture handle for actual frame reading in recognition loop.
`_camera_available_cache`: cached bool from quick probe, used only for sidebar status indicator.
Avoids real open/release overhead on every UI render.

**Q70. What if faces.db is deleted while the app is running?**
`_embeddings_cache` holds last-known embeddings in RAM. Recognition continues until invalidated.
New INSERTs would create a fresh empty faces.db. Graceful degradation, no immediate crash.

---

### Python & Performance (Q71–Q85)

**Q71. What does the global keyword do in get_face_app()?**
Tells Python to read/write the MODULE-LEVEL `_face_app` variable.
Without `global`: assignment creates a local variable, leaving module-level untouched.

**Q72. Time complexity of np.dot(A, b) where A is (N,512) and b is (512,)?**
O(N × 512) = O(N). All N dot products computed in one BLAS call, not N Python calls.

**Q73. What does Optional[np.ndarray] mean in capture_single_frame()?**
Return type is `np.ndarray` or `None`. `Optional[T]` = `Union[T, None]`.
Documents that camera failure returns `None`, not an array.

**Q74. The shutil import appears mid-file — what does this indicate?**
PEP 8 violation. All imports should be at top of file.
An oversight: `shutil` was added later and not reorganized to the top.
Works correctly but is bad style.

**Q75. What is the dead code in get_all_embeddings() and what caused it?**
Lines 122-132 are unreachable. Function always returns at line 119.
Leftover from an earlier implementation before the cache was added.
Refactoring artifact. Not a bug, but poor code hygiene. Mention in code review.

**Q76. What does np.linalg.norm() compute geometrically?**
Euclidean (L2) length: `sqrt(x1^2 + x2^2 + ... + x512^2)`.
The magnitude/length of the vector in 512-dimensional space.

**Q77. Why face.embedding.astype(np.float32) even if InsightFace returns float32?**
Defensive programming: ensures correct dtype if future InsightFace version changes default.
Also creates a copy, preventing accidental modification of InsightFace's internal buffers.

**Q78. What is io.BytesIO used for?**
Streamlit `file_uploader` returns raw `bytes`.
`io.BytesIO` wraps bytes as a file-like object so `PIL.Image.open()` can read without disk I/O.

**Q79. What does glob.glob() do in get_registration_images()?**
Returns file paths matching a shell-style wildcard.
`glob.glob("data/registrations/Alice/*.jpg")` efficiently lists all .jpg files
without manual `os.listdir()` + extension filtering.

**Q80. Why cv2.imencode to JPEG before st.image()?**
JPEG ~10:1 compression reduces data transfer to browser.
Significantly reduces latency in live recognition loop.

**Q81. np.array(list) vs np.vstack(list) for 1-D arrays?**
Both produce the same (N, d) 2-D matrix. Functionally identical here.
`np.array()` more general. `np.vstack()` semantically clearer for row stacking.

**Q82. What does ctx_id=-1 do vs ctx_id=0?**
`ctx_id=-1`: force CPU-only, skip GPU enumeration entirely.
`ctx_id=0`: request GPU 0, fall back to CPU silently if unavailable.

**Q83. Why does fetchall() return list of tuples not dicts?**
Plain tuples for performance (default SQLite behavior). Values accessed by index: `r[0]`, `r[1]`.
Set `conn.row_factory = sqlite3.Row` for named access at a small performance cost.

**Q84. What happens if conn.close() is not called?**
Connection remains open until Python GC destroys the object.
File lock held — can cause "database is locked" errors under concurrent access.

**Q85. Explain the session timer calculation in recognition.py.**
`datetime.now() - session_start` = timedelta.
`.total_seconds()` = float elapsed seconds.
`// 60` = minutes, `% 60` = remaining seconds.
`:02d` = zero-padded 2-digit format (e.g., `"03:07"`).

---

### Architecture & Design (Q86–Q100)

**Q86. First change if serving 100 concurrent users?**
PostgreSQL for concurrent writes. FAISS for fast similarity search.
FastAPI with Gunicorn workers instead of Streamlit.

**Q87. How to implement API rate limiting?**
Track IP + timestamps in Redis (sliding window counter).
Reject > N recognitions/minute from same IP with HTTP 429 Too Many Requests.

**Q88. Can this system distinguish identical twins?**
Not reliably. Near-identical facial geometry → near-identical embeddings.
Person with marginally higher score gets recognized. Fundamental limitation of appearance-based systems.

**Q89. What is the role of REGISTRATIONS_DIR?**
Durable file system store for raw registration images.
Enables re-generating embeddings on model upgrades without re-registering users.

**Q90. Why re-compute embedding from ALL images on every update?**
Guarantees DB embedding perfectly reflects current file system state.
Incremental updates would drift if images are also deleted in the same operation.

**Q91. How to add real-time SQLite backup?**
Use `source_conn.backup(dest_conn)` from Python's sqlite3 API.
Schedule with APScheduler. Enable WAL mode: `PRAGMA journal_mode=WAL`.
WAL allows non-blocking reads during backup.

**Q92. Recognition in low-light conditions?**
Lower `det_score` threshold below 0.6.
Lower `SIMILARITY_THRESHOLD` below 89.
Preprocess with `cv2.equalizeHist()` or CLAHE (Contrast Limited AHE).
Use IR camera + IR illumination hardware.

**Q93. Explain cache invalidation to a junior developer.**
"Whiteboard (cache) = instant to read. Filing cabinet (DB) = slow.
When someone registers or is deleted, ERASE the whiteboard entirely.
Next reader updates it from the cabinet. Setting `_embeddings_cache = None` IS that erase."

**Q94. Define accuracy, precision, recall for this system.**
Accuracy: % of ALL recognition events (correct + incorrect) that were right.
Precision: Of all people marked Present, % that actually showed up.
Recall: Of all people who showed up, % that got marked.

**Q95. How to add a blacklist feature?**
Add `blacklisted BOOLEAN DEFAULT 0` to faces table.
After best_name found in recognition: query `blacklisted` for that name.
If 1: override `recognized=False`, label="ACCESS DENIED".

**Q96. Recognition without normalization?**
Score dominated by magnitude not direction.
Same person at different lighting → different magnitudes → inconsistent scores.
Threshold becomes arbitrary and meaningless.

**Q97. Multi-factor attendance (face + PIN)?**
Add `pin_hash TEXT` column to faces table.
Only call `mark_attendance()` if face >= threshold AND entered PIN matches stored hash.
Reduces false positives to near zero.

**Q98. Advantage of raw images on disk alongside DB embedding?**
Model upgrade path: regenerate all embeddings from stored photos without re-registration.
Images = durable ground truth. DB embedding = derived, regeneratable artifact.

**Q99. How to mock get_all_embeddings() in unit tests?**
```python
import unittest.mock as mock
test_names  = ["Alice", "Bob"]
test_matrix = np.array([normalize_embedding(np.random.randn(512).astype(np.float32)),
                        normalize_embedding(np.random.randn(512).astype(np.float32))])
with mock.patch("backend_api.get_all_embeddings", return_value=(test_names, test_matrix)):
    frame, results = recognize_faces_in_frame(test_image)
    assert results[0]["name"] in ["Alice", "Bob", "Unknown"]
```

**Q100. Three production architectural improvements. Justify each.**

1. **VECTOR DATABASE** (pgvector / FAISS / Milvus):
   Current `np.dot` is O(N×512). At 10K+ users, brute-force becomes a bottleneck.
   ANN indexes provide sub-linear search — O(log N) — at a small accuracy tradeoff.

2. **ASYNC PROCESSING QUEUE** (Redis + background worker):
   Current: Streamlit thread blocks on `app.get(frame)` for ~150ms.
   With queue: frame dropped into Redis, worker runs inference, result returned async.
   UI stays responsive. Throughput scales with number of worker processes.

3. **AUTHENTICATION + ENCRYPTION**:
   Current: Anyone with network access can register, delete users, or clear attendance.
   Production: JWT auth, bcrypt-hashed admin passwords, SQLite encrypted with SQLCipher,
   HTTPS enforced, rate limiting, and all biometric data encrypted at rest.


---

## SECTION 11 — STUDY ROADMAP

### Phase 1 — Core Math & Configuration (2 hours)

| File | Focus | Time |
|---|---|---|
| `config.py` | Every constant and why each value was chosen | 15 min |
| `utils.py` | L2 normalization math, cosine similarity derivation, why dot = cosine for unit vectors | 45 min |

**Practice:** Close all files. Write `normalize_embedding()` and `cosine_similarity()` from memory.
Explain aloud why the dot product equals cosine similarity for unit vectors.

---

### Phase 2 — Database Layer (2 hours)

| Lines | Focus | Time |
|---|---|---|
| backend_api lines 38–54 | `_init_databases()`, CREATE TABLE IF NOT EXISTS, BLOB type | 20 min |
| backend_api lines 81–181 | All CRUD functions, `np.frombuffer`, parameterized queries, idempotency | 60 min |
| backend_api lines 184–309 | `mark_attendance()`, `get_attendance_records()`, `get_dashboard_stats()`, GROUP BY, LIMIT | 40 min |

**Practice:** Draw both database schemas on paper with column types.
Write all 11+ SQL queries from memory without looking.

---

### Phase 3 — Face Recognition Core (3 hours)

| Lines | Focus | Time |
|---|---|---|
| backend_api lines 57–74 | Lazy loading pattern, InsightFace init, det_size, ctx_id | 30 min |
| backend_api lines 97–121 | Cache mechanism, `np.frombuffer`, matrix construction | 45 min |
| backend_api lines 316–384 | `recognize_faces_in_frame()` — full pipeline, line by line | 60 min |
| backend_api lines 445–534 | `validate_face_image()`, `update_user_faces()` — registration pipeline | 45 min |

**Practice:** Trace `recognize_faces_in_frame()` for a single detected face.
Write down every variable and its shape at each step.
Draw the embedding matrix dot product visually.

---

### Phase 4 — Camera & System Design (1 hour)

| Lines | Focus | Time |
|---|---|---|
| backend_api lines 389–436 | Camera lifecycle, persistent handle, `cap.release()` | 30 min |
| Entire project | Layer diagram, data flow, cache invalidation, remaining bottlenecks | 30 min |

---

### Phase 5 — Interview Simulation (2 hours)

Answer all 100 questions aloud without reading this document.
Mark any question you cannot answer confidently with a star (*).
Return to the relevant section for every starred question.

Focus areas:
- Q1–Q25: Computer Vision & Face Recognition
- Q26–Q50: Database & SQL
- Q71–Q85: Python & Performance
- Q86–Q100: Architecture & System Design

---

### File Priority Rankings

| Rank | File | Priority | Reason |
|---|---|---|---|
| 1 | `backend_api.py` | **ESSENTIAL** | All business logic lives here |
| 2 | `utils.py` | **ESSENTIAL** | The recognition math |
| 3 | `config.py` | **ESSENTIAL** | Every constant needs justification |
| 4 | `ui/pages/recognition.py` | Good to know | Frame loop orchestration |
| 5 | `ui/pages/register_user.py` | Good to know | Registration flow calls |
| 6 | `ui/pages/dashboard.py` | Low priority | Calls `get_dashboard_stats()` |
| 7 | `streamlit_app.py` | Concept only | SPA routing pattern |
| 8 | `ui/styles.py` | **SKIP** | Pure CSS |
| 9 | `ui/components.py` | **SKIP** | HTML templates |
| 10 | `ui/pages/settings.py` | **SKIP** | UI form only |
| 11 | `ui/pages/about.py` | **SKIP** | Static text |
| 12 | `patch_delete.py` | **SKIP** | One-off developer script |

---

**Total recommended study time: ~10 hours**

> **The three files that contain everything your interviewer cares about:**
> `backend_api.py` · `utils.py` · `config.py`
>
> Master these three files and you can confidently answer every question in this guide.
