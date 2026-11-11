from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence


class CompositionState(str, Enum):
    COMPOSABLE_FOR_FURTHER_REVIEW = (
        "COMPOSABLE_FOR_FURTHER_REVIEW"
    )
    COMPOSABLE_WITH_LIMITATION = "COMPOSABLE_WITH_LIMITATION"
    DEPENDENCY_HOLD = "DEPENDENCY_HOLD"
    CONFLICT_UNRESOLVED = "CONFLICT_UNRESOLVED"
    REVALIDATION_REQUIRED = "REVALIDATION_REQUIRED"


class CompositionDiagnostic(str, Enum):
    CORRELATED_WITNESS_LIMITATION = (
        "CORRELATED_WITNESS_LIMITATION"
    )
    REQUIRED_DEPENDENCY_UNRESOLVED = (
        "REQUIRED_DEPENDENCY_UNRESOLVED"
    )
    CONFLICT_UNRESOLVED = "CONFLICT_UNRESOLVED"
    REQUIRED_OUTPUT_STALE = "REQUIRED_OUTPUT_STALE"


@dataclass(frozen=True)
class CompositionFinding:
    state: CompositionState
    diagnostics: tuple[CompositionDiagnostic, ...]


def compose_inspector_outputs(
    *,
    outputs: Sequence[Mapping[str, object]],
    unresolved_dependencies: Sequence[str],
    conflicts: Sequence[Mapping[str, object]],
) -> CompositionFinding:
    required_hold = any(
        output.get("required") is True
        and output.get("state") == "HOLD"
        for output in outputs
    )

    if unresolved_dependencies or required_hold:
        return CompositionFinding(
            state=CompositionState.DEPENDENCY_HOLD,
            diagnostics=(
                CompositionDiagnostic
                .REQUIRED_DEPENDENCY_UNRESOLVED,
            ),
        )

    unresolved_conflict = any(
        conflict.get("status") == "UNRESOLVED"
        for conflict in conflicts
    )

    if unresolved_conflict:
        return CompositionFinding(
            state=CompositionState.CONFLICT_UNRESOLVED,
            diagnostics=(
                CompositionDiagnostic.CONFLICT_UNRESOLVED,
            ),
        )

    stale_required_output = any(
        output.get("required") is True
        and output.get("freshness") != "CURRENT"
        for output in outputs
    )

    if stale_required_output:
        return CompositionFinding(
            state=CompositionState.REVALIDATION_REQUIRED,
            diagnostics=(
                CompositionDiagnostic.REQUIRED_OUTPUT_STALE,
            ),
        )

    correlated_witness = any(
        output.get("source_inspector") == "DELTA-005"
        and output.get("state") == "CORRELATED_SOURCE"
        for output in outputs
    )

    if correlated_witness:
        return CompositionFinding(
            state=CompositionState.COMPOSABLE_WITH_LIMITATION,
            diagnostics=(
                CompositionDiagnostic
                .CORRELATED_WITNESS_LIMITATION,
            ),
        )

    return CompositionFinding(
        state=CompositionState.COMPOSABLE_FOR_FURTHER_REVIEW,
        diagnostics=(),
    )