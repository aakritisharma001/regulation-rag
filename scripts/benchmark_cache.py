
import json
import time
import urllib.request
from pathlib import Path


API_URL = "http://127.0.0.1:8000/ask"


def send_question(question):
    payload = json.dumps({
        "question": question
    }).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    start = time.perf_counter()

    with urllib.request.urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    elapsed = (time.perf_counter() - start) * 1000

    return elapsed, result


def main():
    with open(
        "data/evaluation_questions.json",
        "r",
        encoding="utf-8"
    ) as file:
        questions = json.load(file)

    # Use five questions for a manageable API benchmark.
    selected_questions = questions[:5]

    miss_times = []
    hit_times = []

    print("Starting cache benchmark...")
    print("\nROUND 1: Cache MISS")

    for index, item in enumerate(selected_questions, start=1):
        elapsed, result = send_question(item["question"])
        miss_times.append(elapsed)

        print(
            f"Question {index}: "
            f"{result['cache']} | {elapsed:.2f} ms"
        )

    print("\nROUND 2: Cache HIT")

    for index, item in enumerate(selected_questions, start=1):
        elapsed, result = send_question(item["question"])
        hit_times.append(elapsed)

        print(
            f"Question {index}: "
            f"{result['cache']} | {elapsed:.2f} ms"
        )

    average_miss = sum(miss_times) / len(miss_times)
    average_hit = sum(hit_times) / len(hit_times)

    print("\n" + "=" * 50)
    print("             CACHE BENCHMARK")
    print("=" * 50)

    print(f"Average cache MISS latency: {average_miss:.2f} ms")
    print(f"Average cache HIT latency:  {average_hit:.2f} ms")

    if average_hit > 0:
        speedup = average_miss / average_hit
        print(f"Approximate speedup:        {speedup:.2f}x")

    print("=" * 50)


if __name__ == "__main__":
    main()
