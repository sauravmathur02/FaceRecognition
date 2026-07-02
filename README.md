# Face Recognition Attendance System

A real-time attendance marking system built with Python, OpenCV, Streamlit, and InsightFace. Detects faces via webcam, matches them against registered users using highly optimized vectorized cosine similarity on face embeddings, and automatically records attendance in a local SQLite database — once per person per day.

---

## Tech Stack

| Component | Technology |
|---|---|
| Frontend Web UI | [Streamlit](https://streamlit.io/) |
| Face Detection & Recognition | [InsightFace](https://github.com/deepinsight/insightface) (`buffalo_l` model) |
| Inference Runtime | ONNX Runtime (CPU Optimized) |
| Image Processing | OpenCV |
| Embedding Math | NumPy (Vectorized similarity search) |
| Database | SQLite (`faces.db`, `attendance.db`) |
| Language | Python 3.9+ |

---

## Features

- **Beautiful Streamlit Dashboard** for viewing attendance metrics and managing users.
- **Live face recognition** from webcam in the browser.
- **Robust User Management** — register, update, and manage face registration images directly from the UI.
- **Cosine similarity** matching with a configurable threshold (default: 89%).
- **Average embedding** per person — computed from multiple images for better accuracy.
- **CPU Optimized** — runs efficiently with dynamically resized detection boundaries and vectorized similarity search.
- **Attendance marking** — once per calendar day, stored in SQLite.

---

## Project Structure

```text
FaceRecognition/
├── streamlit_app.py        # Main Streamlit web application entry point
├── config.py               # All constants: paths, thresholds, model name
├── utils.py                # Shared helpers: normalize_embedding, cosine_similarity
├── backend_api.py          # Core logic: InsightFace inference, database access, image management
│
├── ui/                     # Streamlit frontend pages and components
│   ├── components/         # Reusable UI widgets (KPIs, tables)
│   └── pages/              # Pages: Dashboard, Recognition, Register User, Attendance, etc.
│
├── data/
│   └── registrations/      # Permanent storage for per-person registration images
│
├── faces.db                # SQLite DB — registered user embeddings
├── attendance.db           # SQLite DB — daily attendance records
├── requirements.txt        # Core backend dependencies
└── requirements_ui.txt     # Streamlit frontend dependencies
```

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd FaceRecognition
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

Install both core backend dependencies and Streamlit UI dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements_ui.txt
```

### 4. Initialise databases

The application automatically creates `faces.db` and `attendance.db` on startup if they don't exist.

---

## Usage

Launch the Streamlit web application:

```bash
streamlit run streamlit_app.py
```

This will automatically open the dashboard in your web browser. 

### Registering / Updating a user
1. Navigate to the **Registered Users** page.
2. Enter a new user's name or select an existing user to update.
3. You can capture live images using your webcam or upload existing photos.
4. The system requires at least 3 valid face images.

### Running live recognition
1. Navigate to the **Live Recognition** page.
2. Grant camera permissions in your browser.
3. The system will process the video feed:
   - 🟢 **Green box** — recognized user (similarity ≥ 89%)
   - 🔴 **Red box** — unknown person (similarity < 89%)
4. Attendance is marked automatically and only **once per day**.

---

## Configuration

All tunable values are in [`config.py`](config.py). Change them here and every module picks up the update automatically.

| Constant | Default | Description |
|---|---|---|
| `DB_NAME` | `"faces.db"` | Path to the face embeddings database |
| `ATTENDANCE_DB` | `"attendance.db"` | Path to the attendance database |
| `SIMILARITY_THRESHOLD` | `89` | Minimum cosine similarity (%) to recognize a face |
| `MODEL_NAME` | `"buffalo_l"` | InsightFace model to use |
| `REGISTRATIONS_DIR` | `"data/registrations"` | Root folder for permanent registration images |
| `LOG_LEVEL` | `"INFO"` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## Database Schema

### `faces.db`

```sql
CREATE TABLE faces (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL,
    embedding BLOB    NOT NULL   -- float32 bytes, L2-normalized average embedding
);
```

### `attendance.db`

```sql
CREATE TABLE attendance (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT    NOT NULL,
    date TEXT    NOT NULL,   -- format: YYYY-MM-DD
    time TEXT    NOT NULL    -- format: HH:MM:SS
);
```

---

## How Face Matching Works

1. **Registration:** For each image, InsightFace extracts a 512-dimensional embedding. Each embedding is L2-normalized, then all embeddings for a person are averaged and normalized again. This single average vector is stored in `faces.db`.
2. **Recognition:** For each detected face in the webcam frame, the embedding is extracted and normalized. The similarities against all registered users are computed instantaneously using a vectorized NumPy dot product matrix multiplication.
3. **Threshold:** If the best similarity is ≥ **89%**, the person is recognized. Below that, they are labeled "Unknown".
4. **Attendance:** On a match, the system checks if an attendance record already exists for that person today. If not, it inserts one.

---

## License

MIT
