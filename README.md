# SnapClass

Face recognition identification and classroom attendance management built with Python, Streamlit, dlib, and Supabase.

SnapClass registers individuals, generates face embeddings, and identifies new faces by comparing them with registered profiles. Faces that do not meet the matching threshold are returned as **Unknown**.

[Open the application](https://snapclass-9.streamlit.app)

## Features

### Face recognition
- Camera-based student registration.
- Face detection and 128-dimensional embedding extraction.
- Nearest-match identification using Euclidean distance.
- Threshold-based rejection of unknown faces.
- Uploaded-photo identification with names and match distances.
- Multiple-face identification within a single image.

### Attendance management
- Teacher registration and password login.
- Subject creation and confirmed subject deletion.
- Enrollment through subject codes and shared links.
- Enrolled-student lists for each subject.
- Face-based classroom attendance with review before saving.
- Attendance history with present and absent student names.
- Optional voice registration and voice attendance.

Voice attendance is an additional feature and is not included in the face-recognition evaluation below.

## How face identification works

1. Convert the input image to RGB.
2. Detect faces using dlib's frontal-face detector.
3. Locate facial landmarks using the pretrained landmark predictor.
4. Generate a 128-dimensional descriptor using
   `dlib_face_recognition_resnet_model_v1`.
5. Calculate Euclidean distance between each query descriptor and all
   registered face descriptors.
6. Select the registered descriptor with the smallest distance.
7. Accept its identity when the distance is at or below the threshold.
   Otherwise, return **Unknown**.

For a query embedding q and registered embedding e:

    distance(q, e) = sqrt(sum((q[i] - e[i])²))

Lower distance indicates a closer match. Distance is not a confidence
percentage.

The current implementation stores one face embedding per registered
student. It uses pretrained models; it does not train an identity
classifier or fine-tune the embedding model.

Face identification searches all registered student profiles. Subject
enrollment determines attendance membership, not whether a face is
known to the recognition system.

## Matching threshold

The current threshold is **0.6**:

    nearest distance <= 0.6 → accept the nearest identity
    nearest distance > 0.6  → Unknown

This was retained as an initial baseline consistent with dlib's
face-recognition example. It was fixed throughout the reported tests
and was not optimized on this small evaluation set.

Reducing the threshold generally makes acceptance stricter; increasing
it makes acceptance more permissive. A larger, separate validation set
is needed to choose a threshold appropriate for a particular deployment.

Reference:
[dlib face-recognition example](https://github.com/davisking/dlib/blob/master/python_examples/face_recognition.py)

## Technology

| Component | Technology |
|---|---|
| Application | Python and Streamlit |
| Face detection and embeddings | dlib and face_recognition_models |
| Distance calculations | NumPy |
| Result tables | pandas |
| Database | Supabase |
| Teacher password hashing | bcrypt |
| Image handling | Pillow |
| Enrollment QR codes | Segno |
| Optional voice recognition | Resemblyzer and librosa |

## Local setup

### 1. Prepare the environment

Use Python 3.12. The project includes Python syntax that requires
Python 3.12 or later.

From the project root on Windows:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Git must be installed because one dependency is installed from GitHub.

### 2. Configure Supabase

Create `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "YOUR_SUPABASE_PROJECT_URL"
SUPABASE_KEY = "YOUR_SUPABASE_PROJECT_KEY"
```

Use your own project configuration. Never commit real secrets.

The application expects these existing tables and relationships:

| Table | Purpose |
|---|---|
| teachers | Teacher accounts and password hashes |
| students | Names, face embeddings, and optional voice embeddings |
| subjects | Subjects owned by teachers |
| subject_students | Student-to-subject enrollments |
| attendance_logs | Student attendance by subject and timestamp |

Required relationships connect subjects to teachers, enrollments to
students and subjects, and attendance logs to students and subjects.

Subject deletion requires cascading foreign keys from
`subject_students.subject_id` and `attendance_logs.subject_id` to
`subjects.subject_id`.

The current project uses a manually configured Supabase database.
Creating the secrets file does not create its tables. A fresh
installation requires equivalent table definitions, relationships,
and appropriate access policies.

### 3. Start the app

```powershell
python -m streamlit run app.py
```

## Usage

### Register a student
1. Open Student Portal.
2. Capture a clear image containing one face.
3. If the face is not recognized, enter the student's name.
4. Optionally record a voice sample.
5. Create the profile.

### Identify a face
1. Open face identification from the home page.
2. Upload a new photograph.
3. Click Identify Faces.
4. Review the predicted name or Unknown result and nearest distance.

Identification does not create attendance records.

### Record attendance
1. Log in to Teacher Portal.
2. Create a subject and share its enrollment code.
3. Have students join the subject.
4. Select the subject and add classroom photos.
5. Run face analysis.
6. Review the results and confirm to save.
7. Open Attendance Records to view session details.

## Evaluation

A preliminary manual evaluation was conducted through the application's
face-identification interface.

- Five query images contained seven evaluated faces.
- Three faces belonged to registered individuals.
- Four faces belonged to unregistered individuals.
- Query photos differed from the registration photos.
- The matching threshold remained fixed at 0.6.
- The group photo, T02, produced three separately recorded face results.

Expected identities and registration status were supplied by the tester.
Predictions and distances were transcribed from application screenshots.

### Results

| Test ID | Expected | Predicted | Distance | Outcome |
|---|---|---|---:|---|
| [T01](docs/evaluation/screenshots/T01.png) | Prajwal | Prajwal | 0.4587 | Correct identification |
| [T02-F1](docs/evaluation/screenshots/T02.png) | Siddharoodha | Siddharoodha | 0.4461 | Correct identification |
| [T02-F2](docs/evaluation/screenshots/T02.png) | Unknown | Unknown | 0.6072 | Correct rejection |
| [T02-F3](docs/evaluation/screenshots/T02.png) | Unknown | Unknown | 0.6486 | Correct rejection |
| [T03](docs/evaluation/screenshots/T03.png) | Karthik N | Karthik N | 0.3919 | Correct identification |
| [T04](docs/evaluation/screenshots/T04.png) | Unknown | Unknown | 0.6329 | Correct rejection |
| [T05](docs/evaluation/screenshots/T05.png) | Unknown | Unknown | 0.6180 | Correct rejection |
| [T06](docs/evaluation/screenshots/T06.png) | No face | No face detected | N/A | Correct no-face handling |

### Summary

| Metric | Observed result |
|---|---:|
| Known-face identification rate | 3/3 — 100% |
| Unknown-face rejection rate | 4/4 — 100% |
| Wrong identifications | 0 |
| False rejections | 0 |
| False acceptances | 0 |

Six query images were tested: five contained seven evaluated faces, and one contained no face. The no-face image was correctly handled without producing an identity.

[View results as CSV](docs/evaluation/results.csv) ·
[Download the spreadsheet](docs/evaluation/SnapClass_Evaluation.xlsx)


## Failure cases and limitations

No incorrect identity predictions were observed in the submitted batch.
The following remain expected risks rather than measured failures:

- Poor lighting, blur, occlusion, and large head rotations can prevent
  detection or reduce matching reliability.
- A single enrollment photo may not capture enough appearance variation.
- Similar-looking people may be confused.
- No liveness detection is implemented. Face login is not suitable as
  production-grade authentication.
- An unknown distance of 0.6072 is close to the 0.6 boundary, so this
  small sample does not establish robust separation.
- Teacher login uses application-managed credentials; database
  authorization and access policies require a separate security review.
- The evaluation does not measure voice recognition, latency, large
  galleries, or performance across a representative population.

## Improvements

- Collect a larger and more varied evaluation dataset.
- Select the threshold using a separate validation set.
- Support multiple enrollment samples per person.
- Add enrollment image-quality checks.
- Add liveness checks and stronger authentication.
- Export reproducible database setup and pin verified dependency versions.
- Automate recognition evaluation and regression checks.

## Cost and data handling

Face recognition runs in the application process without a paid
inference API. Hosting and database usage depend on the services
configured by the operator.

Enrollment stores face embeddings in Supabase. Embeddings are sensitive
biometric data and should be protected with appropriate access controls.

Use consented test images. Do not commit database credentials or private
participant data to a public repository.