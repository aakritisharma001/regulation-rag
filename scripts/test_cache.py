from app.cache import AnswerCache


def main():
    cache = AnswerCache(max_size=2)

    cache.set("question1", "answer1")
    cache.set("question2", "answer2")

    print("First retrieval:", cache.get("question1"))

    cache.set("question3", "answer3")

    print("Question 1:", cache.get("question1"))
    print("Question 2:", cache.get("question2"))
    print("Question 3:", cache.get("question3"))

    print("Cache size:", len(cache))


if __name__ == "__main__":
    main()