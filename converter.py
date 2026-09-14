import re
import os
import sys
import subprocess
import shutil
import tempfile
import fitz  # PyMuPDF
import pymupdf4llm

_cached_tess_info = None
_cached_tess_lang = None

def get_tesseract_info():
    """
    Locates Tesseract executable and tessdata directory.
    Checks bundled Tesseract inside PyInstaller app first, then local project folder, then system installations.
    Returns (tesseract_exe_path, tessdata_dir_path) or (None, None).
    """
    global _cached_tess_info
    if _cached_tess_info is not None:
        return _cached_tess_info

    # 1. Bundled inside PyInstaller or running locally in Doc2MD project
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    bundled_exe = os.path.join(base_dir, 'tesseract_bin', 'tesseract.exe')
    bundled_tessdata = os.path.join(base_dir, 'tesseract_bin', 'tessdata')
    if os.path.exists(bundled_exe):
        _cached_tess_info = (bundled_exe, bundled_tessdata if os.path.exists(bundled_tessdata) else None)
        return _cached_tess_info

    # 2. System installations
    system_candidates = [
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR",
        os.environ.get("TESSERACT_PATH", ""),
    ]
    for sc in system_candidates:
        if sc and os.path.exists(os.path.join(sc, 'tesseract.exe')):
            exe = os.path.join(sc, 'tesseract.exe')
            tessdata = os.path.join(sc, 'tessdata')
            _cached_tess_info = (exe, tessdata if os.path.exists(tessdata) else None)
            return _cached_tess_info

    which_tess = shutil.which("tesseract")
    if which_tess:
        _cached_tess_info = (which_tess, None)
        return _cached_tess_info

    _cached_tess_info = (None, None)
    return _cached_tess_info

def get_tesseract_languages(tess_path, tessdata_dir=None):
    """
    Detects available languages in Tesseract (prioritizing Greek 'ell' and English 'eng').
    """
    global _cached_tess_lang
    if _cached_tess_lang is not None:
        return _cached_tess_lang
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        cmd = [tess_path]
        if tessdata_dir and os.path.exists(tessdata_dir):
            cmd.extend(["--tessdata-dir", tessdata_dir])
        cmd.append("--list-langs")

        env = os.environ.copy()
        tess_dir = os.path.dirname(tess_path)
        if tess_dir not in env.get("PATH", ""):
            env["PATH"] = tess_dir + os.pathsep + env.get("PATH", "")
        if tessdata_dir:
            env["TESSDATA_PREFIX"] = tessdata_dir

        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=flags, env=env)
        langs = res.stdout.lower()
        has_ell = 'ell' in langs
        has_eng = 'eng' in langs
        if has_ell and has_eng:
            _cached_tess_lang = 'ell+eng'
        elif has_ell:
            _cached_tess_lang = 'ell'
        elif has_eng:
            _cached_tess_lang = 'eng'
        else:
            _cached_tess_lang = 'eng'
    except Exception:
        _cached_tess_lang = 'ell+eng'
    return _cached_tess_lang

def ocr_page_tesseract(page, dpi=300):
    """
    Renders a fitz page to a high-res image and extracts text via Tesseract OCR.
    """
    tess_path, tessdata_dir = get_tesseract_info()
    if not tess_path:
        return ""

    lang = get_tesseract_languages(tess_path, tessdata_dir)
    tmp_path = None
    try:
        pix = page.get_pixmap(dpi=dpi)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        pix.save(tmp_path)

        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        cmd = [tess_path]
        if tessdata_dir and os.path.exists(tessdata_dir):
            cmd.extend(["--tessdata-dir", tessdata_dir])
        cmd.extend([tmp_path, "stdout", "-l", lang])

        env = os.environ.copy()
        tess_dir = os.path.dirname(tess_path)
        if tess_dir not in env.get("PATH", ""):
            env["PATH"] = tess_dir + os.pathsep + env.get("PATH", "")
        if tessdata_dir:
            env["TESSDATA_PREFIX"] = tessdata_dir

        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=flags,
            env=env
        )
        return res.stdout.strip()
    except Exception as e:
        print(f"OCR failed on page: {e}")
        return ""
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass



