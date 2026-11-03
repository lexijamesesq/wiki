"""Strict frontmatter reader shared by describe.py and contract_lint.py.

Stdlib only (this repo ships no third-party dependencies). It reads the YAML
subset knowledge files use: top-level `key: value` pairs whose values are
plain/quoted scalars, flow lists, block lists, or block scalars. Anything it
cannot read with confidence raises FrontmatterError, so "YAML must parse" is a
real check rather than a best effort.
"""

from __future__ import annotations

import re

KEY_RE = re.compile(r"^([A-Za-z_][\w\-]*)[ ]*:(?:[ ]+(.*))?$")
BLOCK_SCALAR_RE = re.compile(r"^([>|])([+-]?)(\d?)([+-]?)\s*(#.*)?$")
HEADING_RE = re.compile(r"^#[ \t]+(.+?)[ \t]*#*[ \t]*$")
FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")


class FrontmatterError(ValueError):
    """Frontmatter is present but is not readable YAML."""


class Mapping(dict):
    """A nested mapping the reader recognises but does not interpret."""


def split_frontmatter(text):
    """Return (frontmatter_text | None, body). None means no frontmatter block."""
    text = text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].rstrip() in ("---", "..."):
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1 :])
    raise FrontmatterError("frontmatter opens with '---' but is never closed")


