import json
from pathlib import Path

import pytest

from composition_contract.composer import (
    CompositionDiagnostic,
    CompositionState,
    compose_inspector_outputs,
)

CASES = (
    Path(__file__).parent.parent
    / "specimens"
    / "composition"
)


def load_case(filename: str) -> dict:
    return json.loads(
        (CASES / filename).read_text(encoding="utf-8")
    )


def compose_case(filename: str):
    data = load_case(filename)

    return compose_inspector_outputs(
        outputs=data["outputs"],
        unresolved_dependencies=data.get(
            "unresolved_dependencies",
            [],
        ),
        conflicts=data.get("conflicts", []),
    )


def test_all_present_is_composable_for_further_review() -> None:
    result = compose_case("CC-00_ALL_PRESENT.json")

    assert (
        result.state
        is CompositionState.COMPOSABLE_FOR_FURTHER_REVIEW
    )
    assert result.diagnostics == ()


def test_correlated_witness_is_preserved_as_limitation() -> None:
    result = compose_case(
        "CC-01_CORRELATED_WITNESS.json"
    )

    assert (
        result.state
        is CompositionState.COMPOSABLE_WITH_LIMITATION
    )
    assert result.diagnostics == (
        CompositionDiagnostic.CORRELATED_WITNESS_LIMITATION,
    )


def test_required_dependency_hold_propagates() -> None:
    result = compose_case(
        "CC-02_REQUIRED_DEPENDENCY_HOLD.json"
    )

    assert result.state is CompositionState.DEPENDENCY_HOLD
    assert result.diagnostics == (
        CompositionDiagnostic.REQUIRED_DEPENDENCY_UNRESOLVED,
    )


def test_unresolved_conflict_remains_unresolved() -> None:
    result = compose_case(
        "CC-03_CONFLICT_UNRESOLVED.json"
    )

    assert result.state is CompositionState.CONFLICT_UNRESOLVED
    assert result.diagnostics == (
        CompositionDiagnostic.CONFLICT_UNRESOLVED,
    )


def test_stale_required_output_requires_revalidation() -> None:
    result = compose_case(
        "CC-04_STALE_REQUIRED_OUTPUT.json"
    )

    assert result.state is CompositionState.REVALIDATION_REQUIRED
    assert result.diagnostics == (
        CompositionDiagnostic.REQUIRED_OUTPUT_STALE,
    )


def test_expected_standing_is_not_composition_input() -> None:
    data = load_case("CC-02_REQUIRED_DEPENDENCY_HOLD.json")

    data["expected_standing"] = (
        "COMPOSABLE_FOR_FURTHER_REVIEW"
    )

    result = compose_inspector_outputs(
        outputs=data["outputs"],
        unresolved_dependencies=data[
            "unresolved_dependencies"
        ],
        conflicts=data.get("conflicts", []),
    )

    assert result.state is CompositionState.DEPENDENCY_HOLD


def test_result_does_not_claim_global_pass_or_authority() -> None:
    result = compose_case("CC-00_ALL_PRESENT.json")

    assert not hasattr(result, "global_pass")
    assert not hasattr(result, "execution_authority")
    assert not hasattr(result, "claim_truth")


def test_input_states_are_not_rewritten() -> None:
    data = load_case("CC-01_CORRELATED_WITNESS.json")

    before = json.loads(json.dumps(data["outputs"]))

    compose_inspector_outputs(
        outputs=data["outputs"],
        unresolved_dependencies=data[
            "unresolved_dependencies"
        ],
        conflicts=data.get("conflicts", []),
    )

    assert data["outputs"] == before


@pytest.mark.parametrize(
    ("filename", "expected_state"),
    [
        (
            "CC-00_ALL_PRESENT.json",
            CompositionState.COMPOSABLE_FOR_FURTHER_REVIEW,
        ),
        (
            "CC-01_CORRELATED_WITNESS.json",
            CompositionState.COMPOSABLE_WITH_LIMITATION,
        ),
        (
            "CC-02_REQUIRED_DEPENDENCY_HOLD.json",
            CompositionState.DEPENDENCY_HOLD,
        ),
        (
            "CC-03_CONFLICT_UNRESOLVED.json",
            CompositionState.CONFLICT_UNRESOLVED,
        ),
        (
            "CC-04_STALE_REQUIRED_OUTPUT.json",
            CompositionState.REVALIDATION_REQUIRED,
        ),
    ],
)
def test_case_state_matrix(
    filename: str,
    expected_state: CompositionState,
) -> None:
    result = compose_case(filename)

    assert result.state is expected_state