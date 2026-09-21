from pypdf import PdfReader


def extract_text_from_pdf(file_path: str):

    reader = PdfReader(file_path)

    pages_text = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text:
            pages_text.append({
                "page_number": page_number,
                "text": text
            })
    # Ignore the last 8 pages
    if len(pages_text) > 8:
        pages_text = pages_text[:-8]



    return pages_text