#!/usr/bin/env python3
"""Check a deck spec (deck.json) against assets/deck.schema.json, without building anything.

    validate_spec.py deck.json

For agents and tools that write deck.json without reading the whole reference:
the schema is the contract, and this script checks it with the standard library
only (no jsonschema package). It implements the subset of JSON Schema that the
schema uses; any other validator (draft 2020-12) gives the same answer.

Prints {"valid": bool, "errors": [{"path": "slides[2].fill.Title", "message": "..."}]}.
Exit codes: 0 valid, 1 invalid, 2 the file cannot be read or is not JSON.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "assets" / "deck.schema.json"
# Annotations are ignored; any other keyword in the schema is a programming error.
ANNOTATIONS = {"$schema", "$id", "title", "description"}
KEYWORDS = {"$ref", "$defs", "type", "enum", "properties", "required", "additionalProperties", "items",
            "minItems", "maxItems", "minProperties", "minimum", "maximum", "minLength", "pattern", "anyOf"}
TYPES = {
    "null": lambda v: v is None,
    "boolean": lambda v: isinstance(v, bool),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "string": lambda v: isinstance(v, str),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
}


def load_schema(path: Path = SCHEMA_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _join(path: str, key) -> str:
    if isinstance(key, int):
        return f"{path}[{key}]"
    return f"{path}.{key}" if path else str(key)


class Validator:
    def __init__(self, schema: dict):
        self.root = schema

    def _ref(self, ref: str) -> dict:
        node = self.root
        for part in ref.lstrip("#/").split("/"):
            node = node[part]
        return node

    def errors(self, value, schema: dict | None = None, path: str = "") -> list:
        schema = self.root if schema is None else schema
        unknown = set(schema) - KEYWORDS - ANNOTATIONS
        if unknown:
            raise ValueError(f"schema keyword(s) not supported by validate_spec.py: {sorted(unknown)}")
        out = []

        def err(msg, at=path):
            out.append({"path": at or "(root)", "message": msg})

        if "$ref" in schema:
            out += self.errors(value, self._ref(schema["$ref"]), path)
        if "type" in schema:
            types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
            if not any(TYPES[t](value) for t in types):
                err(f"expected {' or '.join(types)}, got {_type_name(value)}")
                return out
        if "enum" in schema and value not in schema["enum"]:
            err(f"{value!r} is not one of {', '.join(map(repr, schema['enum']))}")
        if isinstance(value, str):
            if len(value) < schema.get("minLength", 0):
                err("must not be empty")
            if "pattern" in schema and not re.search(schema["pattern"], value):
                err(f"{value!r} does not match {schema['pattern']}")
        if TYPES["number"](value):
            if "minimum" in schema and value < schema["minimum"]:
                err(f"must be at least {schema['minimum']}")
            if "maximum" in schema and value > schema["maximum"]:
                err(f"must be at most {schema['maximum']}")
        if isinstance(value, list):
            if len(value) < schema.get("minItems", 0):
                err(f"needs at least {schema['minItems']} item(s)")
            if "maxItems" in schema and len(value) > schema["maxItems"]:
                err(f"takes at most {schema['maxItems']} item(s)")
            if "items" in schema:
                for i, item in enumerate(value):
                    out += self.errors(item, schema["items"], _join(path, i))
        if isinstance(value, dict):
            if len(value) < schema.get("minProperties", 0):
                err("must not be empty")
            for key in schema.get("required", []):
                if key not in value:
                    err(f"missing required key '{key}'")
            props = schema.get("properties", {})
            extra = schema.get("additionalProperties", True)
            for key, item in value.items():
                if key in props:
                    out += self.errors(item, props[key], _join(path, key))
                elif extra is False:
                    allowed = ", ".join(sorted(props))
                    err(f"unknown key '{key}' (allowed: {allowed})", _join(path, key))
                elif isinstance(extra, dict):
                    out += self.errors(item, extra, _join(path, key))
        if "anyOf" in schema:
            out += self._any_of(value, schema["anyOf"], path)
        return out

    def _any_of(self, value, branches: list, path: str) -> list:
        results = [self.errors(value, b, path) for b in branches]
        if any(not r for r in results):
            return []
        here = path or "(root)"
        # A branch that failed only deeper inside the value is the form the author meant:
        # report its errors. Otherwise say plainly that no form fits.
        deep = [r for r in results if all(e["path"] != here for e in r)]
        if deep:
            return min(deep, key=len)
        if all(r and all(e["message"].startswith("missing required key") for e in r) for r in results):
            keys = sorted({e["message"].split("'")[1] for r in results for e in r})
            return [{"path": here, "message": f"needs one of the keys {', '.join(keys)}"}]
        return [{"path": here, "message": f"{_type_name(value)} value does not match any accepted form "
                                          "(see references/spec-reference.md)"}]


def _type_name(value) -> str:
    for name in ("null", "boolean", "integer", "number", "string", "array", "object"):
        if TYPES[name](value):
            return name
    return type(value).__name__


def validate(spec, schema: dict | None = None) -> list:
    """List of {"path", "message"}; empty when the spec is valid."""
    return Validator(schema or load_schema()).errors(spec)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv and argv[0] in ("-h", "--help") else 2
    try:
        spec = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": f"cannot read {argv[0]} as JSON ({exc})"}, ensure_ascii=False))
        return 2
    errors = validate(spec)
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to a legacy code page; agents read UTF-8
        getattr(_stream, "reconfigure", lambda **_: None)(encoding="utf-8")
    sys.exit(main())
