import os
from pathlib import Path

import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_VERA_DIR = os.path.join(os.path.dirname(reportlab.__file__), "fonts")

_VARIANT_SUFFIXES = [
    ("regular",     ""),
    ("bold",        "-Bold"),
    ("italic",      "-Oblique"),
    ("bold_italic", "-BoldOblique"),
]


def register_builtin_fonts():
    """Register the Vera font family bundled with ReportLab as embedded defaults."""
    pdfmetrics.registerFont(TTFont("Vera", os.path.join(_VERA_DIR, "Vera.ttf")))
    pdfmetrics.registerFont(TTFont("Vera-Bold", os.path.join(_VERA_DIR, "VeraBd.ttf")))
    pdfmetrics.registerFont(TTFont("Vera-Italic", os.path.join(_VERA_DIR, "VeraIt.ttf")))
    pdfmetrics.registerFont(TTFont("Vera-BoldItalic", os.path.join(_VERA_DIR, "VeraBI.ttf")))
    pdfmetrics.registerFontFamily(
        "Vera",
        normal="Vera",
        bold="Vera-Bold",
        italic="Vera-Italic",
        boldItalic="Vera-BoldItalic",
    )


def register_fonts(fonts_config, base_path=None):
    """Register custom TTF font families from the config fonts list."""
    for font in fonts_config:
        name = font["name"]
        variants = {}

        for field, suffix in _VARIANT_SUFFIXES:
            if field not in font:
                continue
            path = font[field]
            if base_path is not None:
                path = str(Path(base_path) / path)
            registered_name = name if not suffix else f"{name}{suffix}"
            try:
                pdfmetrics.registerFont(TTFont(registered_name, path))
            except Exception as e:
                raise ValueError(f"Font '{name}' ({field}): cannot load '{path}'") from e
            variants[field] = registered_name

        pdfmetrics.registerFontFamily(
            name,
            normal=variants.get("regular", name),
            bold=variants.get("bold", variants.get("regular", name)),
            italic=variants.get("italic", variants.get("regular", name)),
            boldItalic=variants.get("bold_italic", variants.get("regular", name)),
        )
