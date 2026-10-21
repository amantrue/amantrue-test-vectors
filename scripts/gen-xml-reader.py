import base64
import json
import os
import re
import shutil
import sys
from xml.parsers import expat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES_FILE = os.path.join(ROOT, "scripts", "xml-reader-cases.json")
OUT_DIR = os.path.join(ROOT, "xml-reader")

NAME_START = (
    (0x3A, 0x3A, 1), (0x41, 0x5A, 1), (0x5F, 0x5F, 1), (0x61, 0x7A, 1),
    (0xC0, 0xD6, 1), (0xD8, 0xF6, 1), (0xF8, 0xFF, 1), (0x100, 0x131, 1),
    (0x134, 0x13E, 1), (0x141, 0x148, 1), (0x14A, 0x17E, 1), (0x180, 0x1C3, 1),
    (0x1CD, 0x1F0, 1), (0x1F4, 0x1F5, 1), (0x1FA, 0x217, 1), (0x250, 0x2A8, 1),
    (0x2BB, 0x2C1, 1), (0x386, 0x386, 1), (0x388, 0x38A, 1), (0x38C, 0x38C, 1),
    (0x38E, 0x3A1, 1), (0x3A3, 0x3CE, 1), (0x3D0, 0x3D6, 1), (0x3DA, 0x3E0, 2),
    (0x3E2, 0x3F3, 1), (0x401, 0x40C, 1), (0x40E, 0x44F, 1), (0x451, 0x45C, 1),
    (0x45E, 0x481, 1), (0x490, 0x4C4, 1), (0x4C7, 0x4C8, 1), (0x4CB, 0x4CC, 1),
    (0x4D0, 0x4EB, 1), (0x4EE, 0x4F5, 1), (0x4F8, 0x4F9, 1), (0x531, 0x556, 1),
    (0x559, 0x559, 1), (0x561, 0x586, 1), (0x5D0, 0x5EA, 1), (0x5F0, 0x5F2, 1),
    (0x621, 0x63A, 1), (0x641, 0x64A, 1), (0x671, 0x6B7, 1), (0x6BA, 0x6BE, 1),
    (0x6C0, 0x6CE, 1), (0x6D0, 0x6D3, 1), (0x6D5, 0x6D5, 1), (0x6E5, 0x6E6, 1),
    (0x905, 0x939, 1), (0x93D, 0x93D, 1), (0x958, 0x961, 1), (0x985, 0x98C, 1),
    (0x98F, 0x990, 1), (0x993, 0x9A8, 1), (0x9AA, 0x9B0, 1), (0x9B2, 0x9B2, 1),
    (0x9B6, 0x9B9, 1), (0x9DC, 0x9DD, 1), (0x9DF, 0x9E1, 1), (0x9F0, 0x9F1, 1),
    (0xA05, 0xA0A, 1), (0xA0F, 0xA10, 1), (0xA13, 0xA28, 1), (0xA2A, 0xA30, 1),
    (0xA32, 0xA33, 1), (0xA35, 0xA36, 1), (0xA38, 0xA39, 1), (0xA59, 0xA5C, 1),
    (0xA5E, 0xA5E, 1), (0xA72, 0xA74, 1), (0xA85, 0xA8B, 1), (0xA8D, 0xA8D, 1),
    (0xA8F, 0xA91, 1), (0xA93, 0xAA8, 1), (0xAAA, 0xAB0, 1), (0xAB2, 0xAB3, 1),
    (0xAB5, 0xAB9, 1), (0xB05, 0xB0C, 1), (0xB0F, 0xB10, 1), (0xB13, 0xB28, 1),
    (0xB2A, 0xB30, 1), (0xB32, 0xB33, 1), (0xB36, 0xB39, 1), (0xB3D, 0xB3D, 1),
    (0xB5C, 0xB5D, 1), (0xB5F, 0xB61, 1), (0xB85, 0xB8A, 1), (0xB8E, 0xB90, 1),
    (0xB92, 0xB95, 1), (0xB99, 0xB9A, 1), (0xB9C, 0xB9C, 1), (0xB9E, 0xB9F, 1),
    (0xBA3, 0xBA4, 1), (0xBA8, 0xBAA, 1), (0xBAE, 0xBB5, 1), (0xBB7, 0xBB9, 1),
    (0xC05, 0xC0C, 1), (0xC0E, 0xC10, 1), (0xC12, 0xC28, 1), (0xC2A, 0xC33, 1),
    (0xC35, 0xC39, 1), (0xC60, 0xC61, 1), (0xC85, 0xC8C, 1), (0xC8E, 0xC90, 1),
    (0xC92, 0xCA8, 1), (0xCAA, 0xCB3, 1), (0xCB5, 0xCB9, 1), (0xCDE, 0xCDE, 1),
    (0xCE0, 0xCE1, 1), (0xD05, 0xD0C, 1), (0xD0E, 0xD10, 1), (0xD12, 0xD28, 1),
    (0xD2A, 0xD39, 1), (0xD60, 0xD61, 1), (0xE01, 0xE2E, 1), (0xE30, 0xE30, 1),
    (0xE32, 0xE33, 1), (0xE40, 0xE45, 1), (0xE81, 0xE82, 1), (0xE84, 0xE84, 1),
    (0xE87, 0xE88, 1), (0xE8A, 0xE8D, 3), (0xE94, 0xE97, 1), (0xE99, 0xE9F, 1),
    (0xEA1, 0xEA3, 1), (0xEA5, 0xEA7, 2), (0xEAA, 0xEAB, 1), (0xEAD, 0xEAE, 1),
    (0xEB0, 0xEB0, 1), (0xEB2, 0xEB3, 1), (0xEBD, 0xEBD, 1), (0xEC0, 0xEC4, 1),
    (0xF40, 0xF47, 1), (0xF49, 0xF69, 1), (0x10A0, 0x10C5, 1), (0x10D0, 0x10F6, 1),
    (0x1100, 0x1100, 1), (0x1102, 0x1103, 1), (0x1105, 0x1107, 1), (0x1109, 0x1109, 1),
    (0x110B, 0x110C, 1), (0x110E, 0x1112, 1), (0x113C, 0x1140, 2), (0x114C, 0x1150, 2),
    (0x1154, 0x1155, 1), (0x1159, 0x1159, 1), (0x115F, 0x1161, 1), (0x1163, 0x1169, 2),
    (0x116D, 0x116E, 1), (0x1172, 0x1173, 1), (0x11AE, 0x11AF, 1), (0x11B7, 0x11B8, 1),
    (0x11BA, 0x11BA, 1), (0x11BC, 0x11C2, 1), (0x11F9, 0x11F9, 1), (0x1E00, 0x1E9B, 1),
    (0x1EA0, 0x1EF9, 1), (0x1F00, 0x1F15, 1), (0x1F18, 0x1F1D, 1), (0x1F20, 0x1F45, 1),
    (0x1F48, 0x1F4D, 1), (0x1F50, 0x1F57, 1), (0x1F5D, 0x1F5D, 1), (0x1F5F, 0x1F7D, 1),
    (0x1F80, 0x1FB4, 1), (0x1FB6, 0x1FBC, 1), (0x1FBE, 0x1FBE, 1), (0x1FC2, 0x1FC4, 1),
    (0x1FC6, 0x1FCC, 1), (0x1FD0, 0x1FD3, 1), (0x1FD6, 0x1FDB, 1), (0x1FE0, 0x1FEC, 1),
    (0x1FF2, 0x1FF4, 1), (0x1FF6, 0x1FFC, 1), (0x2126, 0x2126, 1), (0x212A, 0x212B, 1),
    (0x212E, 0x212E, 1), (0x2180, 0x2182, 1), (0x3007, 0x3007, 1), (0x3021, 0x3029, 1),
    (0x3041, 0x3094, 1), (0x30A1, 0x30FA, 1), (0x3105, 0x312C, 1), (0x4E00, 0x9FA5, 1),
    (0xAC00, 0xD7A3, 1),
)

