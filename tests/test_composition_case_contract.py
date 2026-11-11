import json
from pathlib import Path

CASES = (
    Path(__file__).parent.parent
    / "specimens"
    / "composition"
)

EXPECTED = {
    "CC-00_ALL_PRESENT.json": "COMPOSABLE_FOR_FURTHER_REVIEW",
    "CC-01_CORRELATED_WITNESS.json": "COMPOSABLE_WITH_LIMITATION",
    "CC-02_REQUIRED_DEPENDENCY_HOLD.json": "DEPENDENCY_HOLD",
    "CC-03_CONFLICT_UNRESOLVED.json": "CONFLICT_UNRESOLVED",
    "CC-04_STALE_REQUIRED_OUTPUT.json": "REVALIDATION_REQUIRED",
}


def load_case(filename: str) -> dict:
    return json.loads(
        (CASES / filename).read_text(encoding="utf-8")
    )


def test_all_composition_cases_are_present() -> None:
    present = {path.name for path in CASES.glob("CC-*.json")}
    assert present == set(EXPECTED)


def test_case_ids_match_filenames() -> None:
    for filename in EXPECTED:
        data = load_case(filename)
        assert filename.startswith(data["case_id"])


def test_expected_standings_are_explicit() -> None:
    for filename, expected in EXPECTED.items():
        assert load_case(filename)["expected_standing"] == expected


def test_all_present_case_has_no_unresolved_dependency() -> None:
    data = load_case("CC-00_ALL_PRESENT.json")

    assert data["unresolved_dependencies"] == []
    assert all(
        output["freshness"] == "CURRENT"
        for output in data["outputs"]
        if output["required"]
    )


def test_correlated_witness_is_preserved_as_limitation() -> None:
    data = load_case("CC-01_CORRELATED_WITNESS.json")

    witness = next(
        output
        for output in data["outputs"]
        if output["source_inspector"] == "DELTA-005"
    )

    assert witness["state"] == "CORRELATED_SOURCE"


def test_required_hold_is_explicit_dependency() -> None:
    data = load_case("CC-02_REQUIRED_DEPENDENCY_HOLD.json")

    assert "DELTA-004" in data["unresolved_dependencies"]

    transfer = next(
        output
        for output in data["outputs"]
        if output["source_inspector"] == "DELTA-004"
    )

    assert transfer["required"] is True
    assert transfer["state"] == "HOLD"


def test_conflict_remains_unresolved() -> None:
    data = load_case("CC-03_CONFLICT_UNRESOLVED.json")

    assert data["conflicts"]
    assert data["conflicts"][0]["status"] == "UNRESOLVED"


def test_stale_required_output_is_explicit() -> None:
    data = load_case("CC-04_STALE_REQUIRED_OUTPUT.json")

    stale = [
        output
        for output in data["outputs"]
        if output["required"]
        and output["freshness"] == "STALE"
    ]

    assert len(stale) == 1
    assert stale[0]["source_inspector"] == "DELTA-002"