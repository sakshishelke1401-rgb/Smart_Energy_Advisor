"""Bill-photo OCR: Tesseract (via pytesseract) plus parsing of month / units / amount.

Works best on clear photos. Marathi bills need the Marathi language pack for Tesseract ('mar');
if it is installed it is used together with English automatically. Values are always shown to the
user for confirmation before they are saved.
"""
import io
import os
import re
from functools import lru_cache

from PIL import Image, ImageOps, UnidentifiedImageError

try:
    import pytesseract
except ImportError:  # pragma: no cover
    pytesseract = None

Image.MAX_IMAGE_PIXELS = 40_000_000

ENGLISH_MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
MARATHI_MONTHS = {"जानेवारी": 1, "फेब्रुवारी": 2, "मार्च": 3, "एप्रिल": 4, "मे": 5, "जून": 6, "जुलै": 7,
                  "ऑगस्ट": 8, "सप्टेंबर": 9, "ऑक्टोबर": 10, "नोव्हेंबर": 11, "डिसेंबर": 12}
_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

_MONTH_YEAR = re.compile(
    r"(?P<mon>" + "|".join(sorted(MARATHI_MONTHS, key=len, reverse=True)) + r"|[A-Za-z]{3,9})"
    r"[\s\-,/.]*(?P<year>(?:19|20)\d{2})")
_LABELLED_MONTH = re.compile(
    r"(?:billing\s*(?:period|month)|bill\s*month|month\s*of|बिल\s*महिना|महिना)[^A-Za-z0-9\u0900-\u097F]{0,8}"
    + _MONTH_YEAR.pattern, re.I)
_UNITS = [
    r"(?:units?\s*consumed|total\s*units?|energy\s*consumed|consumption)[^\d\n]{0,14}(\d+(?:\.\d+)?)",
    r"(?:एकूण\s*वापर|वापर|युनिट)[^\d\n]{0,14}(\d+(?:\.\d+)?)",
    r"(\d+(?:\.\d+)?)\s*(?:units|kwh)\b",
]
_AMOUNT = [
    r"(?:net\s*payable|amount\s*payable|total\s*(?:amount|bill)|bill\s*amount|current\s*bill)[^\d\n]{0,14}(\d[\d,]*(?:\.\d+)?)",
    r"(?:देयक\s*रक्कम|एकूण\s*रक्कम|देय\s*रक्कम)[^\d\n]{0,14}(\d[\d,]*(?:\.\d+)?)",
    r"(?:₹|rs\.?)\s*(\d[\d,]*(?:\.\d+)?)",
]


class OCRUnavailable(RuntimeError):
    """Tesseract (or pytesseract) isn't available on this machine."""


def _month_number(name: str):
    if name in MARATHI_MONTHS:
        return MARATHI_MONTHS[name]
    n = name[:3].lower()
    return ENGLISH_MONTHS.index(n) + 1 if n in ENGLISH_MONTHS else None


def _find_month(text: str):
    for pattern in (_LABELLED_MONTH, _MONTH_YEAR):
        for m in pattern.finditer(text):
            num = _month_number(m.group("mon"))
            if num:
                return f"{m.group('year')}-{num:02d}"
    return None


def _first(patterns, text):
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1)
    return None


def parse_bill_text(text: str) -> dict:
    """Pull month / units / amount out of raw OCR text. Missing values come back as None."""
    t = (text or "").translate(_DIGITS)
    units, amount = _first(_UNITS, t), _first(_AMOUNT, t)
    return {"m": _find_month(t),
            "u": float(units) if units else None,
            "a": float(amount.replace(",", "")) if amount else None}


def _configure():
    cmd = os.environ.get("TESSERACT_CMD")
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd


@lru_cache(maxsize=1)
def _languages(cmd=None) -> str:
    try:
        have = set(pytesseract.get_languages(config=""))
    except Exception:
        return "eng"
    return "eng+mar" if {"eng", "mar"} <= have else ("eng" if "eng" in have else sorted(have)[0])


def ocr_available() -> bool:
    if pytesseract is None:
        return False
    _configure()
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def read_bill(data: bytes) -> dict:
    """Run OCR on an uploaded bill photo. Raises OCRUnavailable or ValueError (friendly message)."""
    if not ocr_available():
        raise OCRUnavailable("Automatic reading isn't set up on this server (Tesseract OCR not found). "
                             "Please type the values from your photo.")
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ValueError("That file isn't a readable image.")
    img = ImageOps.autocontrast(ImageOps.exif_transpose(img).convert("L"))
    if img.width < 1600:
        scale = 1600 / img.width
        img = img.resize((1600, max(1, int(img.height * scale))), Image.LANCZOS)
    langs = _languages(os.environ.get("TESSERACT_CMD"))
    try:
        text = pytesseract.image_to_string(img, lang=langs, config="--psm 6", timeout=45)
    except pytesseract.TesseractError:
        raise ValueError("I couldn't read any text from this photo. Try a clearer, well-lit picture.")
    except RuntimeError:
        raise ValueError("Reading the photo took too long. Try a smaller or clearer image.")
    result = parse_bill_text(text)
    result["languages"] = langs
    return result
