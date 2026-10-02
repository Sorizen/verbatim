from copy import deepcopy
from typing import Any

from pydantic import BaseModel

DEFS_KEY = '$defs'
REF_KEY = '$ref'
REF_PREFIX = '#/$defs/'
PROPERTIES_KEY = 'properties'
TYPE_OBJECT = 'object'
UNSUPPORTED_KEYWORDS = frozenset(
    {
        'title',
        'default',
        'pattern',
        'format',
        'minLength',
        'maxLength',
        'minimum',
        'maximum',
        'exclusiveMinimum',
        'exclusiveMaximum',
        'minItems',
        'maxItems',
        'examples',
    }
)


def strict_json_schema(model: type[BaseModel]) -> dict[str, Any]:
    schema = model.model_json_schema()
    definitions: dict[str, Any] = schema.pop(DEFS_KEY, {})
    inlined: dict[str, Any] = _inline_refs(schema, definitions)
    strict: dict[str, Any] = _strictify(inlined)
    return strict


def _inline_refs(node: Any, definitions: dict[str, Any]) -> Any:
    if isinstance(node, list):
        return [_inline_refs(item, definitions) for item in node]
    if not isinstance(node, dict):
        return node
    if REF_KEY in node:
        target = deepcopy(definitions[node[REF_KEY].removeprefix(REF_PREFIX)])
        overlay = {key: value for key, value in node.items() if key != REF_KEY}
        return _inline_refs({**target, **overlay}, definitions)
    return {key: _inline_refs(value, definitions) for key, value in node.items()}


def _strictify(node: Any) -> Any:
    if isinstance(node, list):
        return [_strictify(item) for item in node]
    if not isinstance(node, dict):
        return node
    strict: dict[str, Any] = {}
    for key, value in node.items():
        if key in UNSUPPORTED_KEYWORDS:
            continue
        if key == PROPERTIES_KEY:
            strict[key] = {name: _strictify(schema) for name, schema in value.items()}
            continue
        strict[key] = _strictify(value)
    if strict.get('type') == TYPE_OBJECT and PROPERTIES_KEY in strict:
        strict['additionalProperties'] = False
        strict['required'] = list(strict[PROPERTIES_KEY])
    return strict
