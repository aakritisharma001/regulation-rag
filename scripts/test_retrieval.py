
from app.retrieval import Retriever


def main():

    print("Loading retriever...")

    retriever = Retriever()

    print("\nRetriever loaded successfully!")

    while True:

        query = input("\nEnter your question (or type exit): ")

        if query.lower().strip() == "exit":
            break

        results = retriever.search(query, top_k=3)

        print("\nRetrieved Results")
        print("=" * 50)

        if not results:
            print("No results found.")
            continue

        for i, result in enumerate(results, start=1):

            print(f"\nResult {i}")

            print("Document:", result["document"])
            print("Page:", result["page"])
            print("Similarity:", round(result["score"], 4))

            print("Text:")
            print(result["text"])


if __name__ == "__main__":
    main()
