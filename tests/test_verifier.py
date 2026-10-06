from app.verifier import Verifier


def test_verifier_accepts_clean_output():
    verifier = Verifier()
    result = verifier.evaluate(["collected 3 items", "3 passed"])
    assert result.passed is True


def test_verifier_flags_failures():
    verifier = Verifier()
    result = verifier.evaluate(["FAILED tests/test_demo.py::test_one"])
    assert result.passed is False
