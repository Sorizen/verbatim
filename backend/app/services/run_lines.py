from app.pipeline.contracts import Brief, Line, LineCheck, SceneCheck, Script
from app.schema import AlignedWordSchema, LineReportSchema, WordDiffSchema


def speaker_names(brief: Brief | None) -> dict[str, str]:
    if not brief:
        return {}
    return {character.id: character.name for character in brief.characters}


def build_line_report(
    shot_id: str,
    line: Line,
    check: LineCheck | None,
    attempt: int | None,
    names: dict[str, str],
) -> LineReportSchema:
    return LineReportSchema(
        shot_id=shot_id,
        speaker=line.speaker,
        speaker_name=names.get(line.speaker, line.speaker),
        text=line.text,
        locked=line.locked,
        attempt=attempt if check else None,
        heard=check.heard if check else None,
        wer=check.wer if check else None,
        diff=[WordDiffSchema.model_validate(item.model_dump()) for item in check.diff] if check else [],
        alignment=[AlignedWordSchema.model_validate(item.model_dump()) for item in check.alignment] if check else [],
        speaker_matches=check.speaker_matches if check else None,
    )


def build_line_reports(brief: Brief | None, script: Script | None, check: SceneCheck | None) -> list[LineReportSchema]:
    if not script:
        return []
    names = speaker_names(brief)
    checks = {line.shot_id: line for line in check.lines} if check else {}
    attempt = check.attempt if check else None
    return [
        build_line_report(shot.id, line, checks.get(shot.id), attempt, names)
        for shot in script.shots
        if (line := shot.line)
    ]
