"""ONNX inference for the semiconductor defect classifier.

The network is a torchvision ResNet exported to ONNX: input (N, 3, 224, 224)
float32, output (N, 10) logits. Class names come from models/class_mapping.json.

The weights of the export live in an external file next to the .onnx
(``defect_model.onnx.data``). If it is missing, the model cannot be loaded and
the app falls back to a clearly labelled demo mode (see ``predict``).
"""
import io
import json
import re
import threading

import numpy as np
from django.conf import settings
from PIL import Image, ImageOps

IMG_SIZE = 224
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

_lock = threading.Lock()
_state = {'loaded': False, 'session': None, 'error': None, 'classes': None}


def _load():
    with _lock:
        if _state['loaded']:
            return
        with open(settings.CLASS_MAPPING_PATH, encoding='utf-8') as fh:
            mapping = json.load(fh)
        _state['classes'] = [name for name, _ in sorted(mapping.items(), key=lambda kv: kv[1])]
        try:
            import onnxruntime as ort
            _state['session'] = ort.InferenceSession(
                str(settings.MODEL_PATH), providers=['CPUExecutionProvider'])
        except Exception as exc:  # missing .data file, bad model, no onnxruntime...
            _state['error'] = str(exc)
        _state['loaded'] = True


def get_classes():
    _load()
    return _state['classes']


def model_status():
    _load()
    return {'ready': _state['session'] is not None, 'error': _state['error']}


def preprocess(data: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img).convert('RGB')  # greyscale SEM images -> 3 channels
    img = img.resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - MEAN) / STD
    return arr.transpose(2, 0, 1)[None].astype(np.float32)


def _softmax(x):
    e = np.exp(x - x.max())
    return e / e.sum()


def _demo_guess(filename: str, classes):
    """Demo mode only: read the class from the sample's file name.

    Used when the model weights are missing so the page can still be shown.
    Returns a probability vector or None when the name is not recognised.
    """
    n = re.sub(r'[^a-z]', '', (filename or '').lower())
    keys = [
        ('Bridge', 'bridge'), ('Complex', 'complex'), ('Cracks', 'crack'),
        ('Flat', 'flat'), ('Foreign Material', 'foreg'), ('Foreign Material', 'foreign'),
        ('Line Edge Roughness', 'ler'), ('Linear', 'linear'), ('Linear', 'liner'),
        ('Scratches', 'scratch'), ('Z-axis', 'zaxis'), ('Clean', 'clean'),
    ]
    for cls, key in keys:
        if n.startswith(key) and cls in classes:
            p = np.full(len(classes), 0.01, dtype=np.float32)
            p[classes.index(cls)] = 0.91
            return p / p.sum()
    return None


def predict(data: bytes, filename: str = ''):
    """Return dict with mode, top class and the full probability list."""
    _load()
    classes = _state['classes']
    x = preprocess(data)  # raises on non-image input

    if _state['session'] is not None:
        sess = _state['session']
        logits = sess.run(None, {sess.get_inputs()[0].name: x})[0][0]
        probs = _softmax(logits.astype(np.float64))
        mode = 'model'
    else:
        probs = _demo_guess(filename, classes)
        if probs is None:
            raise RuntimeError(
                'Model weights (models/defect_model.onnx.data) are missing, so only the '
                'sample images from the gallery can be shown in demo mode.')
        mode = 'demo'

    order = np.argsort(-probs)
    return {
        'mode': mode,
        'label': classes[int(order[0])],
        'confidence': float(probs[order[0]]),
        'scores': [{'label': classes[int(i)], 'score': float(probs[i])} for i in order],
    }