def first_heading(body):
    """First `# ` heading outside fenced code, or None."""
    fence = None
    for line in body.split("\n"):
        m = FENCE_RE.match(line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is None:
            h = HEADING_RE.match(line)
            if h:
                return h.group(1).strip()
    return None


def parse_frontmatter(text):
    """Parse frontmatter text into a dict. Raises FrontmatterError."""
    lines = text.split("\n")
    result = {}
    i = 0
    while i < len(lines):
        raw = lines[i]
        lineno = i + 1
        if not raw.strip() or raw.lstrip().startswith("#") and raw[0] != " ":
            i += 1
            continue
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise FrontmatterError(f"line {lineno}: tab used for indentation")
        if raw[0] in " -":
            raise FrontmatterError(f"line {lineno}: unexpected indented content")
        m = KEY_RE.match(raw.rstrip())
        if not m:
            raise FrontmatterError(f"line {lineno}: expected 'key: value'")
        key, rest = m.group(1), (m.group(2) or "").strip()
        if key in result:
            raise FrontmatterError(f"line {lineno}: duplicate key '{key}'")
        value, i = _read_value(lines, i, rest)
        result[key] = value
    return result


def _indented(line):
    return line.startswith((" ", "\t"))


def _read_value(lines, i, rest):
    """Read the value for the key on lines[i]; return (value, next_index)."""
    lineno = i + 1
    i += 1
    if rest.startswith("#"):
        rest = ""
    if rest == "":
        j = i
        while j < len(lines) and (
            not lines[j].strip() or _indented(lines[j]) or lines[j].startswith("- ")
        ):
            j += 1
        block = [
            ln for ln in lines[i:j] if ln.strip() and not ln.lstrip().startswith("#")
        ]
        if not block:
            return None, i
        if block[0].lstrip().startswith("-"):
            return _read_block_list(lines[i:j], i), j
        if not KEY_RE.match(block[0].strip()):
            raise FrontmatterError(f"line {lineno}: nested value is not a mapping")
        return Mapping(), j
    if rest[0] in "[{":
        text, i = _gather_flow(lines, i - 1, rest)
        value, pos = _parse_flow(text, 0, lineno)
        if text[pos:].strip() and not text[pos:].strip().startswith("#"):
            raise FrontmatterError(f"line {lineno}: unexpected text after flow value")
        return (Mapping() if isinstance(value, Mapping) else value), i
    bs = BLOCK_SCALAR_RE.match(rest)
    if bs:
        return _read_block_scalar(lines, i, bs.group(1) == ">", "-" in rest)
    if rest[0] in "\"'":
        return _read_quoted(lines, i - 1, rest)
    return _read_plain(lines, i, rest, lineno)


def _read_block_scalar(lines, i, folded, strip):
    j = i
    body = []
    while j < len(lines) and (not lines[j].strip() or _indented(lines[j])):
        body.append(lines[j])
        j += 1
    content = [ln for ln in body if ln.strip()]
    if not content:
        return "", j
    indent = min(len(ln) - len(ln.lstrip(" ")) for ln in content)
    parts = [ln[indent:] if ln.strip() else "" for ln in body]
    while parts and parts[-1] == "":
        parts.pop()
    if folded:
        out, para = [], []
        for p in parts:
            if p == "":
                out.append(" ".join(para))
                para = []
            else:
                para.append(p.strip())
        out.append(" ".join(para))
        text = "\n".join(s for s in out)
    else:
        text = "\n".join(parts)
    return (text if strip else text + "\n"), j


def _read_quoted(lines, idx, rest):
    """Quoted scalar that may continue over indented lines."""
    quote = rest[0]
    buf = rest
    j = idx + 1
    while True:
        end = _closing_quote(buf, quote)
        if end is not None:
            break
        if j < len(lines) and (_indented(lines[j]) or not lines[j].strip()):
            buf += " " + lines[j].strip()
            j += 1
            continue
        raise FrontmatterError(f"line {idx + 1}: unterminated {quote} quoted string")
    tail = buf[end + 1 :].strip()
    if tail and not tail.startswith("#"):
        raise FrontmatterError(f"line {idx + 1}: unexpected text after quoted string")
    return _unquote(buf[: end + 1]), j


def _closing_quote(s, quote):
    k = 1
    while k < len(s):
        c = s[k]
        if quote == '"' and c == "\\":
            k += 2
            continue
        if c == quote:
            if quote == "'" and k + 1 < len(s) and s[k + 1] == "'":
                k += 2
                continue
            return k
        k += 1
    return None


def _unquote(tok):
    inner = tok[1:-1]
    if tok[0] == "'":
        return inner.replace("''", "'")
    esc = {"n": "\n", "t": "\t", '"': '"', "\\": "\\", "/": "/"}
    out, k = [], 0
    while k < len(inner):
        if inner[k] == "\\" and k + 1 < len(inner):
            out.append(esc.get(inner[k + 1], "\\" + inner[k + 1]))
            k += 2
        else:
            out.append(inner[k])
            k += 1
    return "".join(out)


def _strip_comment(s):
    m = re.search(r"\s#", s)
    return s[: m.start()] if m else s


def _read_plain(lines, i, rest, lineno):
    parts = [_strip_comment(rest).strip()]
    j = i
    while j < len(lines) and lines[j].strip() and _indented(lines[j]):
        if lines[j].lstrip().startswith("#"):
            break
        parts.append(_strip_comment(lines[j]).strip())
        j += 1
    text = " ".join(p for p in parts if p)
    return _plain_scalar(text, lineno), j


def _plain_scalar(text, lineno):
    if text == "":
        return None
    if text[0] in "@`":
        raise FrontmatterError(f"line {lineno}: '{text[0]}' cannot start a plain value")
    if text[0] in "*&":
        raise FrontmatterError(
            f"line {lineno}: unquoted '{text[0]}' reads as a YAML alias"
        )
    if re.search(r":(\s|$)", text):
        raise FrontmatterError(
            f"line {lineno}: unquoted ': ' inside a value; quote the value"
        )
    low = text.lower()
    if low in ("null", "~"):
        return None
    if low in ("true", "false"):
        return low == "true"
    if re.fullmatch(r"[-+]?\d+", text):
        return int(text)
    if re.fullmatch(r"[-+]?(\d+\.\d*|\.\d+)([eE][-+]?\d+)?", text):
        return float(text)
    return text


def _read_block_list(block, base):
    items = []
    dash_indent = None
    k = 0
    while k < len(block):
        ln = block[k]
        lineno = base + k + 1
        k += 1
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        indent = len(ln) - len(ln.lstrip(" "))
        if dash_indent is None:
            dash_indent = indent
        if indent > dash_indent:
            # Continuation of the previous entry (mapping keys, nested lists, or a
            # wrapped plain scalar). Mappings stay opaque; plain text is joined.
            if (
                items
                and isinstance(items[-1], str)
                and not isinstance(items[-1], Mapping)
            ):
                items[-1] = (items[-1] + " " + _strip_comment(s)).strip()
            elif not items:
                raise FrontmatterError(f"line {lineno}: unexpected indented content")
            continue
        if (
            indent < dash_indent
            or not s.startswith("-")
            or (len(s) > 1 and s[1] != " ")
        ):
            raise FrontmatterError(f"line {lineno}: malformed list entry")
        item = s[1:].strip()
        if item[:1] in ("'", '"'):
            # A quoted entry may wrap onto deeper-indented lines until it closes.
            while _closing_quote(item, item[0]) is None and k < len(block):
                nxt = block[k]
                if nxt.strip() and len(nxt) - len(nxt.lstrip(" ")) <= dash_indent:
                    break
                item += " " + nxt.strip()
                k += 1
        items.append(_list_item(item, lineno))
    return items


def _list_item(item, lineno):
    if item == "":
        return None
    if item[0] in "[{":
        value, pos = _parse_flow(item, 0, lineno)
        if item[pos:].strip() and not item[pos:].strip().startswith("#"):
            raise FrontmatterError(f"line {lineno}: unexpected text after list entry")
        return Mapping() if isinstance(value, Mapping) else value
    if item[0] in "\"'":
        end = _closing_quote(item, item[0])
        if end is None:
            raise FrontmatterError(f"line {lineno}: unterminated quoted list entry")
        tail = item[end + 1 :].strip()
        if tail and not tail.startswith("#"):
            raise FrontmatterError(f"line {lineno}: unexpected text after list entry")
        return _unquote(item[: end + 1])
    if KEY_RE.match(_strip_comment(item).strip()):
        return Mapping()
    return _plain_scalar(_strip_comment(item).strip(), lineno)


def _gather_flow(lines, idx, rest):
    """Join continuation lines until a flow collection's brackets balance."""
    text = rest
    j = idx + 1
    while _flow_depth(text) > 0:
        if j >= len(lines):
            raise FrontmatterError(f"line {idx + 1}: unterminated flow collection")
        text += " " + lines[j].strip()
        j += 1
    return text, j


def _flow_depth(text):
    depth, quote, k = 0, None, 0
    while k < len(text):
        c = text[k]
        if quote:
            if quote == '"' and c == "\\":
                k += 1
            elif c == quote:
                quote = None
        elif c in "\"'":
            quote = c
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth -= 1
        k += 1
    return depth


def _parse_flow(s, pos, lineno):
    """Parse a flow value starting at s[pos]; return (value, next_pos)."""
    pos = _skip_ws(s, pos)
    if pos >= len(s):
        raise FrontmatterError(f"line {lineno}: empty flow value")
    c = s[pos]
    if c == "[":
        items, pos = [], pos + 1
        while True:
            pos = _skip_ws(s, pos)
            if pos >= len(s):
                raise FrontmatterError(f"line {lineno}: unterminated flow list")
            if s[pos] == "]":
                return items, pos + 1
            value, pos = _parse_flow(s, pos, lineno)
            items.append(value)
            pos = _skip_ws(s, pos)
            if pos < len(s) and s[pos] == ",":
                pos += 1
            elif pos < len(s) and s[pos] != "]":
                raise FrontmatterError(f"line {lineno}: expected ',' or ']' in list")
    if c == "{":
        depth, quote, k = 0, None, pos
        while k < len(s):
            ch = s[k]
            if quote:
                if ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return Mapping(), k + 1
            k += 1
        raise FrontmatterError(f"line {lineno}: unterminated flow mapping")
    if c in "\"'":
        end = _closing_quote(s[pos:], c)
        if end is None:
            raise FrontmatterError(f"line {lineno}: unterminated quoted string")
        return _unquote(s[pos : pos + end + 1]), pos + end + 1
    k = pos
    while k < len(s) and s[k] not in ",]":
        k += 1
    return _plain_scalar(s[pos:k].strip(), lineno), k


def _skip_ws(s, pos):
    while pos < len(s) and s[pos] in " \t":
        pos += 1
    return pos


def read_file(path):
    """Read a knowledge file. Returns (frontmatter | None, body, error | None).

    frontmatter is None when the file has no block or the block is unreadable;
    error carries the reason for the latter.
    """
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    try:
        fm_text, body = split_frontmatter(text)
    except FrontmatterError as exc:
        return None, text, str(exc)
    if fm_text is None:
        return None, body, None
    try:
        return parse_frontmatter(fm_text), body, None
    except FrontmatterError as exc:
        return None, body, str(exc)
