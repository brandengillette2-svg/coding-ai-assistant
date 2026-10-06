from app.context_library import ContextLibrary


def test_context_library_add_and_search(tmp_path):
    db_path = tmp_path / "context.db"
    store = ContextLibrary(db_path)
    store.add("prior_fix", "token_refresh", "retry the request on token expiry", {"module": "auth"})
    results = store.search("token", limit=5)
    assert len(results) >= 1
    assert results[0]["key"] == "token_refresh"