NAME_REST = (
    (0x2D, 0x2E, 1), (0x30, 0x39, 1), (0xB7, 0xB7, 1), (0x2D0, 0x2D1, 1),
    (0x300, 0x345, 1), (0x360, 0x361, 1), (0x387, 0x387, 1), (0x483, 0x486, 1),
    (0x591, 0x5A1, 1), (0x5A3, 0x5B9, 1), (0x5BB, 0x5BD, 1), (0x5BF, 0x5BF, 1),
    (0x5C1, 0x5C2, 1), (0x64B, 0x652, 1), (0x660, 0x669, 1), (0x670, 0x670, 1),
    (0x6D6, 0x6DC, 1), (0x6DD, 0x6DF, 1), (0x6E0, 0x6E4, 1), (0x6E7, 0x6E8, 1),
    (0x6EA, 0x6ED, 1), (0x6F0, 0x6F9, 1), (0x901, 0x903, 1), (0x93C, 0x93C, 1),
    (0x93E, 0x94C, 1), (0x94D, 0x94D, 1), (0x951, 0x954, 1), (0x962, 0x963, 1),
    (0x966, 0x96F, 1), (0x981, 0x983, 1), (0x9BC, 0x9BC, 1), (0x9BE, 0x9BF, 1),
    (0x9C0, 0x9C4, 1), (0x9C7, 0x9C8, 1), (0x9CB, 0x9CD, 1), (0x9D7, 0x9D7, 1),
    (0x9E2, 0x9E3, 1), (0x9E6, 0x9EF, 1), (0xA3E, 0xA3F, 1), (0xA40, 0xA42, 1),
    (0xA47, 0xA48, 1), (0xA4B, 0xA4D, 1), (0xA66, 0xA6F, 1), (0xA70, 0xA71, 1),
    (0xA81, 0xA83, 1), (0xABC, 0xABC, 1), (0xABE, 0xAC5, 1), (0xAC7, 0xAC9, 1),
    (0xACB, 0xACD, 1), (0xAE6, 0xAEF, 1), (0xB01, 0xB03, 1), (0xB3C, 0xB3C, 1),
    (0xB3E, 0xB43, 1), (0xB47, 0xB48, 1), (0xB4B, 0xB4D, 1), (0xB56, 0xB57, 1),
    (0xB66, 0xB6F, 1), (0xB82, 0xB83, 1), (0xBBE, 0xBC2, 1), (0xBC6, 0xBC8, 1),
    (0xBCA, 0xBCD, 1), (0xBD7, 0xBD7, 1), (0xBE7, 0xBEF, 1), (0xC01, 0xC03, 1),
    (0xC3E, 0xC44, 1), (0xC46, 0xC48, 1), (0xC4A, 0xC4D, 1), (0xC55, 0xC56, 1),
    (0xC66, 0xC6F, 1), (0xC82, 0xC83, 1), (0xCBE, 0xCC4, 1), (0xCC6, 0xCC8, 1),
    (0xCCA, 0xCCD, 1), (0xCD5, 0xCD6, 1), (0xCE6, 0xCEF, 1), (0xD02, 0xD03, 1),
    (0xD3E, 0xD43, 1), (0xD46, 0xD48, 1), (0xD4A, 0xD4D, 1), (0xD57, 0xD57, 1),
    (0xD66, 0xD6F, 1), (0xE31, 0xE31, 1), (0xE34, 0xE3A, 1), (0xE46, 0xE46, 1),
    (0xE47, 0xE4E, 1), (0xE50, 0xE59, 1), (0xEB1, 0xEB1, 1), (0xEB4, 0xEB9, 1),
    (0xEBB, 0xEBC, 1), (0xEC6, 0xEC6, 1), (0xEC8, 0xECD, 1), (0xED0, 0xED9, 1),
    (0xF18, 0xF19, 1), (0xF20, 0xF29, 1), (0xF35, 0xF39, 2), (0xF3E, 0xF3F, 1),
    (0xF71, 0xF84, 1), (0xF86, 0xF8B, 1), (0xF90, 0xF95, 1), (0xF97, 0xF97, 1),
    (0xF99, 0xFAD, 1), (0xFB1, 0xFB7, 1), (0xFB9, 0xFB9, 1), (0x20D0, 0x20DC, 1),
    (0x302A, 0x302F, 1), (0x3031, 0x3035, 1), (0x3099, 0x309A, 1), (0x309D, 0x309E, 1),
    (0x30FC, 0x30FE, 1),
)

