# stdlib ElementTree is used only for building outgoing XML (Element/SubElement/tostring),
# which is not a parsing vector. All parsing of untrusted device responses goes through defusedxml.
from xml.etree import ElementTree as ET  # nosec B405

from defusedxml import ElementTree as DefusedET

KEY_CFG_NAMESPACE = "http://www.isapi.org/ver20/XMLSchema"
KEY_CFG_VERSION = "2.0"


def parse_key_cfg_xml(xml_text: str) -> dict[str, str]:
    # Assumes the keyCfg schema is a single level of leaf elements under <KeyCfg>.
    # Nested sub-elements would be silently flattened to empty strings.
    root = DefusedET.fromstring(xml_text)
    fields: dict[str, str] = {}
    for child in root:
        tag = child.tag.split("}", 1)[-1]
        fields[tag] = child.text if child.text is not None else ""
    return fields


def build_key_cfg_xml(fields: dict[str, str]) -> str:
    ET.register_namespace("", KEY_CFG_NAMESPACE)
    root = ET.Element(
        f"{{{KEY_CFG_NAMESPACE}}}KeyCfg",
        attrib={"version": KEY_CFG_VERSION},
    )
    for tag, value in fields.items():
        element = ET.SubElement(root, f"{{{KEY_CFG_NAMESPACE}}}{tag}")
        element.text = "" if value is None else str(value)

    body = ET.tostring(root, encoding="unicode")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{body}'


def parse_response_status_xml(xml_text: str) -> dict[str, str]:
    root = DefusedET.fromstring(xml_text)
    status: dict[str, str] = {}
    for child in root:
        tag = child.tag.split("}", 1)[-1]
        status[tag] = child.text if child.text is not None else ""
    return status
