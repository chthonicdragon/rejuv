from scripts.validate_examples import validate_examples


def test_all_public_examples_validate() -> None:
    assert validate_examples() == []
