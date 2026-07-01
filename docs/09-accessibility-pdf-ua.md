# Accessibility — PDF/UA-1

pdfgen produces PDF/UA-1-conformant output (ISO 14289-1). This means documents are readable by screen readers such as NVDA, JAWS, and macOS VoiceOver, and will pass automated accessibility validators including veraPDF.

---

## What PDF/UA-1 requires

| Requirement | What pdfgen does |
|---|---|
| Document declared as tagged (`MarkInfo/Marked = true`) | Set automatically in the PDF catalog |
| Natural language declared (`Lang`) | Read from `document.lang` (default `"en-GB"`) |
| Structure tree present (`StructTreeRoot`) | Built from every rendered element after the render pass |
| Title shown in viewer title bar (`DisplayDocTitle`) | Set automatically in `ViewerPreferences` |
| Document title in metadata | Read from `document.title` |
| XMP conformance declaration (`pdfuaid:part = 1`) | Written to XMP metadata after the render pass |
| Tab order follows structure (`/Tabs /S`) | Set on every page after the render pass |
| ParentTree (maps MCIDs back to struct elements) | Built and wired to `StructTreeRoot` |
| All content tagged or marked as Artifact | Every flowable wrapped in `/Tag <</MCID N>> BDC…EMC`; decorative drawing (rules, borders, header chrome) wrapped in `/Artifact BDC…EMC` |
| All fonts embedded | Fonts registered via `TTFont(...)` are fully embedded; see [Fonts](#fonts-and-pdf-ua) below |
| Glyph-to-Unicode mapping for all glyphs | Ensured by TrueType fonts; standard Type 1 fonts (Helvetica, Symbol, etc.) do **not** satisfy this requirement |
| `Figure` elements have `/Alt` text | Set from the `alt` field on `image` and `chart` elements |
| Table header cells have `/Scope` | Set to `/Col` on all `TH` struct elements automatically |

---

## Fonts and PDF/UA

This is the most common source of compliance failures. PDF/UA requires **every font used in the document to be embedded** — including fonts used in headers, footers, and the cover page.

The 14 standard PDF fonts (`Helvetica`, `Times-Roman`, `Courier`, `Symbol`, `ZapfDingbats`, and their variants) are **never embedded** by ReportLab. Using them in any element — even a decorative artifact — will fail PDF/UA clause 7.21.4.1.

**pdfgen ships with a built-in fallback:** the Bitstream Vera Sans family (bundled with every ReportLab installation) is registered automatically and used as the default for all styles, headers, footers, and the cover page. This means a config with no `fonts` block is already PDF/UA-compliant.

For production documents, configure your own branded fonts:

```json
{
  "fonts": [
    {
      "name": "BrandSans",
      "regular":     "fonts/BrandSans-Regular.ttf",
      "bold":        "fonts/BrandSans-Bold.ttf",
      "italic":      "fonts/BrandSans-Italic.ttf",
      "bold_italic": "fonts/BrandSans-BoldItalic.ttf"
    }
  ],
  "styles": {
    "body": { "font": "BrandSans" },
    "h1":   { "font": "BrandSans-Bold" }
  }
}
```

When custom fonts are registered, they are used for all paragraph and heading styles. Headers, footers, and the cover page automatically inherit the `body` and `h1` fonts from the resolved styles — no extra configuration is needed.

### Character coverage

Your font must contain a glyph for every character that appears in your content. If a character is missing, ReportLab silently falls back to `Symbol` or `ZapfDingbats` — neither of which is embedded, and both of which lack Unicode mappings. Common offenders:

| Character | Unicode | Risk |
|---|---|---|
| `✓` CHECK MARK | U+2713 | Not in Vera; triggers ZapfDingbats |
| `✗` BALLOT X | U+2717 | Not in Vera; triggers ZapfDingbats |
| `→` RIGHTWARDS ARROW | U+2192 | Not in Vera |
| `−` MINUS SIGN | U+2212 | In Vera; not in Helvetica's WinAnsi encoding |
| `•` BULLET | U+2022 | In Vera |

Use a font with broad Unicode coverage (e.g. Noto Sans, Source Sans Pro) if your content uses symbols outside the Latin-1 range.

---

## Quick check — `check_ua.py`

A lightweight console validator is included in the project root. It uses pikepdf to inspect the generated PDF without running a Java process.

```bash
python3 check_ua.py output.pdf
```

Example output for a passing document:

```
PDF/UA-1 check: output.pdf

  ✓  MarkInfo/Marked = true
  ✓  Document language set (Lang)
  ✓  StructTreeRoot present
  ✓  ViewerPreferences/DisplayDocTitle = true
  ✓  Document title set in metadata
  ✓  XMP metadata: pdfuaid:part = 1
  ✓  ParentTree present in StructTreeRoot
  ✓  All Figure elements have Alt text
  ✓  All TH elements have Scope attribute
  ✓  All struct elements have a Parent reference
  ✓  Structure roles found
  ✓  StructParents on every page
  ✓  Tab order set to structure order (/Tabs /S) on every page
  ✓  BDC/EMC balanced on every page

  14 passed  0 warnings  0 failed
```

`check_ua.py` exits with code 0 on success and code 1 if any check fails — suitable for use in CI.

**Scope:** `check_ua.py` covers the structural requirements that can be verified from the PDF file without a full spec-compliant parser. It does not cover every clause of ISO 14289-1. For authoritative compliance testing, use veraPDF.

---

## Authoritative check — veraPDF

[veraPDF](https://verapdf.org) is the official open-source PDF/UA validator. It validates against every clause of the spec and is the industry-standard tool.

### Setup (Docker — recommended)

The project includes a pre-built Dockerfile at `docker/verapdf/`. A wrapper script handles building the image on first use.

```bash
./verapdf.sh output.pdf
```

The first run builds the Docker image (~2–3 minutes, cached for subsequent runs). Output is an XML validation report. A compliant document shows:

```xml
<validationReport ... isCompliant="true">
  <details passedRules="106" failedRules="0" ...></details>
</validationReport>
```

### Flags and format

```bash
# Plain-text output instead of XML
./verapdf.sh output.pdf --format text

# Fail-fast (exit 1 on any failure) — useful in CI
./verapdf.sh output.pdf --failfast
```

The `--flavour ua1` flag is always passed by `verapdf.sh`; you do not need to add it manually.

### Requirements

- Docker Desktop installed and running
- ARM64 / Apple Silicon: fully supported (the Dockerfile uses `eclipse-temurin:21-jdk-alpine` which has an ARM64 manifest)

---

## Common failures and fixes

| veraPDF rule | Failure message | Fix |
|---|---|---|
| **7.21.4.1** | The font program is not embedded | Replace standard fonts (Helvetica, Symbol, etc.) with TTF fonts registered via the `fonts` config |
| **7.21.7** | The glyph cannot be mapped to Unicode | Same fix — embedded TTF fonts include ToUnicode maps; Symbol/ZapfDingbats do not |
| **7.1** | Content is neither marked as Artifact nor tagged | Usually means a custom drawing routine bypasses the tagged flowable wrappers; all content must go through `TaggedParagraph`, `TaggedHeading`, `TaggedTable`, etc., or be explicitly wrapped in `begin_artifact`/`end_artifact` |
| **7.18.1** | Figure has no Alt text | Add an `"alt"` field to the `image` or `chart` element in your JSON |

---

## What `accessibility.py` provides

All PDF/UA machinery lives in `pdfgen/accessibility.py`. Key components:

- `setup_document(canv, config)` — writes `Lang`, `MarkInfo`, and `DisplayDocTitle` to the PDF catalog during canvas initialisation
- `_StructTracker` — accumulates one record per tagged element during rendering; reset at the start of each canvas pass so only the final multiBuild pass contributes
- `build_struct_tree(tracker, output_path)` — post-processes the rendered PDF with pikepdf: builds the `Document > Sect > element` tree, wires up `ParentTree`, sets `StructParents` and `/Tabs /S` on every page, and writes XMP metadata
- `TaggedParagraph`, `TaggedHeading`, `TaggedCaption`, `TaggedListFlowable` — flowable subclasses that emit `/Tag <</MCID N>> BDC…EMC` around their content
- `TaggedFigure` (`TaggedImage`, `TaggedChart`) — same, for images and charts; requires an `alt` attribute for `Figure` elements
- `TaggedTable` — wraps each cell in `/TH` or `/TD` BDC/EMC; wraps all decorative drawing (backgrounds, grid lines) in `/Artifact BDC…EMC`
- `ArtifactRule` — decorative horizontal rules, marked as Layout Artifact
- `begin_artifact(canv)` / `end_artifact(canv)` — low-level helpers for custom drawing code in `templates/page.py`