MAX_SIZE = 1048576
MAX_DEPTH = 64
SEP = "\x1f"
XML_NS = "http://www.w3.org/XML/1998/namespace"
RULES = ("size", "encoding", "decl", "doctype", "pi", "char", "name", "ns",
         "dup-attr", "structure", "depth", "syntax")

CHAR_BAD = re.compile("[^\t\n\r -퟿-�\U00010000-\U0010ffff]")
DECL_START = re.compile(r"<\?xml(?=[ \t\r\n?])")
DECL_STRICT = re.compile(
    r"<\?xml[ \t\r\n]+version[ \t\r\n]*=[ \t\r\n]*(?:\"1\.0\"|'1\.0')"
    r"(?:[ \t\r\n]+encoding[ \t\r\n]*=[ \t\r\n]*(?:\"([A-Za-z][A-Za-z0-9._-]*)\"|'([A-Za-z][A-Za-z0-9._-]*)'))?"
    r"(?:[ \t\r\n]+standalone[ \t\r\n]*=[ \t\r\n]*(?:\"(?:yes|no)\"|'(?:yes|no)'))?"
    r"[ \t\r\n]*\?>"
)
MARKUP_CHARS = set("<>&\"'=/ \t\r\n!?[]")


class Refuse(Exception):
    def __init__(self, rule):
        Exception.__init__(self, rule)
        self.rule = rule


