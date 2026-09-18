"""
OCR Service (Module 3).

Real local Optical Character Recognition engine for VeriShield:
1. Primary engine: EasyOCR (PyTorch CRAFT detection + CRNN recognition) running locally on CPU/GPU.
2. Fallback engine: Tesseract OCR (via pytesseract wrapper).
3. If neither engine is able to extract text, returns an honest low-confidence/empty result
   clearly flagged for manual review rather than fabricating or simulating text.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_easyocr_reader = None
_easyocr_load_attempted = False
_tesseract_available = None


def _get_easyocr_reader():
    """Lazily construct a singleton EasyOCR Reader. Returns None if unavailable."""
    global _easyocr_reader, _easyocr_load_attempted
    if _easyocr_load_attempted:
        return _easyocr_reader
    _easyocr_load_attempted = True
    try:
        import easyocr

        logger.info("Initializing EasyOCR reader (gpu=%s)...", settings.USE_GPU)
        _easyocr_reader = easyocr.Reader(["en"], gpu=settings.USE_GPU)
        logger.info("EasyOCR reader initialized successfully.")
    except Exception as exc:  # noqa: BLE001
        logger.warning("EasyOCR initialization failed (%s). Will try Tesseract fallback.", exc)
        _easyocr_reader = None
    return _easyocr_reader


def _check_tesseract() -> bool:
    """Check if Tesseract binary is accessible."""
    global _tesseract_available
    if _tesseract_available is not None:
        return _tesseract_available
    try:
        import pytesseract

        pytesseract.get_tesseract_version()
        _tesseract_available = True
    except Exception as exc:  # noqa: BLE001
        logger.warning("Tesseract binary check failed (%s).", exc)
        _tesseract_available = False
    return _tesseract_available


class OCRResult:
    def __init__(
        self,
        lines: List[str],
        mean_confidence: float,
        boxes: List[dict],
        engine_used: str = "none",
        status: str = "SUCCESS",
    ):
        self.lines = lines
        self.mean_confidence = mean_confidence
        self.boxes = boxes  # list of {"text": str, "confidence": float, "bbox": [x, y, w, h]}
        self.engine_used = engine_used
        self.status = status


def run_ocr(image_path: str | Path, preprocessed_img: Optional[np.ndarray] = None) -> OCRResult:
    """
    Run real OCR on the given image path or preprocessed numpy array.
    Tries EasyOCR first, then falls back to Tesseract.
    """
    # 1. Try EasyOCR
    reader = _get_easyocr_reader()
    if reader is not None:
        try:
            return _run_easyocr(reader, image_path, preprocessed_img)
        except Exception as exc:  # noqa: BLE001
            logger.warning("EasyOCR inference failed (%s). Attempting Tesseract fallback.", exc)

    # 2. Try Tesseract
    if _check_tesseract():
        try:
            return _run_tesseract(image_path, preprocessed_img)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Tesseract inference failed (%s).", exc)

    # 3. Honest fallback: no fake text
    logger.warning("No OCR engine succeeded for '%s'. Returning empty result for manual review.", Path(image_path).name)
    return OCRResult(
        lines=[],
        mean_confidence=0.0,
        boxes=[],
        engine_used="none",
        status="MANUAL_REVIEW_REQUIRED",
    )


def _run_easyocr(reader, image_path: str | Path, preprocessed_img: Optional[np.ndarray]) -> OCRResult:
    source = preprocessed_img if preprocessed_img is not None else str(image_path)
    raw_results = reader.readtext(source)

    lines: List[str] = []
    boxes: List[dict] = []
    confidences: List[float] = []

    for item in raw_results:
        # EasyOCR format: (bbox, text, prob)
        if len(item) == 3:
            box, text, prob = item
        elif len(item) == 2:
            box, text = item
            prob = 0.5
        else:
            continue

        clean_text = str(text).strip()
        if not clean_text:
            continue

        lines.append(clean_text)
        conf_pct = round(float(prob) * 100, 2)
        confidences.append(conf_pct)

        xs = [pt[0] for pt in box]
        ys = [pt[1] for pt in box]
        min_x = max(0, int(min(xs)))
        min_y = max(0, int(min(ys)))
        width = max(1, int(max(xs) - min(xs)))
        height = max(1, int(max(ys) - min(ys)))

        boxes.append(
            {
                "text": clean_text,
                "confidence": conf_pct,
                "bbox": [min_x, min_y, width, height],
            }
        )

    mean_conf = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
    status = "SUCCESS" if lines else "MANUAL_REVIEW_REQUIRED"

    return OCRResult(
        lines=lines,
        mean_confidence=mean_conf,
        boxes=boxes,
        engine_used="easyocr",
        status=status,
    )


def _run_tesseract(image_path: str | Path, preprocessed_img: Optional[np.ndarray]) -> OCRResult:
    import pytesseract

    if preprocessed_img is not None:
        target = preprocessed_img
    else:
        target = cv2.imread(str(image_path))
        if target is None:
            from PIL import Image

            target = np.array(Image.open(image_path).convert("RGB"))

    data = pytesseract.image_to_data(target, output_type=pytesseract.Output.DICT)

    lines: List[str] = []
    boxes: List[dict] = []
    confidences: List[float] = []

    current_line_words: List[str] = []
    current_line_conf: List[float] = []
    prev_line_num = None

    n_boxes = len(data["text"])
    for i in range(n_boxes):
        text = str(data["text"][i]).strip()
        conf = float(data["conf"][i])
        line_num = data["line_num"][i]

        if not text or conf < 0:
            continue

        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        boxes.append(
            {
                "text": text,
                "confidence": round(conf, 2),
                "bbox": [int(x), int(y), int(w), int(h)],
            }
        )
        confidences.append(conf)

        if prev_line_num is not None and line_num != prev_line_num:
            if current_line_words:
                lines.append(" ".join(current_line_words))
                current_line_words = []
                current_line_conf = []

        current_line_words.append(text)
        current_line_conf.append(conf)
        prev_line_num = line_num

    if current_line_words:
        lines.append(" ".join(current_line_words))

    mean_conf = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
    status = "SUCCESS" if lines else "MANUAL_REVIEW_REQUIRED"

    return OCRResult(
        lines=lines,
        mean_confidence=mean_conf,
        boxes=boxes,
        engine_used="tesseract",
        status=status,
    )
