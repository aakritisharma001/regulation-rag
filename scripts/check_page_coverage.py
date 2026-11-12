import json
from collections import defaultdict

with open("storage/metadata.json", "r", encoding="utf-8") as file:
    chunks = json.load(file)

coverage = defaultdict(set)

for chunk in chunks:
    coverage[chunk["document"]].add(chunk["page"])

for document, pages in sorted(coverage.items()):
    print("\n" + document)
    print("Pages available:", sorted(pages))
    print("Total pages:", len(pages))