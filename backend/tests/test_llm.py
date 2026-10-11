from services.llm import complete, stream


def test_llm_complete_and_stream():
    result = complete("Say hi in one word")

    assert isinstance(result, str)
    assert len(result) > 0

    chunks = list(stream("Count from 1 to 5"))

    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
