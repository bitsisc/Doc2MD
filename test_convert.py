import fitz
import pymupdf4llm
import markitdown

print("Testing pymupdf4llm...")
md1 = pymupdf4llm.to_markdown("programme-guide-2026_en.pdf", pages=list(range(10)))
print("--- pymupdf4llm (first 10 pages) ---")
print(md1[:1500])

print("\nTesting markitdown...")
try:
    md_engine = markitdown.MarkItDown()
    res = md_engine.convert("programme-guide-2026_en.pdf")
    print("--- markitdown ---")
    print(res.text_content[:1500])
except Exception as e:
    print("markitdown error:", e)
