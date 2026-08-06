import re
import os
import fitz  # PyMuPDF
import pymupdf4llm

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
    """
    try:
        raw_md = pymupdf4llm.to_markdown(file_path, page_chunks=False, write_images=False)
        formatted_md = clean_and_format_markdown_for_llm(raw_md)
        if formatted_md and len(formatted_md) > 50:
            return formatted_md
    except Exception as e:
        print("pymupdf4llm failed, falling back:", e)

    doc = fitz.open(file_path)
    md_lines = []

    for page in doc:
        blocks = page.get_text("blocks")
        for b in blocks:
            text = b[4].strip()
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
    return result


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


def convert_document(file_path):
    """
    Unified converter based on file extension.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return convert_pdf_to_md(file_path)
    elif ext in ['.docx', '.doc', '.odt']:
        return convert_docx_to_md(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
