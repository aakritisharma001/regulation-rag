import json
from collections import defaultdict

with open("storage/metadata.json", "r", encoding="utf-8") as file:
    chunks = json.load(file)

# Pages selected for closer inspection
selected_pages = {
    "297NTF24A93A6BC7943F2A35FACCE28E4ABC3.pdf": [2, 3, 4, 5, 6, 7, 8],
    "475MDA65A2A40240B4510BB6301A33C9ECBFE.pdf": [4, 5, 6, 7, 8, 9],
    "476MDDC5A297B05094F8096910FE97E1AD34D.pdf": [2, 3, 4, 5],
    "FEMA23RA03112026F5D7706996DD3493DAD9E0899C64D4793.pdf": [1],
    "NT298343573D91EA4465B8CFF54B27EC977D5.pdf": [2, 3, 4, 5, 6, 7, 8, 9, 10],
    "NT298AC9CBAC4415B41D5B6CE45FF58A5AB54.pdf": [2, 3, 4],
}

documents = defaultdict(lambda: defaultdict(list))

for chunk in chunks:
    document = chunk["document"]
    page = chunk["page"]

    if page in selected_pages.get(document, []):
        documents[document][page].append(chunk["text"])

for document, pages in sorted(documents.items()):
    print("\n" + "=" * 90)
    print("DOCUMENT:", document)
    print("=" * 90)

    for page, page_chunks in sorted(pages.items()):
        print("\nPAGE:", page)

        # Show up to the first 3 chunks from each selected page
        for chunk in page_chunks[:3]:
            print(chunk[:1000])
            print("-" * 40)