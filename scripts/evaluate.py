
import json
import time
from pathlib import Path

from app.retrieval import Retriever


def main():
    questions_path = Path("data/evaluation_questions.json")

    with open(questions_path, "r", encoding="utf-8") as file:
        questions = json.load(file)

    print("Loading retriever...")
    retriever = Retriever()

    hits_at_3 = 0
    hits_at_5 = 0
    failed_questions = []
    retrieval_times = []

    print("\nStarting evaluation...")
    print("Total questions:", len(questions))

    for number, item in enumerate(questions, start=1):
        question = item["question"]
        relevant_documents = set(item["relevant_documents"])

        start_time = time.perf_counter()

        # Retrieve the top 5 results once.
        results = retriever.search(question, top_k=5)

        elapsed = time.perf_counter() - start_time
        retrieval_times.append(elapsed)

        # Check whether a relevant document appears in top 3.
        top_3_documents = {
            result["document"] for result in results[:3]
        }

        # Check whether a relevant document appears in top 5.
        top_5_documents = {
            result["document"] for result in results[:5]
        }

        hit_3 = bool(relevant_documents.intersection(top_3_documents))
        hit_5 = bool(relevant_documents.intersection(top_5_documents))

        if hit_3:
            hits_at_3 += 1

        if hit_5:
            hits_at_5 += 1

        if not hit_5:
            failed_questions.append({
                "question": question,
                "expected": list(relevant_documents),
                "retrieved": [
                    result["document"] for result in results
                ]
            })

        print(f"Processed {number}/{len(questions)}")

    total = len(questions)

    hit_rate_3 = (hits_at_3 / total) * 100
    hit_rate_5 = (hits_at_5 / total) * 100
    average_retrieval_time = (
        sum(retrieval_times) / total
    ) * 1000

    print("\n" + "=" * 55)
    print("              RETRIEVAL EVALUATION")
    print("=" * 55)

    print(f"Total questions:       {total}")
    print(f"Hits at k=3:           {hits_at_3}/{total}")
    print(f"Hit Rate@3:            {hit_rate_3:.2f}%")
    print(f"Hits at k=5:           {hits_at_5}/{total}")
    print(f"Hit Rate@5:            {hit_rate_5:.2f}%")

    print(
        f"Average retrieval time: {average_retrieval_time:.2f} ms"
    )

    if failed_questions:
        print("\nQuestions with no relevant document in top 5:")

        for item in failed_questions:
            print("\nQuestion:", item["question"])
            print("Expected:", item["expected"])
            print("Retrieved:", item["retrieved"])
    else:
        print("\nAll questions retrieved a relevant document in top 5.")

    print("=" * 55)


if __name__ == "__main__":
    main()
