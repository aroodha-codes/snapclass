# 📸 SnapClass

## AI-Powered Face Recognition Attendance System

SnapClass is an AI-powered smart attendance application that uses **face recognition** to identify registered students and assist teachers with classroom attendance.

The system detects faces, generates numerical face embeddings, matches them against enrolled users, rejects unknown faces using a similarity threshold, and allows attendance results to be reviewed before they are saved.

SnapClass also includes teacher and student portals, subject management, QR-based enrollment, attendance history, and optional voice-recognition functionality.

---

## ✨ Features

### 👨‍🏫 Teacher Portal

- Secure teacher registration and login
- Create and manage subjects
- Generate subject enrollment codes
- Generate QR codes for student enrollment
- Upload classroom images
- Detect multiple faces in classroom images
- Identify registered students
- Reject unknown faces
- Review recognition results before marking attendance
- Save attendance records
- View attendance history
- View class statistics
- Optional voice-based attendance

### 🎓 Student Portal

- Student registration
- Face enrollment
- Face-based identification
- Optional voice enrollment
- Join subjects using subject codes
- Join subjects through shared links
- View enrolled subjects
- View attendance statistics
- Unenroll from subjects

---

# 🧠 Face Recognition Pipeline

The face-recognition system follows the pipeline:

```text
Input Image
     ↓
Face Detection
     ↓
Facial Landmark Detection
     ↓
Face Embedding Generation
     ↓
128-Dimensional Embedding
     ↓
Compare with Enrolled Embeddings
     ↓
Identity Prediction
     ↓
Distance Verification
     ↓
Threshold Check
     ↓
Known Person / Unknown Person
```

The system does not automatically accept the closest registered identity.

After predicting a possible identity, SnapClass compares the detected face embedding with the stored embedding using **Euclidean distance**.

If the distance exceeds the configured threshold, the person is treated as **Unknown**.

---

# 🔍 Face Detection

SnapClass uses **dlib's frontal face detector** to locate faces inside input images.

Detected faces are processed individually before recognition.

The system can therefore process classroom photographs containing multiple students.

---

# 🧬 Face Embeddings

Each detected face is transformed into a numerical representation called a **face embedding**.

SnapClass uses a dlib-based face recognition model to generate a:

```text
128-dimensional face embedding
```

Instead of comparing raw images, the application compares these feature vectors.

Conceptually:

```text
Face Image
    ↓
Face Recognition Model
    ↓
[0.12, -0.43, 0.87, ..., 0.21]
    ↓
128-D Face Embedding
```

These embeddings represent important facial characteristics and allow different images of the same person to be compared mathematically.

---

# 🎯 Face Matching

SnapClass currently combines identity prediction with distance-based verification.

The matching process is approximately:

```text
Query Face
    ↓
Generate Embedding
    ↓
Predict Candidate Identity
    ↓
Retrieve Candidate's Stored Embedding
    ↓
Calculate Euclidean Distance
    ↓
Apply Recognition Threshold
```

Euclidean distance between two embeddings can be represented as:

```text
d(A, B) = √Σ(Aᵢ - Bᵢ)²
```

A smaller distance indicates that two facial embeddings are more similar.

---

# 🚫 Unknown Face Rejection

A face-recognition application should not assign every detected face to the nearest registered person.

SnapClass therefore includes an **unknown-person rejection mechanism**.

Current configuration:

```text
Euclidean distance <= 0.60
        ↓
Recognized Person

Euclidean distance > 0.60
        ↓
Unknown Person
```

The threshold is configurable and can be calibrated using validation data.

---

# 🤖 Classification

SnapClass uses **scikit-learn's Support Vector Classifier (SVC)** as part of the recognition process.

The classifier predicts a candidate identity from enrolled face embeddings.

The prediction is then verified using the embedding distance threshold.

This provides an additional rejection layer instead of blindly accepting every classifier prediction.

---

# 🎙️ Voice Recognition

SnapClass also includes optional voice-recognition functionality.

Voice recognition uses **Resemblyzer** to generate speaker embeddings.

Pipeline:

