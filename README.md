# pdfgen

A command-line tool that renders professional PDFs from a JSON configuration file.

**The idea:** give it a JSON document, get back a polished PDF. Every layout decision has a sensible default — you only specify what you want to change.

```bash
pdfgen report.json output.pdf
```

---

## Why pdfgen?

| Approach | Problem |
|---|---|
| HTML-to-PDF | Unpredictable pagination, font inconsistency, browser quirks |
| Low-level PDF libraries | Write every rectangle and string coordinate by hand |
| **pdfgen** | Describe content and intent; the renderer handles layout |

pdfgen sits in the middle: a clean JSON contract that separates *what you want* from *how it is drawn*. Variable substitution, data fetching, and templating all happen **upstream** — pdfgen receives fully resolved JSON and produces a pixel-perfect PDF.

---

## Installation

Requires Python 3.11+ and a virtual environment (system Python is protected on macOS 14+).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

After installation, `pdfgen` is available as a shell command inside the venv.

---

## Quickstart

The smallest valid document:

```json
{
  "document": { "title": "My First Report" },
  "content": [
    { "type": "heading", "level": 1, "text": "Hello World" },
    { "type": "paragraph", "text": "This is a paragraph." }
  ]
}
```

```bash
pdfgen minimal.json output.pdf
```

This produces an A4 PDF with automatic page numbers, default Oxford Risk typography, and no other configuration required. Every detail — margins, fonts, colours, header, footer — is inherited from the built-in defaults.

---

## The defaults + override model

pdfgen ships with a complete `defaults.json` that defines every configurable property. Your JSON is **deep-merged** on top of it — you only need to include the keys you want to change.

```json
{
  "document": { "title": "Q2 Report" },
  "styles": {
    "h1": { "color": "#003366" }
  }
}
```

This changes the h1 colour to Oxford Navy and leaves every other property — font, size, spacing, margins — exactly as defined in the defaults.

**Merge rules:**

| JSON type | Behaviour |
|---|---|
| Object (`{}`) | Deep merged — only specified keys override |
| Array (`[]`) | User array replaces entirely |
| String / number / boolean | User value replaces |

---

## Features

- **Paragraphs and headings** — levels 1–3, full inline HTML markup (`<b>`, `<i>`, `<u>`)
- **Lists** — bullet and numbered
- **Images** — JPEG, PNG; percentage or point width; optional caption
- **Tables** — full-width by default; column widths, per-column alignment, alternating rows, header repeat on page break
- **Charts** — bar (grouped multi-series), line (with area fill), pie
- **Table of contents** — auto-generated from headings, accurate page numbers, configurable depth
- **Cover page** — full-page design; logo, title, subtitle, author, date
- **Headers and footers** — logo, text zones, separator line
- **Automatic page numbers** — "Page X of Y", always accurate, cover excluded
- **PDF metadata** — title, author, subject, keywords written to document properties
- **Custom fonts** — register any TTF family with bold/italic variants; built-in Vera fallback ensures PDF/UA compliance even without custom fonts
- **Style inheritance** — define a base style once, extend it everywhere
- **PDF/UA-1 accessibility** — structure tree, tagged content, Artifact marking, XMP conformance declaration; validated against ISO 14289-1 via veraPDF

---

## Documentation

| Page | Contents |
|---|---|
| [Document Structure](docs/01-document-structure.md) | JSON envelope, page size, margins, metadata |
| [Styles & Typography](docs/02-styles-and-typography.md) | Built-in styles, overriding, extends chains, inline markup, custom fonts |
| [Content Types](docs/03-content-types.md) | All element types with full examples |
| [Tables](docs/04-tables.md) | Column widths, alignment, styling, large tables |
| [Charts](docs/05-charts.md) | Bar, line, pie; data format, multi-series, style overrides |
| [Cover, Headers & Footers](docs/06-cover-headers-footers.md) | Cover page design, header/footer zones, page numbering |
| [Defaults Reference](docs/07-defaults-reference.md) | Complete annotated defaults.json |
| [Limitations](docs/08-limitations.md) | Known constraints and workarounds |
| [Accessibility — PDF/UA-1](docs/09-accessibility-pdf-ua.md) | Compliance details, font requirements, `check_ua.py`, veraPDF via Docker |

---

## Example files

| File | Demonstrates |
|---|---|
| `examples/phase2_report.json` | Paragraphs, headings, lists, page structure |
| `examples/phase3_tables.json` | All table variants, large wrapping table |
| `examples/phase4_toc.json` | Table of contents, PDF keywords, multi-section report |
| `examples/phase5_charts.json` | Bar, line, and pie charts in a full report |

---

## Project structure

```
pdfgen/
  cli.py               Entry point — parses args, orchestrates merge/render
  merger.py            Deep merge engine
  styles.py            Style extends-chain resolver
  fonts.py             TTF font registration
  renderer.py          Main render function; element dispatch table
  utils.py             Shared path resolution helper
  defaults.json        Built-in defaults (the "hidden complex document")
  elements/
    chart.py           Bar / line / pie chart builder
    image.py           Image flowable builder
    list_element.py    Bullet and numbered list builder
    primitives.py      Spacer, rule, page break
    table.py           Table builder with full styling
    toc.py             Table of contents builder
  templates/
    doc.py             PDFDocTemplate subclass (TOC notification support)
    page.py            Page templates, NumberedCanvas, header/footer drawing
```