def in_table(table, code):
    for low, high, stride in table:
        if low <= code <= high and (code - low) % stride == 0:
            return True
    return False


def is_ncname(value):
    if not value or not in_table(NAME_START, ord(value[0])) or value[0] == ":":
        return False
    for ch in value:
        if ch == ":":
            return False
        code = ord(ch)
        if not in_table(NAME_START, code) and not in_table(NAME_REST, code):
            return False
    return True


def decode(raw):
    if len(raw) > MAX_SIZE:
        raise Refuse("size")
    try:
        if raw[:2] in (b"\xfe\xff", b"\xff\xfe"):
            return raw.decode("utf-16"), "utf-16"
        if raw[:2] in (b"<\x00", b"\x00<"):
            raise Refuse("encoding")
        if raw[:3] == b"\xef\xbb\xbf":
            raw = raw[3:]
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        raise Refuse("encoding")


def check_decl(text, kind):
    if not DECL_START.match(text):
        return
    match = DECL_STRICT.match(text)
    if not match:
        raise Refuse("decl")
    declared = match.group(1) or match.group(2)
    if declared is None:
        return
    declared = declared.upper()
    if (kind == "utf-8" and declared == "UTF-8") or (kind == "utf-16" and declared == "UTF-16"):
        return
    raise Refuse("encoding")


def tag_around(data, index):
    start = data.rfind(b"<", 0, index + 1)
    end = data.find(b">", index)
    if start < 0:
        return ""
    return data[start:end if end >= 0 else len(data)].decode("utf-8", "ignore")


def in_quotes(tag):
    quote = ""
    for ch in tag:
        if quote:
            if ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
    return quote != ""


def classify_error(err, index, text, state):
    code = err.code
    errors = expat.errors
    data = text.encode("utf-8")
    here = data[:index].decode("utf-8", "ignore")
    at = data[index:].decode("utf-8", "ignore")[:1]
    if code == errors.codes[errors.XML_ERROR_BAD_CHAR_REF]:
        return "char"
    if code == errors.codes[errors.XML_ERROR_MISPLACED_XML_PI]:
        return "decl"
    if at and re.match(r"<\?xml[ \t\r\n?]", data[index:index + 6].decode("utf-8", "ignore")):
        return "decl"
    if code in (errors.codes[errors.XML_ERROR_UNBOUND_PREFIX],
                errors.codes[errors.XML_ERROR_UNDECLARING_PREFIX],
                errors.codes[errors.XML_ERROR_RESERVED_PREFIX_XML],
                errors.codes[errors.XML_ERROR_RESERVED_PREFIX_XMLNS],
                errors.codes[errors.XML_ERROR_RESERVED_NAMESPACE_URI]):
        return "ns"
    if code == errors.codes[errors.XML_ERROR_DUPLICATE_ATTRIBUTE]:
        names = re.findall(r"[ \t\r\n](xmlns(?::[^ \t\r\n=]+)?)[ \t\r\n]*=", tag_around(data, index))
        if len(names) != len(set(names)):
            return "ns"
        return "dup-attr"
    if code in (errors.codes[errors.XML_ERROR_JUNK_AFTER_DOC_ELEMENT],
                errors.codes[errors.XML_ERROR_NO_ELEMENTS]):
        return "structure"
    tag = here[max(here.rfind("<"), 0):]
    open_tag = here.rfind("<") > here.rfind(">")
    if state["depth"] == 0 and not open_tag and at and at != "<" and at not in " \t\r\n":
        return "structure"
    if code in (errors.codes[errors.XML_ERROR_INVALID_TOKEN], errors.codes[errors.XML_ERROR_SYNTAX]) \
            and open_tag and not in_quotes(tag) and tag[1:2] not in ("!", "?"):
        stripped = here.rstrip(" \t\r\n")
        if here.endswith(":"):
            return "name"
        if at and at not in MARKUP_CHARS and not stripped.endswith("=") and stripped[-1:] not in "\"'":
            return "name"
    return "syntax"


