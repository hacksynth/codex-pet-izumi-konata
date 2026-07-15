from codex_pet_validator.dco import parse_git_log


def test_parse_git_log_accepts_signed_commit() -> None:
    raw = "abc123\x00Add validator\n\nSigned-off-by: Test User <test@example.com>\n\x1e"
    commits = parse_git_log(raw)
    assert len(commits) == 1
    assert commits[0].sha == "abc123"
    assert commits[0].signed_off


def test_parse_git_log_rejects_unsigned_commit() -> None:
    commits = parse_git_log("def456\x00Unsigned commit\n\x1e")
    assert len(commits) == 1
    assert not commits[0].signed_off
