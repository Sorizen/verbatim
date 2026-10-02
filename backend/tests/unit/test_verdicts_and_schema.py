from typing import Any

import pytest

from app.enums import DiffOp, SceneVerdict
from app.pipeline.checks import decide_scene_verdict
from app.pipeline.contracts import AlignedWord, FormatCheck, LineCheck, Scene, WordDiff
from app.utils import strict_json_schema

GOOD_FORMAT = FormatCheck(aspect_ok=True, duration_s=15.0, duration_ok=True, has_audio=True)


def make_line(*, broken: bool) -> LineCheck:
    diff = [WordDiff(op=DiffOp.DELETE, expected='up', heard=None)] if broken else []
    return LineCheck(
        shot_id='s1',
        speaker='c1',
        expected='pick it up',
        heard='pick it' if broken else 'pick it up',
        wer=0.33 if broken else 0.0,
        diff=diff,
        alignment=[AlignedWord(op=item.op, expected=item.expected, heard=item.heard) for item in diff],
        start_s=0.5,
        end_s=2.0,
        speaker_matches=True,
    )


@pytest.mark.parametrize(
    ('attempt', 'broken', 'expected'),
    [
        (1, False, SceneVerdict.PASS),
        (1, True, SceneVerdict.RETRY),
        (2, True, SceneVerdict.REBUILD_SHOT),
        (3, True, SceneVerdict.NEEDS_REVIEW),
    ],
)
def test_scene_verdict_follows_retry_then_rebuild_then_review(
    attempt: int, broken: bool, expected: SceneVerdict
) -> None:
    verdict, reasons = decide_scene_verdict(
        attempt=attempt, format_check=GOOD_FORMAT, lines=[make_line(broken=broken)], judgment=None
    )
    assert verdict == expected
    assert bool(reasons) == broken


def collect_objects(node: Any) -> list[dict[str, Any]]:
    if isinstance(node, list):
        return [item for child in node for item in collect_objects(child)]
    if not isinstance(node, dict):
        return []
    found = [node] if node.get('type') == 'object' else []
    return found + [item for child in node.values() for item in collect_objects(child)]


def test_strict_schema_inlines_refs_and_requires_every_property() -> None:
    schema = strict_json_schema(Scene)
    assert '$ref' not in str(schema)
    assert 'format' in schema['properties']
    for node in collect_objects(schema):
        assert node['additionalProperties'] is False
        assert node['required'] == list(node['properties'])