def parse_tree(raw):
    text, kind = decode(raw)
    if text.startswith("﻿"):
        raise Refuse("structure")
    bad = CHAR_BAD.search(text)
    if bad:
        raise Refuse("char")
    check_decl(text, kind)
    state = {"depth": 0}
    stack = []
    result = []

    parser = expat.ParserCreate(encoding="utf-8", namespace_separator=SEP)
    parser.namespace_prefixes = True

    def split(raw_name):
        parts = raw_name.split(SEP)
        if len(parts) == 1:
            return "", parts[0], ""
        if len(parts) == 2:
            return parts[0], parts[1], ""
        return parts[0], parts[1], parts[2]

    def flush():
        if stack and stack[-1]["buffer"]:
            stack[-1]["content"].append("".join(stack[-1]["buffer"]))
            stack[-1]["buffer"] = []

    def on_start(name, attrs):
        if state["depth"] >= MAX_DEPTH:
            raise Refuse("depth")
        ns, local, prefix = split(name)
        for part in (local, prefix):
            if part and not is_ncname(part):
                raise Refuse("name")
        items = []
        for key, value in attrs.items():
            ans, alocal, aprefix = split(key)
            for part in (alocal, aprefix):
                if part and not is_ncname(part):
                    raise Refuse("name")
            items.append([ans, alocal, value])
        items.sort(key=lambda item: (item[0], item[1]))
        flush()
        node = {"ns": ns, "name": local, "attrs": items, "content": [], "buffer": []}
        if stack:
            stack[-1]["content"].append(node)
        else:
            result.append(node)
        stack.append(node)
        state["depth"] += 1

    def on_end(name):
        flush()
        stack.pop()
        state["depth"] -= 1

    def on_chars(data):
        if stack:
            stack[-1]["buffer"].append(data)

    def on_ns(prefix, uri):
        if prefix is not None and not is_ncname(prefix):
            raise Refuse("name")

    def on_pi(target, data):
        raise Refuse("pi")

    def on_doctype(*args):
        raise Refuse("doctype")

    parser.StartElementHandler = on_start
    parser.EndElementHandler = on_end
    parser.CharacterDataHandler = on_chars
    parser.StartNamespaceDeclHandler = on_ns
    parser.ProcessingInstructionHandler = on_pi
    parser.StartDoctypeDeclHandler = on_doctype
    try:
        parser.Parse(text.encode("utf-8"), True)
    except expat.ExpatError as err:
        raise Refuse(classify_error(err, parser.ErrorByteIndex, text, state))
    if len(result) != 1:
        raise Refuse("structure")
    return strip_buffers(result[0])


def strip_buffers(node):
    return {
        "ns": node["ns"],
        "name": node["name"],
        "attrs": node["attrs"],
        "content": [strip_buffers(item) if isinstance(item, dict) else item for item in node["content"]],
    }


def reference_read(raw):
    try:
        return {"ok": True, "tree": parse_tree(raw)}
    except Refuse as refusal:
        return {"ok": False, "rule": refusal.rule}
    except RecursionError:
        return {"ok": False, "rule": "depth"}


def verdict(result):
    return "accept" if result["ok"] else "refuse:" + result["rule"]


def load_body(case):
    if case.get("body_b64") is not None:
        return base64.b64decode(case["body_b64"])
    with open(os.path.join(ROOT, case["body_file"]), "rb") as handle:
        return handle.read()


def main():
    with open(CASES_FILE, encoding="utf-8") as handle:
        cases = json.load(handle)
    names = set()
    outputs = []
    failures = 0
    for case in cases:
        name = case["case"]
        if name in names:
            print("duplicate case name: " + name)
            return 1
        names.add(name)
        expect = case["expect"]
        if expect != "accept" and not (expect.startswith("refuse:") and expect[7:] in RULES):
            print("bad expectation for %s: %r" % (name, expect))
            return 1
        if (case.get("body_b64") is None) == (case.get("body_file") is None):
            print("case needs exactly one of body_b64 and body_file: " + name)
            return 1
        raw = load_body(case)
        result = reference_read(raw)
        if verdict(result) != expect:
            print("MISMATCH %s (%s): expected %s, reference %s" % (name, case["source"], expect, verdict(result)))
            failures += 1
        outputs.append((name, raw, result))
    if failures:
        print("%d cases disagree; nothing written" % failures)
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    for stale in os.listdir(OUT_DIR):
        if stale not in names:
            shutil.rmtree(os.path.join(OUT_DIR, stale))
    for name, raw, result in outputs:
        folder = os.path.join(OUT_DIR, name)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "body.xml"), "wb") as handle:
            handle.write(raw)
        with open(os.path.join(folder, "expected.json"), "w", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, indent=1, sort_keys=False) + "\n")
    accepted = sum(1 for _, _, result in outputs if result["ok"])
    print("wrote %d cases (%d accept, %d refuse)" % (len(outputs), accepted, len(outputs) - accepted))
    return 0


if __name__ == "__main__":
    sys.exit(main())
