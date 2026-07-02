"""
utils.py
--------
Shared utility functions for the Face Recognition Attendance System.

Centralises embedding normalization, cosine similarity computation, and
logging configuration so every module in the project behaves consistently.
"""

import logging

import numpy as np

from config import LOG_FORMAT, LOG_LEVEL


def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """
    L2-normalize a face embedding vector to unit length.

    Dividing by the L2 norm ensures that the dot product between two
    normalized vectors is exactly their cosine similarity — which is the
    metric used for face matching throughout this project.

    Args:
        embedding: Raw face embedding returned by InsightFace (float32).

    Returns:
        Unit-normalized NumPy float32 array (L2 norm == 1.0).
    """
    return embedding / np.linalg.norm(embedding)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two unit-normalized face embeddings.

    Both inputs must already be L2-normalized via normalize_embedding().
    For unit vectors, the dot product equals the cosine similarity, so no
    additional division is required.

    Args:
        a: First normalized face embedding.
        b: Second normalized face embedding.

    Returns:
        Similarity score as a float in [0.0, 1.0].
        1.0 means identical faces; 0.0 means completely dissimilar.
    """
    return float(np.dot(a, b))


def get_logger(name: str) -> logging.Logger:
    """
    Return a module-level logger configured with the project's log format.

    Uses Python's logging.basicConfig, which is safe to call from multiple
    modules — the logging framework only applies the configuration once.
    Log level and format are read from config.py so they can be changed
    project-wide from a single place.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        A configured Logger instance for the given module name.

    Example:
        logger = get_logger(__name__)
        logger.info("Recognition started.")
    """
    logging.basicConfig(
        format=LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
        level=getattr(logging, LOG_LEVEL.upper()),
    )
    return logging.getLogger(name)