```text
Audio Recording
      ↓
Audio Preprocessing
      ↓
Speaker Embedding
      ↓
Compare with Registered Voice Embeddings
      ↓
Similarity Score
      ↓
Threshold Check
      ↓
Recognized / Unknown
```

Current voice similarity threshold:

```text
Similarity >= 0.65 → Recognized
Similarity < 0.65  → Unknown
```

Voice recognition is an additional feature and is independent of the core face-recognition attendance workflow.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      SnapClass      │
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
       Teacher Portal                    Student Portal
              │                                 │
       Create Subjects                     Registration
       Upload Images                       Face Enrollment
       Run Attendance                      Join Subjects
              │                                 │
              └────────────────┬────────────────┘
                               │
                       Recognition Engine
                               │
                  ┌────────────┴────────────┐
                  │                         │
             Face Pipeline             Voice Pipeline
                  │                         │
            Face Detection            Audio Processing
                  │                         │
           Face Embeddings            Voice Embeddings
                  │                         │
           Identity Matching          Similarity Matching
                  │                         │
                  └────────────┬────────────┘
                               │
                          Supabase
                               │
                 Attendance & User Records
```

---

# 🛠️ Technology Stack

| Component            | Technology                  |
| -------------------- | --------------------------- |
| Programming Language | Python                      |
| Web Interface        | Streamlit                   |
| Face Detection       | dlib                        |
| Face Embeddings      | dlib Face Recognition Model |
| Classification       | scikit-learn SVC            |
| Face Matching        | Euclidean Distance          |
| Voice Embeddings     | Resemblyzer                 |
| Audio Processing     | Librosa                     |
| Database             | Supabase                    |
| Authentication       | bcrypt                      |
| Numerical Processing | NumPy                       |
| Data Processing      | Pandas                      |
| QR Code Generation   | Segno                       |

---

# 📁 Project Structure

```text
snapclass/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── .streamlit/
│   ├── secrets.toml
│   └── secrets.example.toml
│
└── src/
    │
    ├── components/
    │   ├── dialog_add_photo.py
    │   ├── dialog_attendance_results.py
    │   ├── dialog_auto_enroll.py
    │   ├── dialog_create_subject.py
    │   ├── dialog_enroll.py
    │   ├── dialog_share_subject.py
    │   ├── dialog_voice_attendance.py
    │   ├── footer.py
    │   ├── header.py
    │   └── subject_card.py
    │
    ├── database/
    │   ├── config.py
    │   └── db.py
    │
    ├── pipelines/
    │   ├── face_pipeline.py
    │   └── voice_pipeline.py
    │
    ├── screens/
    │   ├── home_screen.py
    │   ├── student_screen.py
    │   └── teacher_screen.py
    │
    └── ui/
        └── base_layout.py
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd snapclass
```

---

## 2. Create a Virtual Environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Supabase Configuration

SnapClass uses Supabase for storing application data.

Create:

```text
.streamlit/secrets.toml
```

Add your credentials:

```toml
SUPABASE_URL = "your-supabase-project-url"
SUPABASE_KEY = "your-supabase-key"
```

## Important

Never upload:

```text
.streamlit/secrets.toml
```

to GitHub.

The `.gitignore` file should contain:

```gitignore
.streamlit/secrets.toml
.env
.env.*
.venv/
venv/
__pycache__/
*.pyc
```

A public example file can instead be provided as:

```text
.streamlit/secrets.example.toml
```

with:

```toml
SUPABASE_URL = "your-supabase-project-url"
SUPABASE_KEY = "your-supabase-key"
```

---

# ▶️ Running SnapClass

After configuring the environment:

```bash
streamlit run app.py
```

Streamlit will provide a local URL such as:

```text
http://localhost:8501
```

Open the URL in a browser to use SnapClass.

---

# 🗄️ Database

SnapClass currently uses Supabase tables including:

```text
teachers
students
subjects
subject_students
attendance_logs
```

The database stores information required for:

- Teacher accounts
- Student accounts
- Subjects
- Student enrollment
- Face embeddings
- Voice embeddings
- Attendance records

---

# 🧪 Evaluation

Face-recognition systems should be evaluated using both registered and unregistered users.

The planned evaluation includes:

### Known-person testing

Images belonging to registered users are presented to the system.

The system records whether the correct identity was returned.

### Unknown-person testing

Images belonging to users who were never enrolled are presented.

The system records whether they were correctly rejected as:

```text
Unknown
```

### Metrics

The evaluation will measure:

- Correct identification
- Incorrect identification
- Correct unknown rejection
- False acceptance
- False rejection
- Recognition accuracy
- False Acceptance Rate
- False Rejection Rate

Actual measured evaluation results will be added after running the final validation dataset.

---

# 📊 Threshold Evaluation

The current face-recognition threshold is:

```text
0.60
```

Before production use, the threshold should be tested across several possible values.

For example:

```text
0.40
0.45
0.50
0.55
0.60
```

Each threshold can then be evaluated for:

```text
Correct Recognition
False Acceptance
False Rejection
Unknown Rejection
```

This allows the final threshold to be selected based on measured performance rather than an arbitrary value.

---

# ⚠️ Failure Cases

Face recognition may become less reliable under difficult conditions.

Potential failure cases include:

- Poor lighting
- Strong shadows
- Blurred images
- Low-resolution faces
- Extreme head angles
- Partial face occlusion
- Masks
- Sunglasses
- Large changes in appearance
- Faces located far from the camera
- Multiple visually similar individuals

The unknown-rejection mechanism reduces incorrect acceptance but cannot eliminate all recognition errors.

---

# 🔒 Privacy and Security

Face and voice embeddings are biometric information and should be handled responsibly.

Recommended practices include:

- Obtain permission before enrolling biometric information.
- Never upload real student biometric data to a public repository.
- Keep Supabase credentials private.
- Use appropriate database access policies.
- Store only information required by the application.
- Provide a way to remove enrolled biometric profiles.
- Protect stored embeddings from unauthorized access.
- Do not rely entirely on automated recognition for high-impact decisions.

---

# 🚧 Current Limitations

The current version has several areas that can be improved:

- The face threshold is currently fixed.
- Formal threshold calibration has not yet been completed.
- A dedicated benchmark dataset has not yet been evaluated.
- Enrollment can be strengthened using multiple face samples.
- Recognition performance may decrease in poor lighting.
- Pose variation can affect embedding quality.
- Voice recognition can be affected by environmental noise.
- Production-grade biometric security controls are still required.

---

# 🚀 Planned Improvements

- [ ] Multi-image face enrollment
- [ ] Multiple embeddings per person
- [ ] Explicit nearest-neighbor matching
- [ ] Threshold calibration using validation data
- [ ] Unknown-person test dataset
- [ ] False Acceptance Rate calculation
- [ ] False Rejection Rate calculation
- [ ] Recognition accuracy evaluation
- [ ] Confusion matrix
- [ ] Evaluation dashboard
- [ ] Display recognition distance in the interface
- [ ] Duplicate-person enrollment detection
- [ ] Better low-light image handling
- [ ] Better blurred-image handling
- [ ] Automated tests for face embeddings
- [ ] Automated tests for matching
- [ ] Stronger biometric-data protection
- [ ] Improved exception handling
- [ ] Docker-based reproducible deployment

---

# 🎯 Project Objective

The objective of SnapClass is to explore how AI-based identity recognition can reduce the manual effort involved in classroom attendance.

The project demonstrates practical concepts including:

- Computer vision
- Face detection
- Face embeddings
- Machine-learning classification
- Similarity-based matching
- Unknown-person rejection
- Speaker embeddings
- Database integration
- Streamlit application development
- Biometric privacy considerations

Attendance is treated as an application built on top of the underlying face-identification system.

---

# 👨‍💻 Author

**Siddharoodha**

AI/ML and software development learner focused on building practical computer-vision and intelligent application projects.

---

# ⭐ SnapClass

**AI-Powered Smart Attendance through Face Recognition**

If you find the project useful, feel free to star the repository and share suggestions or improvements.
