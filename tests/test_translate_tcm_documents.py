from scripts.translate_tcm_documents import fetch_untranslated_documents


def test_fetch_untranslated_documents_accepts_limit() -> None:
    # This is a smoke test against the configured development database.
    documents = fetch_untranslated_documents(limit=1)

    assert len(documents) <= 1