def clean_and_format_markdown_for_llm(md_text):
    """
    Transforms extracted Markdown into clean, structured Markdown optimized for AI / LLMs:
    1. Removes HTML image comment tags.
    2. Cleans up Table of Contents dot leaders (................... 123) and table borders.
    3. Formats section headers to proper Markdown headings (#, ##, ###).
    4. Strips page numbers, headers, and footers.
    5. Normalizes whitespace and list formatting.
    """
    if not md_text:
        return ""

    lines = md_text.split('\n')
    cleaned_lines = []

    for line in lines:
        l_strip = line.strip()

        # 1. Remove PyMuPDF image comment tags
        if l_strip.startswith('<!--') and l_strip.endswith('-->'):
            continue

        # 2. Remove standalone page numbers or page break markers
        if re.match(r'^-----*\s*(Page|\d+)\s*-----*$', l_strip, re.IGNORECASE):
            continue
        if re.match(r'^(page|σελίδα)\s+\d+(\s*(of|από|/)\s*\d+)?$', l_strip, re.IGNORECASE):
            continue

        # 3. Clean Table of Contents lines (dots + page numbers: '................... 123')
        if '....' in l_strip:
            cleaned_title = l_strip.strip('|').strip()
            cleaned_title = re.sub(r'\.{3,}\s*\d+$', '', cleaned_title).strip()
            cleaned_title = re.sub(r'^\**', '', cleaned_title).strip()
            cleaned_title = re.sub(r'\**$', '', cleaned_title).strip()

            if cleaned_title and cleaned_title not in ['---', '|---|', 'Table of Contents']:
                cleaned_lines.append(f"- **{cleaned_title}**")
            continue

        if l_strip in ['|---|', '---', '|**Table of Contents**|', 'Table of Contents']:
            continue

        # 4. Detect section headers and convert to Markdown headings
        if not l_strip.startswith('#') and not l_strip.startswith('-') and len(l_strip) > 4 and len(l_strip) < 120:
            if re.match(r'^(PART\s+[A-Z]|KEY\ ACTION\s+\d+|PRIORITIES\ OF|WHAT\ IS|WHO\ CAN|HOW\ TO|WHICH\ ACTIONS)', l_strip, re.IGNORECASE):
                l_strip = f"## {l_strip}"

        cleaned_lines.append(l_strip)

    result = "\n".join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip()


def convert_pdf_to_md(file_path):
    """
    Converts PDF to rich Markdown formatted for AI (LLM).
    Automatically detects scanned PDFs and performs Tesseract OCR when needed.
    """
    tess_path, _ = get_tesseract_info()
    doc = fitz.open(file_path)
    total_pages = len(doc)

    # Check if the PDF has selectable digital text or is predominantly scanned
    sample_pages = min(total_pages, 5)
    sample_text_count = sum(len(doc[i].get_text().strip()) for i in range(sample_pages))
    avg_chars_per_page = sample_text_count / max(sample_pages, 1)

    # If document has plenty of digital text, try pymupdf4llm first
    if avg_chars_per_page >= 25:
        try:
            raw_md = pymupdf4llm.to_markdown(file_path, page_chunks=False, write_images=False)
            formatted_md = clean_and_format_markdown_for_llm(raw_md)
            if formatted_md and len(formatted_md) > 50:
                doc.close()
                return formatted_md
        except Exception as e:
            print("pymupdf4llm failed, falling back:", e)

    # Process page by page (fallback or scanned document)
    md_lines = []

    for page in doc:
        page_text = page.get_text().strip()

        # If page has virtually no digital text and Tesseract is available, perform OCR
        if len(page_text) < 20 and tess_path:
            ocr_text = ocr_page_tesseract(page)
            if ocr_text:
                page_text = ocr_text

        if not page_text:
            continue

        lines = page_text.split('\n')
        for line in lines:
            text = line.strip()
            if not text:
                continue

            if re.match(r'^\d+$', text) or re.match(r'^(page|σελίδα)\s+\d+', text, re.IGNORECASE):
                continue

            if '....' in text:
                text = re.sub(r'\.{3,}\s*\d+$', '', text).strip()
                if text:
                    md_lines.append(f"- **{text}**")
                continue

            if len(text) < 100 and text.isupper() and not text.startswith('#'):
                md_lines.append(f"## {text}")
            else:
                md_lines.append(text)

        md_lines.append("")

    doc.close()
    result = "\n\n".join(md_lines)
    result = re.sub(r'\n{3,}', '\n\n', result).strip()
    return clean_and_format_markdown_for_llm(result)


def convert_docx_to_md(file_path):
    """
    Converts DOCX to Markdown.
    """
    try:
        import markitdown
        md_engine = markitdown.MarkItDown()
        res = md_engine.convert(file_path)
        if res.text_content:
            return clean_and_format_markdown_for_llm(res.text_content)
    except Exception:
        pass

    try:
        import docx
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            if para.style.name.startswith('Heading 1'):
                full_text.append(f"# {text}")
            elif para.style.name.startswith('Heading 2'):
                full_text.append(f"## {text}")
            elif para.style.name.startswith('Heading 3'):
                full_text.append(f"### {text}")
            else:
                full_text.append(text)
        return "\n\n".join(full_text)
    except Exception as e:
        raise RuntimeError(f"Error converting DOCX: {str(e)}")


import zipfile
import xml.etree.ElementTree as ET

NAMESPACES = {
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
    'xlink': 'http://www.w3.org/1999/xlink',
}

