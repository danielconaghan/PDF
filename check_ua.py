#!/usr/bin/env python
"""
Lightweight PDF/UA-1 console validator.

Usage:
    python check_ua.py <file.pdf>

Checks the key PDF/UA-1 (ISO 14289-1) requirements that can be verified
structurally from the file without a full spec-compliant parser.
"""
import sys
import zlib

import pikepdf


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_ua.py <file.pdf>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        pdf = pikepdf.open(path)
    except Exception as e:
        print(f"Cannot open PDF: {e}")
        sys.exit(1)

    results = []

    def ok(name, detail=""):
        results.append(("PASS", name, detail))

    def fail(name, detail=""):
        results.append(("FAIL", name, detail))

    def warn(name, detail=""):
        results.append(("WARN", name, detail))

    root = pdf.Root

    # ── Catalog ───────────────────────────────────────────────────────────────

    mark_info = root.get("/MarkInfo")
    marked = str(mark_info.get("/Marked", "") if mark_info else "").lower()
    (ok if marked == "true" else fail)(
        "MarkInfo/Marked = true",
        "Required: document must declare itself as tagged PDF"
    )

    (ok if hasattr(root, "Lang") else fail)(
        "Document language set (Lang)",
        "Required: natural language of document content"
    )

    (ok if hasattr(root, "StructTreeRoot") else fail)(
        "StructTreeRoot present",
        "Required: structure tree must exist"
    )

    vp = root.get("/ViewerPreferences")
    dt = str(vp.get("/DisplayDocTitle", "") if vp else "").lower()
    (ok if dt == "true" else fail)(
        "ViewerPreferences/DisplayDocTitle = true",
        "Required: title bar must show document title, not filename"
    )

    title = str(pdf.docinfo.get("/Title", "")).strip()
    (ok if title else warn)(
        "Document title set in metadata",
        f"Current value: '{title}'" if title else "Empty — screen readers announce filename instead"
    )

    # XMP pdfuaid:part
    xmp_ok = False
    try:
        meta = pdf.open_metadata()
        xmp_ok = meta.get("pdfuaid:part") == "1"
    except Exception:
        pass
    (ok if xmp_ok else fail)(
        "XMP metadata: pdfuaid:part = 1",
        "Required: declares conformance to PDF/UA-1"
    )

    # ── Structure tree ────────────────────────────────────────────────────────

    if hasattr(root, "StructTreeRoot"):
        str_root = root.StructTreeRoot
        (ok if hasattr(str_root, "ParentTree") else fail)(
            "ParentTree present in StructTreeRoot",
            "Required: maps MCIDs back to their struct elements"
        )

        # Walk struct tree — collect roles and check required fields
        roles_found = set()
        figures_without_alt = 0
        th_without_scope = 0
        elems_without_parent = 0

        def walk(node):
            nonlocal figures_without_alt, th_without_scope, elems_without_parent
            try:
                role = str(node.get("/S", "")).lstrip("/")
                if role:
                    roles_found.add(role)
                if role == "Figure" and not node.get("/Alt"):
                    figures_without_alt += 1
                attr = node.get("/A")
                has_scope = bool(attr and attr.get("/Scope"))
                if role == "TH" and not has_scope:
                    th_without_scope += 1
                if role and not node.get("/P"):
                    elems_without_parent += 1
                kids = node.get("/K")
                if kids is None:
                    return
                if isinstance(kids, pikepdf.Array):
                    for k in kids:
                        try:
                            if isinstance(k, pikepdf.Dictionary):
                                walk(k)
                            elif hasattr(k, "is_indirect") and k.is_indirect:
                                walk(pdf.get_object(k.objgen))
                        except Exception:
                            pass
            except Exception:
                pass

        walk(str_root)

        (ok if figures_without_alt == 0 else fail)(
            "All Figure elements have Alt text",
            f"{figures_without_alt} figure(s) missing Alt attribute"
        )

        (ok if th_without_scope == 0 else warn)(
            "All TH elements have Scope attribute",
            f"{th_without_scope} header cell(s) missing /Scope (Col or Row)"
        )

        (ok if elems_without_parent == 0 else fail)(
            "All struct elements have a Parent reference",
            f"{elems_without_parent} element(s) missing /P"
        )

        useful = {"H1","H2","H3","P","Figure","Table","TR","TH","TD","L","LI","Caption"}
        found_useful = roles_found & useful
        ok(
            "Structure roles found",
            ", ".join(sorted(found_useful)) if found_useful else "(none)"
        )

    # ── Pages ─────────────────────────────────────────────────────────────────

    pages_missing_struct_parents = []
    pages_missing_tabs = []
    pages_unbalanced = []

    for i, page in enumerate(pdf.pages):
        label = f"p{i + 1}"

        if "/StructParents" not in page.obj:
            pages_missing_struct_parents.append(label)

        if "/Tabs" not in page.obj:
            pages_missing_tabs.append(label)

        contents = page.obj.get("/Contents")
        if contents:
            try:
                raw = contents.read_bytes()
                try:
                    data = zlib.decompress(raw)
                except zlib.error:
                    data = raw
                bdc = data.count(b"BDC")
                emc = data.count(b"EMC")
                if bdc != emc:
                    pages_unbalanced.append(f"{label}(BDC={bdc} EMC={emc})")
            except Exception:
                pass

    (ok if not pages_missing_struct_parents else fail)(
        "StructParents on every page",
        f"Missing on: {', '.join(pages_missing_struct_parents)}" if pages_missing_struct_parents else ""
    )

    (ok if not pages_missing_tabs else warn)(
        "Tab order set to structure order (/Tabs /S) on every page",
        f"Missing on: {', '.join(pages_missing_tabs)}" if pages_missing_tabs else ""
    )

    (ok if not pages_unbalanced else fail)(
        "BDC/EMC balanced on every page",
        f"Unbalanced on: {', '.join(pages_unbalanced)}" if pages_unbalanced else ""
    )

    pdf.close()

    # ── Report ────────────────────────────────────────────────────────────────

    print(f"\nPDF/UA-1 check: {path}\n")

    icons = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠"}
    for status, name, detail in results:
        icon = icons[status]
        print(f"  {icon}  {name}")
        if detail and status != "PASS":
            print(f"       {detail}")

    passed = sum(1 for s, _, _ in results if s == "PASS")
    warned = sum(1 for s, _, _ in results if s == "WARN")
    failed = sum(1 for s, _, _ in results if s == "FAIL")

    print(f"\n  {passed} passed  {warned} warnings  {failed} failed\n")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
