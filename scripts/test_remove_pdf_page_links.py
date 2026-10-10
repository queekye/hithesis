"""Regression tests for the portable PDF page-link postprocessor."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link, Text
from pypdf.constants import PageLabelStyle
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    Fit,
    NameObject,
    NumberObject,
    TextStringObject,
)

if __package__:
    from . import remove_pdf_page_links
else:
    import remove_pdf_page_links


SCRIPT = Path(__file__).with_name("remove_pdf_page_links.py")
IMAGE_BYTES = bytes([255, 0, 0, 0, 255, 0, 0, 0, 255, 255, 255, 255])


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_fixture(path: Path, *, links: bool = True, encrypted: bool = False) -> None:
    writer = PdfWriter()
    pages = [writer.add_blank_page(width=240, height=300),
             writer.add_blank_page(width=300, height=360)]
    font = writer._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    }))
    image = DecodedStreamObject()
    image.set_data(IMAGE_BYTES)
    image.update({
        NameObject("/Type"): NameObject("/XObject"),
        NameObject("/Subtype"): NameObject("/Image"),
        NameObject("/Width"): NumberObject(2),
        NameObject("/Height"): NumberObject(2),
        NameObject("/ColorSpace"): NameObject("/DeviceRGB"),
        NameObject("/BitsPerComponent"): NumberObject(8),
    })
    image_ref = writer._add_object(image)
    for index, page in enumerate(pages):
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font}),
            NameObject("/XObject"): DictionaryObject({NameObject("/Im1"): image_ref}),
        })
        contents = DecodedStreamObject()
        contents.set_data(
            f"BT /F1 12 Tf 20 240 Td (Fixture page {index + 1}) Tj ET\n"
            "q 30 0 0 30 20 180 cm /Im1 Do Q\n".encode("ascii")
        )
        page[NameObject("/Contents")] = writer._add_object(contents)
    pages[1].rotate(90)
    note = Text(rect=(20, 20, 60, 60), text="中文批注仍须保留", open=True, flags=4)
    note.pop(NameObject("/Flags"), None)
    note[NameObject("/F")] = NumberObject(4)
    note[NameObject("/T")] = TextStringObject("测试作者")
    note[NameObject("/C")] = ArrayObject([NumberObject(1), NumberObject(1), NumberObject(0)])
    writer.add_annotation(0, note)
    if links:
        writer.add_annotation(0, Link(rect=(20, 100, 110, 115), target_page_index=1,
                                      fit=Fit.xyz(left=25.25, top=260.5, zoom=1.5)))
        writer.add_annotation(1, Link(rect=(20, 100, 110, 115), url="https://example.org/research"))
    parent = writer.add_outline_item("第一章 总目录", 0, bold=True,
                                     fit=Fit.xyz(left=21.25, top=240.5, zoom=1.25))
    writer.add_outline_item("第二页 子节", 1, parent=parent,
                            fit=Fit.xyz(left=22.5, top=270.25, zoom=1.5))
    writer.add_named_destination("中文首页", 0)
    writer.add_named_destination("中文第二页", 1)
    writer.set_page_label(0, 0, style=PageLabelStyle.LOWERCASE_ROMAN, prefix="前言-", start=1)
    writer.set_page_label(1, 1, style=PageLabelStyle.DECIMAL, prefix="正文-", start=7)
    writer.add_metadata({"/Title": "含书签和批注的测试文档", "/Author": "测试作者",
                         "/CreationDate": "D:20260101000000+08'00'"})
    writer.generate_file_identifiers()
    if encrypted:
        writer.encrypt("fixture-password")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        writer.write(stream)


def annotation_objects(reader: PdfReader, subtype: str) -> list:
    return [ref.get_object() for page in reader.pages for ref in page.get("/Annots", [])
            if ref.get_object().get("/Subtype") == subtype]


def add_signature_field(path: Path, *, signed: bool) -> None:
    """A synthetic populated signature field exercises refusal, not cryptography."""
    reader = PdfReader(path)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    field = DictionaryObject({
        NameObject("/FT"): NameObject("/Sig"),
        NameObject("/T"): TextStringObject("Synthetic signature"),
    })
    if signed:
        field[NameObject("/V")] = writer._add_object(DictionaryObject({
            NameObject("/Type"): NameObject("/Sig"),
            NameObject("/Filter"): NameObject("/Adobe.PPKLite"),
            NameObject("/SubFilter"): NameObject("/adbe.pkcs7.detached"),
            NameObject("/Contents"): TextStringObject("synthetic-only-not-a-real-signature"),
            NameObject("/ByteRange"): ArrayObject([NumberObject(0), NumberObject(10),
                                                    NumberObject(20), NumberObject(30)]),
        }))
    writer._root_object[NameObject("/AcroForm")] = writer._add_object(DictionaryObject({
        NameObject("/Fields"): ArrayObject([writer._add_object(field)]),
    }))
    writer.write(path)


class RemovePdfPageLinksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="pdf-page-links-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.source = self.directory / "含 空格" / "输入.pdf"
        self.output = self.directory / "输出 文件.pdf"
        make_fixture(self.source)
        self.source_hash = file_hash(self.source)

    def run_cli(self, *arguments: object) -> subprocess.CompletedProcess:
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, arguments)],
                              capture_output=True, text=True, encoding="utf-8",
                              env=environment, check=False)

    def assert_preserved_document(self, output: Path) -> None:
        source = PdfReader(self.source)
        result = PdfReader(output)
        self.assertEqual(len(result.pages), 2)
        self.assertEqual(annotation_objects(result, "/Link"), [])
        self.assertEqual([page.extract_text().strip() for page in result.pages],
                         ["Fixture page 1", "Fixture page 2"])
        for original, processed in zip(source.pages, result.pages):
            self.assertEqual(original.get_contents().get_data(), processed.get_contents().get_data())
            self.assertEqual(list(original.mediabox), list(processed.mediabox))
            self.assertEqual(original.rotation, processed.rotation)
            self.assertEqual(processed["/Resources"]["/Font"]["/F1"]["/BaseFont"], "/Helvetica")
            self.assertEqual(processed["/Resources"]["/XObject"]["/Im1"].get_data(), IMAGE_BYTES)
        notes = annotation_objects(result, "/Text")
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["/Contents"], "中文批注仍须保留")
        self.assertEqual(notes[0]["/T"], "测试作者")
        self.assertEqual(list(notes[0]["/Rect"]), [20, 20, 60, 60])
        self.assertEqual(list(notes[0]["/C"]), [1, 1, 0])
        self.assertEqual(notes[0]["/F"], 4)
        self.assertTrue(notes[0]["/Open"])
        self.assertEqual(result.page_labels, ["前言-i", "正文-7"])
        self.assertEqual(set(result.named_destinations), {"中文首页", "中文第二页"})
        self.assertEqual(result.get_destination_page_number(result.named_destinations["中文首页"]), 0)
        self.assertEqual(result.get_destination_page_number(result.named_destinations["中文第二页"]), 1)
        self.assertEqual(len(result.outline), 2)
        parent, children = result.outline
        self.assertEqual(parent.title, "第一章 总目录")
        self.assertEqual(result.get_destination_page_number(parent), 0)
        self.assertEqual([float(parent.left), float(parent.top), float(parent.zoom)], [21.25, 240.5, 1.25])
        self.assertEqual(len(children), 1)
        child = children[0]
        self.assertEqual(child.title, "第二页 子节")
        self.assertEqual(result.get_destination_page_number(child), 1)
        self.assertEqual([float(child.left), float(child.top), float(child.zoom)], [22.5, 270.25, 1.5])
        self.assertEqual(dict(result.metadata), dict(source.metadata))
        self.assertEqual(result.trailer["/ID"], source.trailer["/ID"])
        self.assertEqual(file_hash(self.source), self.source_hash)

    def test_removes_only_page_links_and_preserves_document(self) -> None:
        report = remove_pdf_page_links.remove_page_links(self.source, self.output)
        self.assertEqual(report["pages"], 2)
        self.assertEqual(report["page_links_before"], 2)
        self.assertEqual(report["page_links_after"], 0)
        self.assertEqual(report["bookmarks"], 2)
        self.assertEqual(report["named_destinations"], 2)
        self.assert_preserved_document(self.output)

    def test_cli_handles_unicode_paths_and_creates_output_directory(self) -> None:
        output = self.directory / "新 输出目录" / "无链接.pdf"
        result = self.run_cli(self.source, output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["page_links_after"], 0)
        self.assert_preserved_document(output)

    def test_processing_already_link_free_pdf_retains_navigation(self) -> None:
        remove_pdf_page_links.remove_page_links(self.source, self.output)
        first_hash = file_hash(self.output)
        second = self.directory / "second.pdf"
        report = remove_pdf_page_links.remove_page_links(self.output, second)
        self.assertEqual(report["page_links_before"], 0)
        self.assertEqual(report["page_links_after"], 0)
        self.assertEqual(file_hash(self.output), first_hash)
        self.assert_preserved_document(second)

    def test_same_input_output_is_rejected_even_with_force(self) -> None:
        for force in (False, True):
            with self.subTest(force=force), self.assertRaisesRegex(ValueError, "separate output"):
                remove_pdf_page_links.remove_page_links(self.source, self.source, force=force)
        result = self.run_cli(self.source, self.source, "--force")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(file_hash(self.source), self.source_hash)

    def test_existing_output_is_protected_without_force(self) -> None:
        existing = b"Existing output must survive"
        self.output.write_bytes(existing)
        with self.assertRaises(FileExistsError):
            remove_pdf_page_links.remove_page_links(self.source, self.output)
        self.assertEqual(self.output.read_bytes(), existing)
        result = self.run_cli(self.source, self.output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--force", result.stderr)
        self.assertEqual(self.output.read_bytes(), existing)
        self.assertEqual(file_hash(self.source), self.source_hash)

    def test_force_replaces_existing_output_after_success(self) -> None:
        self.output.write_bytes(b"Old output")
        result = self.run_cli(self.source, self.output, "--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["page_links_before"], 2)
        self.assert_preserved_document(self.output)
        self.assertEqual(list(self.directory.glob(f".{self.output.stem}.*.pdf")), [])

    def test_missing_input_reports_error_without_creating_output(self) -> None:
        missing = self.directory / "missing.pdf"
        with self.assertRaises(FileNotFoundError):
            remove_pdf_page_links.remove_page_links(missing, self.output)
        result = self.run_cli(missing, self.output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERROR:", result.stderr)
        self.assertFalse(self.output.exists())

    def test_invalid_output_parent_preserves_source(self) -> None:
        parent = self.directory / "parent-is-a-file"
        parent.write_bytes(b"Keep parent")
        with self.assertRaises(OSError):
            remove_pdf_page_links.remove_page_links(self.source, parent / "output.pdf")
        self.assertEqual(parent.read_bytes(), b"Keep parent")
        self.assertEqual(file_hash(self.source), self.source_hash)

    def test_malformed_input_does_not_replace_existing_output_with_force(self) -> None:
        malformed = self.directory / "malformed.pdf"
        malformed.write_bytes(b"This is not a PDF")
        self.output.write_bytes(b"Keep existing output")
        result = self.run_cli(malformed, self.output, "--force")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.output.read_bytes(), b"Keep existing output")
        self.assertEqual(list(self.directory.glob(f".{self.output.stem}.*.pdf")), [])

    def test_source_change_during_processing_preserves_existing_output(self) -> None:
        self.output.write_bytes(b"Keep existing output")
        original_write = PdfWriter.write

        def write_then_change_source(writer, stream):
            result = original_write(writer, stream)
            self.source.write_bytes(self.source.read_bytes() + b"\n% source changed\n")
            return result

        with patch.object(PdfWriter, "write", write_then_change_source):
            with self.assertRaisesRegex(ValueError, "source PDF changed"):
                remove_pdf_page_links.remove_page_links(self.source, self.output, force=True)
        self.assertEqual(self.output.read_bytes(), b"Keep existing output")
        self.assertEqual(list(self.directory.glob(f".{self.output.stem}.*.pdf")), [])

    def test_encrypted_input_is_rejected(self) -> None:
        encrypted = self.directory / "encrypted.pdf"
        make_fixture(encrypted, encrypted=True)
        with self.assertRaisesRegex(ValueError, "Encrypted"):
            remove_pdf_page_links.remove_page_links(encrypted, self.output)
        self.assertFalse(self.output.exists())

    def test_populated_signature_field_is_rejected_without_touching_files(self) -> None:
        add_signature_field(self.source, signed=True)
        signed_hash = file_hash(self.source)
        self.output.write_bytes(b"Keep existing output")
        with self.assertRaisesRegex(ValueError, "Digitally signed"):
            remove_pdf_page_links.remove_page_links(self.source, self.output, force=True)
        self.assertEqual(file_hash(self.source), signed_hash)
        self.assertEqual(self.output.read_bytes(), b"Keep existing output")
        result = self.run_cli(self.source, self.output, "--force")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Digitally signed", result.stderr)

    def test_empty_signature_field_remains_present_after_processing(self) -> None:
        add_signature_field(self.source, signed=False)
        source_hash = file_hash(self.source)
        report = remove_pdf_page_links.remove_page_links(self.source, self.output)
        self.assertEqual(report["page_links_after"], 0)
        result = PdfReader(self.output)
        self.assertEqual(result.get_fields()["Synthetic signature"]["/FT"], "/Sig")
        self.assertNotIn("/V", result.get_fields()["Synthetic signature"])
        self.assertEqual(file_hash(self.source), source_hash)

    def test_same_file_through_hardlink_is_rejected(self) -> None:
        alias = self.directory / "hardlink.pdf"
        try:
            os.link(self.source, alias)
        except OSError as error:
            self.skipTest(f"Hardlinks unavailable: {error}")
        with self.assertRaisesRegex(ValueError, "separate output"):
            remove_pdf_page_links.remove_page_links(self.source, alias, force=True)
        self.assertEqual(file_hash(self.source), self.source_hash)

    def test_certification_signature_without_exposed_field_is_rejected(self) -> None:
        reader = PdfReader(self.source)
        writer = PdfWriter()
        writer.clone_document_from_reader(reader)
        writer._root_object[NameObject("/Perms")] = writer._add_object(DictionaryObject({
            NameObject("/DocMDP"): writer._add_object(DictionaryObject({
                NameObject("/Type"): NameObject("/Sig"),
                NameObject("/Contents"): TextStringObject("synthetic-only"),
            })),
        }))
        writer.write(self.source)
        source_hash = file_hash(self.source)
        with self.assertRaisesRegex(ValueError, "Digitally signed"):
            remove_pdf_page_links.remove_page_links(self.source, self.output)
        self.assertEqual(file_hash(self.source), source_hash)
        self.assertFalse(self.output.exists())

    def test_verification_failure_preserves_existing_output_and_cleans_temporary(self) -> None:
        self.output.write_bytes(b"Keep existing output")
        original_remove = PdfWriter.remove_annotations

        def remove_then_change_metadata(writer, *args, **kwargs):
            result = original_remove(writer, *args, **kwargs)
            writer.add_metadata({"/Title": "Incorrect changed title"})
            return result

        with patch.object(PdfWriter, "remove_annotations", remove_then_change_metadata):
            with self.assertRaisesRegex(ValueError, "Verification failed"):
                remove_pdf_page_links.remove_page_links(self.source, self.output, force=True)
        self.assertEqual(self.output.read_bytes(), b"Keep existing output")
        self.assertEqual(file_hash(self.source), self.source_hash)
        self.assertEqual(list(self.directory.glob(f".{self.output.stem}.*.pdf")), [])


if __name__ == "__main__":
    unittest.main()
