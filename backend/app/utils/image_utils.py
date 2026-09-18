"""
Image preprocessing utilities: resize, denoise, contrast enhancement,
deskew/rotation correction. Used by the OCR service before extraction
and by the tampering service for forensic analysis.

These use OpenCV/NumPy directly rather than heavier frameworks so the
pipeline stays fast and has minimal dependencies.
"""
from __future__ import annotations

import io
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
from PIL import Image


def load_image_any(path: str | Path) -> np.ndarray:
    """
    Load an image (or first page of a PDF) as a BGR numpy array.
    Raises ValueError on unsupported / unreadable files.
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _load_pdf_first_page(path)

    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        # Fallback via PIL for formats OpenCV may not decode directly (e.g. some PNG color modes)
        try:
            pil_img = Image.open(path).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Could not read image file: {path.name}") from exc
    return img


def _load_pdf_first_page(path: Path) -> np.ndarray:
    """Render the first page of a PDF to a BGR numpy array using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover
        raise ValueError(
            "PDF support requires PyMuPDF (pymupdf). Please upload an image instead, "
            "or install the pymupdf dependency."
        ) from exc

    doc = fitz.open(str(path))
    if doc.page_count == 0:
        raise ValueError("Uploaded PDF has no pages.")
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # upscale 2x for OCR quality
    img_bytes = pix.tobytes("png")
    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def resize_max_dim(img: np.ndarray, max_dim: int = 1600) -> np.ndarray:
    h, w = img.shape[:2]
    scale = max_dim / max(h, w)
    if scale < 1.0:
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def denoise(img: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(img, None, h=6, hColor=6, templateWindowSize=7, searchWindowSize=21)


def enhance_contrast(img: np.ndarray) -> np.ndarray:
    """CLAHE contrast enhancement applied on the L channel of LAB color space."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l2 = clahe.apply(l)
    lab2 = cv2.merge((l2, a, b))
    return cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)


def deskew(img: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Estimate and correct small rotation/skew using the minAreaRect of
    thresholded text-like content. Returns (corrected_image, angle_degrees).
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    coords = np.column_stack(np.where(thresh > 0))
    if coords.shape[0] < 20:
        return img, 0.0

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Only correct small skews typical of scanned/photographed documents;
    # large angles usually mean the heuristic misfired on a busy background.
    if abs(angle) < 0.5 or abs(angle) > 15:
        return img, float(angle)

    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated, float(angle)


def preprocess_pipeline(img: np.ndarray) -> Tuple[np.ndarray, dict]:
    """Run the full preprocessing pipeline and return (result, metadata)."""
    meta = {"steps": []}

    img = resize_max_dim(img)
    meta["steps"].append("resize")

    img = denoise(img)
    meta["steps"].append("denoise")

    img = enhance_contrast(img)
    meta["steps"].append("contrast_enhancement")

    img, angle = deskew(img)
    meta["steps"].append("deskew")
    meta["deskew_angle"] = round(angle, 2)

    return img, meta


def to_grayscale(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
