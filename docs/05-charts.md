# Charts

Charts are rendered by matplotlib into a high-resolution PNG and embedded as an image in the PDF. Three chart types are supported: `bar`, `line`, and `pie`.

---

## Common structure

Every chart shares these top-level properties:

```json
{
  "type":       "chart",
  "chart_type": "bar",
  "title":      "Quarterly Returns (%)",
  "width":      "100%",
  "align":      "left",
  "caption":    "Fig. 1 — Optional caption text.",
  "style":      { ... },
  "data":       { ... }
}
```

| Property | Required | Default | Description |
|---|---|---|---|
| `chart_type` | yes | `"bar"` | `"bar"`, `"line"`, or `"pie"`. |
| `title` | no | none | Title rendered inside the chart, above the plot area. |
| `width` | no | `"100%"` | Content width as a percentage (`"80%"`) or absolute points (`"300pt"`). |
| `align` | no | `"left"` | `"left"`, `"center"`, or `"right"`. Most useful when `width` is less than 100%. |
| `caption` | no | none | Caption below the chart, using the `caption` style. |
| `style` | no | `{}` | Per-chart overrides of `chart_style` defaults. |
| `data` | yes | — | Chart data object (see each type below). |

---

## Bar chart

Grouped vertical bars. Supports one or more data series — multiple series are plotted side-by-side within each group.

```json
{
  "type":       "chart",
  "chart_type": "bar",
  "title":      "Quarterly Total Return (%)",
  "data": {
    "labels": ["Q1 2026", "Q2 2026", "Q3 2026", "Q4 2026"],
    "series": [
      { "name": "Portfolio",  "values": [3.2, 4.8, 2.9, 5.1] },
      { "name": "Benchmark",  "values": [2.1, 3.6, 2.4, 4.0] }
    ]
  }
}
```

**Single-series bar (no legend):**
```json
{
  "type":       "chart",
  "chart_type": "bar",
  "title":      "Risk Contribution by Asset Class (%)",
  "style":      { "bar_width": 0.5 },
  "data": {
    "labels": ["Equities", "Fixed Income", "Alternatives", "Real Assets", "Cash"],
    "series": [
      { "name": "", "values": [6.2, 1.4, 1.8, 0.6, 0.1] }
    ]
  }
}
```

Setting `"name": ""` suppresses the legend entry for that series.

---

## Line chart

One line per series, with subtle area fill below each line. Best for time-series data.

```json
{
  "type":       "chart",
  "chart_type": "line",
  "title":      "NAV Progression — Rebased to 100",
  "data": {
    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "series": [
      { "name": "Growth",   "values": [100, 102.4, 105.1, 103.8, 107.2, 110.6, 113.1, 111.8, 115.4, 118.2, 120.1, 122.4] },
      { "name": "Balanced", "values": [100, 101.4, 103.2, 102.3, 104.8, 107.1, 109.0, 108.2, 111.1, 113.4, 114.8, 116.6] }
    ]
  }
}
```

The number of values in each series must equal the number of labels.

---

## Pie chart

One data series only. Values are segment sizes (they do not need to sum to 100 — matplotlib normalises them automatically). Labels are applied directly to the wedges; percentages are shown inside each wedge.

```json
{
  "type":       "chart",
  "chart_type": "pie",
  "title":      "Strategic Asset Allocation",
  "width":      "65%",
  "align":      "center",
  "style":      { "height_ratio": 0.9 },
  "data": {
    "labels": ["Global Equities", "Fixed Income", "Alternatives", "Real Assets", "Cash"],
    "series": [
      { "values": [45, 30, 15, 5, 5] }
    ]
  }
}
```

Note: `"name"` is not required on a pie series since there is only one.

A `height_ratio` of `0.9` (versus the default `0.55`) makes the pie chart taller relative to its width, giving the wedge labels more room.

---

## Data format

```json
"data": {
  "labels": ["Label 1", "Label 2", "Label 3"],
  "series": [
    { "name": "Series A", "values": [10.0, 20.5, 15.3] },
    { "name": "Series B", "values": [8.1,  18.2, 12.7] }
  ]
}
```

