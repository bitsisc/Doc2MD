from converter import convert_pdf_to_md

print("Converting programme-guide-2026_en.pdf...")
md_content = convert_pdf_to_md('programme-guide-2026_en.pdf')
with open('programme-guide-2026_en.md', 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Saved programme-guide-2026_en.md ({len(md_content)} characters)")
