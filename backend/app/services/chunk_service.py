def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
):

    chunks = []

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        start = 0
        chunk_number = 1

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            chunks.append({
                "page_number": page_number,
                "chunk_number": chunk_number,
                "text": chunk_text
            })

            start = end - chunk_overlap
            chunk_number += 1

    return chunks