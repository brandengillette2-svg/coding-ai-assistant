from app.repo_mapper import RepoMapper


def test_repo_mapper_scan_returns_dict():
    mapper = RepoMapper(".")
    result = mapper.scan()
    assert isinstance(result, dict)


def test_find_relevant_files_handles_empty_task():
    mapper = RepoMapper(".")
    files = mapper.find_relevant_files("")
    assert isinstance(files, list)
