"""
models.py
---------
InsightFace model reference for the Face Recognition Attendance System.

This file is intentionally kept as documentation rather than executable code.

Design decision:
    The InsightFace FaceAnalysis model is initialised directly in recognize.py
    and register.py using MODEL_NAME from config.py. Wrapping it in a shared
    factory function would add an indirection layer with no practical benefit
    for a project of this size — both scripts already load the model in the
    same one-liner:

        app = FaceAnalysis(name=MODEL_NAME)
        app.prepare(ctx_id=0)

    If this project grows to include multiple entry points that all need the
    model (e.g., a REST API or a batch processing script), a shared loader
    can be added here at that point.

Model: buffalo_l
    Architecture : ResNet-based face recognition backbone
    Embedding    : 512-dimensional float32 vector
    Tasks        : Face detection + landmark detection + recognition
    Source       : https://github.com/deepinsight/insightface

To switch models, change MODEL_NAME in config.py.
"""
