"""Jinja 2 Template Utilities."""

from pathlib import Path
from typing import cast
from dataclasses import dataclass
import importlib.resources

import json5
import jinja2


@dataclass(frozen=True, slots=True)
class TemplateText:
    name: str
    source: str
    filename: str


_TEMPLATE_ANCHOR = __name__
_TEMPLATES: dict[str, TemplateText] = {}


def line_col_from_pos(text: str, loc: int) -> tuple[int, int]:
    if not len(text):
        return 1, 1
    sp = text[: loc + 1].splitlines(keepends=True)
    return len(sp), len(sp[-1])


def parse_file(prefix: str, path: Path) -> dict[str, TemplateText]:
    ret: dict[str, TemplateText] = {}

    text = path.read_text()
    pos = 0

    while True:
        line, col = line_col_from_pos(text, pos)
        head_start = text.find("{#-", pos)
        if head_start == -1:
            return ret

        try:
            head_end = text.find("-#}", head_start)
            if head_end == -1:
                raise ValueError("Unable to find end of header")

            body_end = text.find("{#-", head_end)
            if body_end == -1:
                body_end = len(text)
            pos = body_end

            header = text[head_start + 3 : head_end]
            header = "{" + header + "}"
            header = json5.loads(header)
            header = cast(dict, header)

            name = prefix + ":" + header["name"]

            source = text[head_end + 3 : body_end].strip()

            template_text = TemplateText(name, source, str(path))
            ret[name] = template_text
        except Exception as e:
            e.add_note("Failed to parse template file")
            e.add_note(f"Position: {path}:{line}:{col}")
            raise e


def load_template(name: str) -> tuple[str, str, None] | None:
    if name in _TEMPLATES:
        tpl = _TEMPLATES[name]
        return tpl.source, tpl.filename, None

    prefix = name.split(":")[0]
    filename = prefix + ".jinja"

    with importlib.resources.path(_TEMPLATE_ANCHOR, filename) as path:
        if path.exists():
            tpls = parse_file(prefix, path)
            _TEMPLATES.update(tpls)

    if name in _TEMPLATES:
        tpl = _TEMPLATES[name]
        return tpl.source, tpl.filename, None

    return None


def cpp_type(type: str) -> str:
    return {
        "i8": "std::int8_t",
        "i16": "std::int16_t",
        "i32": "std::int32_t",
        "i64": "std::int64_t",
        "u8": "std::uint8_t",
        "u16": "std::uint16_t",
        "u32": "std::uint32_t",
        "u64": "std::uint64_t",
        "f32": "float",
        "f64": "double",
    }[type]


def arrow_type(type: str) -> str:
    return {
        "i8": "arrow::int8()",
        "i16": "arrow::int16()",
        "i32": "arrow::int32()",
        "i64": "arrow::int64()",
        "u8": "arrow::uint8()",
        "u16": "arrow::uint16()",
        "u32": "arrow::uint32()",
        "u64": "arrow::uint64()",
        "f32": "arrow::float32()",
        "f64": "arrow::float64()",
    }[type]


def arrow_array_type(type: str) -> str:
    return {
        "i8": "arrow::Int8Array",
        "i16": "arrow::Int16Array",
        "i32": "arrow::Int32Array",
        "i64": "arrow::Int64Array",
        "u8": "arrow::UInt8Array",
        "u16": "arrow::UInt16Array",
        "u32": "arrow::UInt32Array",
        "u64": "arrow::UInt64Array",
        "f32": "arrow::FloatArray",
        "f64": "arrow::DoubleArray",
    }[type]


def arrow_builder_type(type: str) -> str:
    return {
        "i8": "arrow::Int8Builder",
        "i16": "arrow::Int16Builder",
        "i32": "arrow::Int32Builder",
        "i64": "arrow::Int64Builder",
        "u8": "arrow::UInt8Builder",
        "u16": "arrow::UInt16Builder",
        "u32": "arrow::UInt32Builder",
        "u64": "arrow::UInt64Builder",
        "f32": "arrow::FloatBuilder",
        "f64": "arrow::DoubleBuilder",
    }[type]


_ENVIRONMENT = jinja2.Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    undefined=jinja2.StrictUndefined,
    loader=jinja2.FunctionLoader(load_template),
)
_ENVIRONMENT.filters["cpp_type"] = cpp_type
_ENVIRONMENT.filters["arrow_type"] = arrow_type
_ENVIRONMENT.filters["arrow_array_type"] = arrow_array_type
_ENVIRONMENT.filters["arrow_builder_type"] = arrow_builder_type


def render(template: str, **kwargs) -> str:
    tpl = _ENVIRONMENT.get_template(template)
    return tpl.render(**kwargs)
