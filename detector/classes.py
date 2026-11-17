"""Static content describing each defect class shown on the website."""

# key = class name in models/class_mapping.json
CLASS_INFO = {
    'Bridge': {
        'slug': 'bridge',
        'title': 'Bridge',
        'blurb': 'Unwanted material connects two adjacent lines, creating a short circuit path.',
    },
    'Clean': {
        'slug': None,
        'title': 'Clean',
        'blurb': 'No defect found. The pattern matches the expected, defect-free structure.',
    },
    'Complex': {
        'slug': 'complex',
        'title': 'Complex',
        'blurb': 'A combination of several defect behaviours that cannot be placed in a single simple class.',
    },
    'Cracks': {
        'slug': 'cracks',
        'title': 'Cracks',
        'blurb': 'Fine fractures running through the pattern or substrate that can grow with thermal stress.',
    },
    'Flat': {
        'slug': 'flat',
        'title': 'Flat',
        'blurb': 'Regions where the expected line relief is missing or flattened out.',
    },
    'Foreign Material': {
        'slug': 'foreign-material',
        'title': 'Foreign Material',
        'blurb': 'Particles or contamination sitting on the wafer surface or embedded in the pattern.',
    },
    'Line Edge Roughness': {
        'slug': 'line-edge-roughness',
        'title': 'Line Edge Roughness',
        'blurb': 'Irregular, wavy line edges that cause variation in critical dimensions.',
    },
    'Linear': {
        'slug': 'liner',  # the image folder is spelled "Liner"
        'title': 'Linear',
        'blurb': 'Straight, line-shaped defects that run along or across the pattern.',
    },
    'Scratches': {
        'slug': 'scratches',
        'title': 'Scratches',
        'blurb': 'Mechanical marks, often from handling or polishing, that cut across the surface.',
    },
    'Z-axis': {
        'slug': 'z-axis',
        'title': 'Z-Axis',
        'blurb': 'Height-direction deviations such as bumps or dips relative to the surface plane.',
    },
}
