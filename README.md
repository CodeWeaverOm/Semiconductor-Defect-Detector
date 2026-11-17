# Semiconductor Defect Detector (Django)

## Run
    python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py runserver
Open http://127.0.0.1:8000/

## Model files (in `models/`)
- `defect_model.onnx`
- `defect_model.onnx.data`  <-- external weights, REQUIRED for real predictions
- `class_mapping.json`

Without the `.data` file the site runs in a labelled demo mode (sample images only, classified by file name).
