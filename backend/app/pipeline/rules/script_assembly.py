from app.exceptions import ContractViolationError
from app.pipeline.contracts import Line, LineDraft, Script, ScriptDraft, Shot

UNKNOWN_LOCKED_INDEX = 'shot {shot_id} refers to locked line {index}, but there are only {count}'


def check_locked_indexes(draft: ScriptDraft, locked_count: int) -> None:
    for shot in draft.shots:
        index = shot.line.locked_line_index if shot.line else None
        if index is not None and not 0 <= index < locked_count:
            raise ContractViolationError(UNKNOWN_LOCKED_INDEX.format(shot_id=shot.id, index=index, count=locked_count))


def assemble_line(shot_id: str, draft: LineDraft, locked_lines: list[str]) -> Line:
    if draft.locked_line_index is None:
        return Line(speaker=draft.speaker, text=(draft.text or '').strip(), emotion=draft.emotion, locked=False)
    if not 0 <= draft.locked_line_index < len(locked_lines):
        raise ContractViolationError(
            UNKNOWN_LOCKED_INDEX.format(shot_id=shot_id, index=draft.locked_line_index, count=len(locked_lines))
        )
    return Line(
        speaker=draft.speaker,
        text=locked_lines[draft.locked_line_index],
        emotion=draft.emotion,
        locked=True,
    )


def assemble_script(draft: ScriptDraft, locked_lines: list[str]) -> Script:
    shots = [
        Shot(
            id=shot.id,
            beat=shot.beat,
            duration_s=shot.duration_s,
            line=assemble_line(shot.id, shot.line, locked_lines) if shot.line else None,
        )
        for shot in draft.shots
    ]
    return Script(title=draft.title, shots=shots)
