from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from . import inference
from .classes import CLASS_INFO

MAX_BYTES = 10 * 1024 * 1024


def _sample_files():
    import os
    from django.contrib.staticfiles import finders
    root = finders.find('detector/samples')
    result = {}
    if root and os.path.isdir(root):
        for slug in sorted(os.listdir(root)):
            files = sorted(f for f in os.listdir(os.path.join(root, slug))
                           if f.lower().endswith(('.png', '.jpg', '.jpeg')))
            result[slug] = files
    return result


@ensure_csrf_cookie
def index(request):
    samples = _sample_files()
    classes = []
    for name in inference.get_classes():
        info = CLASS_INFO.get(name, {'slug': None, 'title': name, 'blurb': ''})
        files = samples.get(info['slug'], []) if info['slug'] else []
        classes.append({
            'name': name,
            'title': info['title'],
            'blurb': info['blurb'],
            'images': [{'file': f, 'url': static(f"detector/samples/{info['slug']}/{f}")} for f in files],
        })
    total = sum(len(c['images']) for c in classes)
    return render(request, 'detector/index.html', {
        'classes': classes,
        'num_classes': len(classes),
        'num_samples': total,
        'model': inference.model_status(),
    })


@require_POST
def predict(request):
    upload = request.FILES.get('image')
    if upload is None:
        return JsonResponse({'error': 'No image was received.'}, status=400)
    if upload.size > MAX_BYTES:
        return JsonResponse({'error': 'Image is larger than 10 MB.'}, status=400)
    try:
        result = inference.predict(upload.read(), upload.name)
    except RuntimeError as exc:
        return JsonResponse({'error': str(exc)}, status=503)
    except Exception:
        return JsonResponse({'error': 'That file could not be read as an image.'}, status=400)
    return JsonResponse(result)
