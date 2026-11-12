from app.ingestion import chunk_text


def test_chunk_text_returns_chunks():
    text = "This is a sample sentence. " * 50

    chunks = chunk_text(
        text,
        chunk_size=100,
        overlap=20
    )

    assert len(chunks) > 1


def test_chunk_text_empty_input():
    chunks = chunk_text("")

    assert chunks == []


def test_chunk_text_invalid_overlap():
    try:
        chunk_text("Sample text", chunk_size=100, overlap=100)
        assert False, "Expected ValueError"
    except ValueError:
        assert True