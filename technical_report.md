# Face Recognition Attendance System
## Technical Report

### 1. Executive Summary
This is a localized, AI-powered Face Recognition Attendance System. It leverages state-of-the-art deep learning models for face detection and embedding extraction, cross-referencing live webcam feeds against a local SQLite database to mark attendance in real-time. The application is built with a Single Page Application (SPA) feel using Streamlit for the frontend UI.

### 2. System Architecture
The system architecture follows a decoupled frontend-backend pattern, even though it runs in a single runtime environment.
- **Frontend (Streamlit):** Handles UI rendering, user interactions, routing, and camera feed display. It manages session states to prevent hardware lockups and provides a dynamic dashboard.
- **Backend Adapter (`backend_api.py`):** Acts as a thin middleware layer between the UI and the core logic/database. It executes SQLite queries, loads the AI model, processes image frames, and returns unified results to the frontend.
- **Core ML Logic:** Built around the InsightFace library (specifically the `buffalo_l` model), which performs Face Detection, Alignment, and Embedding Generation.
- **Storage:** Two local SQLite databases (`faces.db` for embeddings, `attendance.db` for logging).

### 3. Technology Stack
- **Language:** Python 3.x
- **Frontend Framework:** Streamlit
- **Computer Vision & ML:** OpenCV (`cv2`), InsightFace, NumPy
- **Database:** SQLite3
- **File System:** Standard Python `os`, `glob`, `shutil`

### 4. File Structure & Components
* **`streamlit_app.py`**: The main entry point. Sets up the Streamlit page configuration, injects custom CSS, and handles the SPA routing loop based on `st.session_state`.
* **`backend_api.py`**: The core API layer. Contains functions for database initialization, caching embeddings into memory, opening/releasing the webcam, managing user registrations (with image validation), and running the similarity search on incoming video frames.
* **`config.py`**: Centralized configuration file holding constants like database paths (`faces.db`, `attendance.db`), model name (`buffalo_l`), webcam ID, and the `SIMILARITY_THRESHOLD` (set to 89%).
* **`utils.py`**: Contains pure, shared utility functions such as L2 normalization of embeddings (`normalize_embedding`) and vectorized dot-product calculation for similarity (`cosine_similarity`).
* **`ui/` (Directory)**: Contains the modularized UI pages (Dashboard, Recognition, Register, Attendance, etc.) and custom CSS stylesheets (`ui.styles.CSS`).

### 5. Database Schema
The application uses two separate SQLite databases to separate identity management from transactional logs.

**Database 1: `faces.db`**
* Table: `faces`
  * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
  * `name` (TEXT, NOT NULL)
  * `embedding` (BLOB, NOT NULL) - Stores the L2-normalized 512-dimensional float32 vector.

**Database 2: `attendance.db`**
* Table: `attendance`
  * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
  * `name` (TEXT, NOT NULL)
  * `date` (TEXT, NOT NULL) - Format: YYYY-MM-DD
  * `time` (TEXT, NOT NULL) - Format: HH:MM:SS

### 6. Face Recognition Pipeline
1. **Frame Capture:** OpenCV reads a BGR frame from the webcam.
2. **Detection:** InsightFace (`app.get(frame)`) scans the frame for faces, calculating bounding boxes and confidence scores.
3. **Embedding:** For detected faces, InsightFace generates a raw embedding vector.
4. **Normalization:** The raw vector is passed through `utils.normalize_embedding` (divided by its L2 norm) to create a unit vector.
5. **Matching:** The system performs a vectorized dot product (`np.dot`) between the live normalized vector and the cached matrix of all registered user vectors.
6. **Thresholding:** The maximum dot-product score is compared against `SIMILARITY_THRESHOLD` (89%). If it exceeds the threshold, the face is recognized.
7. **Logging:** `backend_api.mark_attendance` records the event if the person hasn't been logged yet on the current calendar date.

### 7. Performance & Optimization
* **In-Memory Caching:** Instead of querying `faces.db` and parsing BLOBs for every frame, `backend_api.get_all_embeddings()` caches the names list and a NumPy matrix of embeddings in memory (`_embeddings_cache`). This makes the dot-product similarity search extremely fast (O(1) database hits per frame).
* **Vectorized Math:** `np.dot(embs_matrix, query_emb)` computes the similarity score for all registered users simultaneously, leveraging highly optimized C code under the hood.
* **L2 Normalization Pre-computation:** Because vectors are normalized before saving to the database, computing Cosine Similarity at runtime only requires a dot product, saving CPU cycles.

### 8. Security & Known Limitations
* **UI Security:** The application relies on `unsafe_allow_html=True` in Streamlit. While currently safe, it is theoretically vulnerable to XSS if user inputs are improperly sanitized before rendering.
* **Authentication:** The Admin dashboard is accessible to anyone on the network with access to the Streamlit port. There is no password/login layer.
* **Anti-Spoofing:** The current model evaluates 2D facial features. It lacks liveness detection and could potentially be fooled by a high-resolution photograph or video presented to the camera.

### 9. Future Improvements
* **Liveness Detection:** Integrate a blink-detection or depth-mapping model to prevent photo spoofing.
* **Authentication Layer:** Implement an admin login screen before showing the dashboard and navigation sidebar.
* **Database Migrations:** Transition to SQLAlchemy or a similar ORM to handle database schema upgrades seamlessly as the application scales.
* **Asynchronous Processing:** Move the camera reading and face recognition into a separate background thread/process to prevent UI frame-rate drops when rendering Streamlit components.
