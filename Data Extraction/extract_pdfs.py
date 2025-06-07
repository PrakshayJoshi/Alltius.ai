import os
import json
import fitz  # PyMuPDF

def extract_text_from_pdfs(pdf_folder: str):
    """Reads all PDFs in a folder and returns a list of dicts with filename and content."""
    data = []

    for fname in os.listdir(pdf_folder):
        if not fname.lower().endswith(".pdf"):
            continue

        path = os.path.join(pdf_folder, fname)
        doc = fitz.open(path)
        text_chunks = []

        for page in doc:
            # get_text("text") returns the plain text of the page
            text = page.get_text("text")
            if text.strip():
                text_chunks.append(text.strip())

        full_text = "\n\n".join(text_chunks)
        data.append({
            "filename": fname,
            "content": full_text
        })
        print(f"Extracted {len(text_chunks)} pages from {fname}")

    return data

def main():
    pdf_folder = os.path.join(os.path.dirname(__file__), "..", "pdfs")
    output_path = os.path.join(os.path.dirname(__file__), "insurance_pdfs_data.json")

    print("Reading PDFs from:", pdf_folder)
    pdf_data = extract_text_from_pdfs(pdf_folder)

    # Save to JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pdf_data, f, ensure_ascii=False, indent=2)
    print("Saved extracted text to:", output_path)

if __name__ == "__main__":
    main()

