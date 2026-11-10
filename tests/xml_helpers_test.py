import pytest
from defusedxml import ElementTree as DefusedET

from src.utils.xml_helpers import (
    KEY_CFG_NAMESPACE,
    build_key_cfg_xml,
    parse_key_cfg_xml,
    parse_response_status_xml,
)


def test_parse_key_cfg_xml_flat_fields(sample_key_cfg_xml):
    fields = parse_key_cfg_xml(sample_key_cfg_xml)
    assert fields["id"] == "1"
    assert fields["callNumber"] == "61"
    assert fields["enableCallCenter"] == "false"
    assert fields["callMethod"] == "callNumber"


def test_parse_key_cfg_xml_empty_element_becomes_empty_string():
    xml_text = f'<KeyCfg xmlns="{KEY_CFG_NAMESPACE}"><callNumber/></KeyCfg>'
    fields = parse_key_cfg_xml(xml_text)
    assert fields["callNumber"] == ""


def test_parse_key_cfg_xml_malformed_raises():
    with pytest.raises(DefusedET.ParseError):
        parse_key_cfg_xml("<unclosed>")


def test_build_key_cfg_xml_roundtrip():
    original = {
        "id": "1",
        "callNumber": "3001",
        "enableCallCenter": "false",
        "callMethod": "callNumber",
    }
    body = build_key_cfg_xml(original)
    assert body.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert f'xmlns="{KEY_CFG_NAMESPACE}"' in body
    assert "<callNumber>3001</callNumber>" in body

    parsed = parse_key_cfg_xml(body)
    assert parsed == original


def test_build_key_cfg_xml_escapes_special_chars():
    body = build_key_cfg_xml({"callNumber": "<script>&amp;"})
    assert "&lt;script&gt;" in body
    assert "&amp;amp;" in body


def test_build_key_cfg_xml_coerces_none_to_empty():
    body = build_key_cfg_xml({"callNumber": None})
    assert "<callNumber />" in body or "<callNumber></callNumber>" in body


def test_parse_response_status_xml(sample_ok_status_xml):
    status = parse_response_status_xml(sample_ok_status_xml)
    assert status["statusCode"] == "1"
    assert status["statusString"] == "OK"
    assert status["subStatusCode"] == "ok"
