#!/usr/bin/env python3
"""Remove PDF /Link annotations, retaining page contents and document navigation."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import sys
import tempfile


def page_link_count(reader) -> int:
    return sum(
        ref.get_object().get("/Subtype") == "/Link"
        for page in reader.pages
        for ref in page.get("/Annots", [])
    )


def destination_signature(reader, destination):
    page = reader.get_destination_page_number(destination)
    if page is not None and not 0 <= page < len(reader.pages):
        raise ValueError("A navigation destination points outside the document.")
    values = [destination.get(key) for key in ("/Type", "/Left", "/Bottom", "/Right", "/Top", "/Zoom")]
    # PDF float serialization can round beyond meaningful coordinate precision.
    return [page, *[round(float(value), 6) if isinstance(value, (int, float)) else value for value in values]]


def document_signature(reader):
    outlines = []

    def visit(items, level=0):
        for item in items:
            if isinstance(item, list):
                visit(item, level + 1)
            else:
                outlines.append([level, item.title, destination_signature(reader, item)])

    visit(reader.outline)
    pages = []
    for page in reader.pages:
        contents = page.get_contents()
        non_link_annotations = Counter(
            str(ref.get_object().get("/Subtype"))
            for ref in page.get("/Annots", [])
            if ref.get_object().get("/Subtype") != "/Link"
        )
        pages.append({
            "content_sha256": hashlib.sha256(contents.get_data() if contents else b"").hexdigest(),
            "boxes": {key: [round(float(value), 6) for value in page.get(key, [])]
                      for key in ("/MediaBox", "/CropBox", "/TrimBox", "/BleedBox", "/ArtBox")},
            "rotation": page.rotation,
            "other_annotations": dict(non_link_annotations),
        })
    return {
        "pages": pages,
        "page_labels": reader.page_labels,
        "outlines": outlines,
        "named_destinations": {name: destination_signature(reader, destination)
                               for name, destination in reader.named_destinations.items()},
        "metadata": dict(reader.metadata or {}),
    }


def remove_page_links(source: Path, output: Path, *, force: bool = False) -> dict:
    from pypdf import PdfReader, PdfWriter

    source = source.resolve(strict=True)
    output = output.resolve()
    if source == output or (output.exists() and source.samefile(output)):
        raise ValueError("Use a separate output path to preserve the source PDF.")
    if output.exists() and not force:
        raise FileExistsError(f"Output already exists: {output}; use --force to replace it.")
    source_bytes = source.read_bytes()
    reader = PdfReader(BytesIO(source_bytes))
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported; use an unencrypted source.")
    permissions = reader.trailer["/Root"].get("/Perms")
    if permissions is not None:
        permissions = permissions.get_object()
    permission_signature = permissions and any(permissions.get(key) for key in ("/DocMDP", "/UR", "/UR3"))
    if permission_signature or any(field.get("/FT") == "/Sig" and field.get("/V")
                                   for field in (reader.get_fields() or {}).values()):
        raise ValueError("Digitally signed PDFs cannot be rewritten; use an unsigned source.")
    before = document_signature(reader)
    links_before = page_link_count(reader)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.remove_annotations(subtypes="/Link")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{output.stem}.", suffix=".pdf", dir=output.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            writer.write(stream)
        result = PdfReader(BytesIO(temporary.read_bytes()))
        if page_link_count(result):
            raise ValueError("Verification failed: output still contains page links.")
        if document_signature(result) != before:
            raise ValueError("Verification failed: page content, geometry or navigation changed.")
        if source.read_bytes() != source_bytes:
            raise ValueError("The source PDF changed during processing; output was not replaced.")
        if output.exists() and not force:
            raise FileExistsError(f"Output appeared during processing: {output}")
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return {
        "source": str(source), "output": str(output),
        "pages": len(result.pages), "page_links_before": links_before, "page_links_after": 0,
        "bookmarks": len(before["outlines"]), "named_destinations": len(before["named_destinations"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--force", action="store_true", help="Replace an existing output after verification.")
    args = parser.parse_args()
    try:
        report = remove_page_links(args.source, args.output, force=args.force)
    except ImportError:
        print('ERROR: pypdf is required. Install with: python -m pip install "pypdf>=6,<7"', file=sys.stderr)
        return 1
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    # ASCII JSON also works in terminals whose code page cannot display the path.
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