- `labels` — array of strings, one per group (bar/line) or segment (pie).
- `series` — array of series objects. Bar and line support multiple series; pie uses only the first.
- `name` — series label, shown in the legend. Use `""` to suppress the legend entry for that series.
- `values` — array of numbers. Must be the same length as `labels`.

---

## Styling charts

Set global defaults in `chart_style` (top-level) and override per-chart in the element's `"style"` block. Both are shallow merges — specify only what you want to change.

### Global defaults

```json
"chart_style": {
  "colors":       ["#003366", "#c69b3a", "#4a8b6e"],
  "grid_color":   "#e8e8e8",
  "height_ratio": 0.5
}
```

### Per-chart override

```json
{
  "type":       "chart",
  "chart_type": "bar",
  "style": {
    "colors":       ["#003366", "#2e6da4"],
    "bar_width":    0.6,
    "height_ratio": 0.4
  },
  "data": { ... }
}
```

### All `chart_style` keys

| Key | Default | Description |
|---|---|---|
| `colors` | `["#1a1a2e", "#2e6da4", "#c69b3a", "#4a8b6e", "#8b5a6e", "#4b8fcf"]` | Ordered list of colours. Series are assigned colours by index; the list cycles if there are more series than colours. |
| `background` | `"#ffffff"` | Chart and axes background colour. |
| `grid` | `true` | Show horizontal grid lines on bar and line charts. |
| `grid_color` | `"#eeeeee"` | Grid line colour. |
| `legend` | `true` | Show a legend when series have non-empty names. |
| `bar_width` | `0.7` | Total grouped bar width as a fraction of the slot width (0–1). Shared across all series in the group. |
| `line_width` | `2.0` | Line width in points for line charts. |
| `dpi` | `150` | Render resolution. Higher values produce sharper charts at the cost of file size. 150 is appropriate for print-quality PDFs. |
| `height_ratio` | `0.55` | Chart height as a multiple of width. `0.55` produces a slightly wide format; `1.0` produces a square chart. |
| `space_before` | `12` | Space before the chart in points. |
| `space_after` | `12` | Space after the chart in points. |

---

## Chart width and alignment

```json
{
  "type":       "chart",
  "chart_type": "pie",
  "width":      "60%",
  "align":      "center"
}
```

- `width` accepts `"100%"` (default), a percentage like `"60%"`, or an absolute value like `"300pt"`.
- `align` controls horizontal alignment when `width` is less than 100%.
- The height is always derived from `width × height_ratio` before rendering, then corrected to the actual rendered image height (so titles and legends are never clipped).

---

## Practical patterns

**Compact side annotation** — narrow chart beside a table, both in the same section:
```json
{ "type": "chart", "chart_type": "bar", "width": "65%", "align": "left", "data": { ... } }
```

**Two charts on one page** — reduce `height_ratio` so both fit:
```json
{ "type": "chart", "chart_type": "line", "style": { "height_ratio": 0.4 }, "data": { ... } }
{ "type": "spacer", "height": 8 }
{ "type": "chart", "chart_type": "bar",  "style": { "height_ratio": 0.4 }, "data": { ... } }
```

**Matching brand colours** — override the default palette across all charts:
```json
"chart_style": {
  "colors": ["#003366", "#c69b3a", "#4a8b6e", "#005599", "#8b5a6e"]
}
```

---

## Limitations

- **Pie charts use only the first series.** Additional series in the `data.series` array are ignored.
- **No horizontal bars.** Bars are always vertical.
- **No stacked bars.** Multiple series are always grouped (side-by-side).
- **No axis label customisation.** The y-axis label, axis limits, and tick format cannot currently be configured through JSON — they use matplotlib's automatic defaults.
- **No interactive elements.** Charts are static images embedded in the PDF.
- **Pie label overlap.** When a pie chart has many small segments, labels on adjacent wedges may overlap. Reduce the number of segments, or use a legend instead by setting `"legend": true` and omitting labels from `data.labels`.
