from app.context_library import ContextLibrary
import tempfile


def test_context_library_add_and_search():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = f"{tmp_dir}/context.db"
        store = ContextLibrary(db_path)
        store.add("prior_fix", "token_refresh", "retry the request on token expiry", {"module": "auth"})
        results = store.search("token", limit=5)
        assert len(results) >= 1
        assert results[0]["key"] == "token_refresh"