def extract_node_text(elem):
    text_parts = []
    if elem.text:
        text_parts.append(elem.text)
    for child in elem:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag == 's':
            count = int(child.attrib.get(f"{{{NAMESPACES['text']}}}c", 1))
            text_parts.append(' ' * count)
        elif tag == 'tab':
            text_parts.append('\t')
        elif tag == 'line-break':
            text_parts.append('\n')
        elif tag == 'a':
            link_text = extract_node_text(child)
            href = child.attrib.get(f"{{{NAMESPACES['xlink']}}}href", '')
            if href:
                text_parts.append(f"[{link_text}]({href})")
            else:
                text_parts.append(link_text)
        elif tag == 'span':
            span_text = extract_node_text(child)
            text_parts.append(span_text)
        else:
            text_parts.append(extract_node_text(child))
        if child.tail:
            text_parts.append(child.tail)
    return "".join(text_parts)

def convert_odt_to_md(file_path):
    """
    Converts ODT (OpenDocument Text) to Markdown using pypandoc with XML fallback.
    """
    try:
        import pypandoc
        raw_md = pypandoc.convert_file(file_path, 'gfm')
        if raw_md and len(raw_md.strip()) > 20:
            return clean_and_format_markdown_for_llm(raw_md)
    except Exception as e:
        print("pypandoc failed, falling back to XML parser:", e)

    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            if 'content.xml' not in z.namelist():
                raise ValueError("Invalid ODT file: content.xml missing")
            xml_bytes = z.read('content.xml')
        
        root = ET.fromstring(xml_bytes)
        body = root.find('.//office:body', NAMESPACES)
        if body is None:
            return ""
        office_text = body.find('.//office:text', NAMESPACES)
        if office_text is None:
            return ""

        md_lines = []

        def process_element(elem, list_depth=0):
            for child in elem:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                
                if tag == 'h':
                    level = int(child.attrib.get(f"{{{NAMESPACES['text']}}}outline-level", 1))
                    heading_prefix = '#' * min(max(level, 1), 6)
                    text = extract_node_text(child).strip()
                    if text:
                        md_lines.append(f"{heading_prefix} {text}")
                        md_lines.append("")
                        
                elif tag == 'p':
                    text = extract_node_text(child).strip()
                    if text:
                        if list_depth > 0:
                            indent = "  " * (list_depth - 1)
                            md_lines.append(f"{indent}- {text}")
                        else:
                            md_lines.append(text)
                            md_lines.append("")
                            
                elif tag == 'list':
                    process_element(child, list_depth + 1)
                    if list_depth == 0:
                        md_lines.append("")
                        
                elif tag == 'list-item':
                    process_element(child, list_depth)
                    
                elif tag == 'table':
                    rows = []
                    for row in child.findall('.//table:table-row', NAMESPACES):
                        row_cells = []
                        for cell in row.findall('.//table:table-cell', NAMESPACES):
                            cell_text = extract_node_text(cell).replace('\n', ' ').strip()
                            row_cells.append(cell_text)
                        if any(row_cells):
                            rows.append(row_cells)
                    
                    if rows:
                        col_count = max(len(r) for r in rows)
                        for r in rows:
                            while len(r) < col_count:
                                r.append('')
                        md_lines.append("| " + " | ".join(rows[0]) + " |")
                        md_lines.append("| " + " | ".join(["---"] * col_count) + " |")
                        for r in rows[1:]:
                            md_lines.append("| " + " | ".join(r) + " |")
                        md_lines.append("")

        process_element(office_text)
        raw_md = "\n".join(md_lines)
        return clean_and_format_markdown_for_llm(raw_md)
    except Exception as e:
        raise RuntimeError(f"Error converting ODT: {str(e)}")

def convert_image_to_md(file_path):
    """
    Converts standalone image (PNG, JPG, TIFF, etc.) to Markdown using Tesseract OCR.
    """
    tess_path, tessdata_dir = get_tesseract_info()
    if not tess_path:
        raise RuntimeError("Tesseract OCR is not installed or not found. Please install Tesseract OCR.")

    lang = get_tesseract_languages(tess_path, tessdata_dir)
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    cmd = [tess_path]
    if tessdata_dir and os.path.exists(tessdata_dir):
        cmd.extend(["--tessdata-dir", tessdata_dir])
    cmd.extend([file_path, "stdout", "-l", lang])

    env = os.environ.copy()
    tess_dir = os.path.dirname(tess_path)
    if tess_dir not in env.get("PATH", ""):
        env["PATH"] = tess_dir + os.pathsep + env.get("PATH", "")
    if tessdata_dir:
        env["TESSDATA_PREFIX"] = tessdata_dir

    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=flags,
        env=env
    )
    if res.returncode != 0:
        raise RuntimeError(f"OCR failed: {res.stderr}")

    raw_text = res.stdout.strip()
    return clean_and_format_markdown_for_llm(raw_text)

def convert_document(file_path):
    """
    Unified converter based on file extension.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return convert_pdf_to_md(file_path)
    elif ext in ['.docx', '.doc']:
        return convert_docx_to_md(file_path)
    elif ext == '.odt':
        return convert_odt_to_md(file_path)
    elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']:
        return convert_image_to_md(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

