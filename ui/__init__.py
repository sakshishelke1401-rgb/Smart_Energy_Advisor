"""The user interface, kept as Python modules and served by Flask (see app.py)."""
import hashlib

from .page import HTML
from .script import JS
from .styles import CSS

CSS_VERSION = hashlib.sha1(CSS.encode("utf-8")).hexdigest()[:10]
JS_VERSION = hashlib.sha1(JS.encode("utf-8")).hexdigest()[:10]


def render_index() -> str:
    """The page, with cache-busting links to the stylesheet and script."""
    return (HTML.replace("__CSS_URL__", f"/assets/app.css?v={CSS_VERSION}")
                .replace("__JS_URL__", f"/assets/app.js?v={JS_VERSION}"))
