import os
from pathlib import Path
from xml.etree import ElementTree as ET

from .writer import write_unattend


SYSPREP_PATH = Path(os.environ["WINDIR"]) / "System32" / "Sysprep"
_COMPONENT_ATTRS = {"publicKeyToken": "31bf3856ad364e35", "language": "neutral", "versionScope": "nonSxS"}


def _architecture(context):
    return "amd64" if "64" in str(context.arch).lower() else "x86"


def _component(parent, name, architecture):
    return ET.SubElement(parent, "component", dict(_COMPONENT_ATTRS, name=name, processorArchitecture=architecture))


def _text(parent, tag, value):
    node = ET.SubElement(parent, tag)
    node.text = str(value)
    return node


def _add_local_account(shell, config):
    accounts = ET.SubElement(shell, "UserAccounts")
    local_accounts = ET.SubElement(accounts, "LocalAccounts")
    account = ET.SubElement(local_accounts, "LocalAccount", {"wcm:action": "add"})
    password = ET.SubElement(account, "Password")
    _text(password, "Value", config.admin_password)
    _text(password, "PlainText", "true")
    _text(account, "DisplayName", config.admin_username)
    _text(account, "Group", "Administrators")
    _text(account, "Name", config.admin_username)
    if config.auto_logon:
        auto_logon = ET.SubElement(shell, "AutoLogon")
        auto_password = ET.SubElement(auto_logon, "Password")
        _text(auto_password, "Value", config.admin_password)
        _text(auto_password, "PlainText", "true")
        _text(auto_logon, "Enabled", "true")
        _text(auto_logon, "LogonCount", config.auto_logon_count)
        _text(auto_logon, "Username", config.admin_username)


def _indent(element, level=0):
    padding = "\n" + "    " * level
    if len(element):
        if not element.text or not element.text.strip():
            element.text = padding + "    "
        for child in element:
            _indent(child, level + 1)
        if not element[-1].tail or not element[-1].tail.strip():
            element[-1].tail = padding
    if level and (not element.tail or not element.tail.strip()):
        element.tail = padding


def create_xml(context, config):
    architecture = _architecture(context)
    root = ET.Element("unattend", {"xmlns:wcm": "http://schemas.microsoft.com/WMIConfig/2002/State", "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"})
    specialize = ET.SubElement(root, "settings", {"pass": "specialize"})
    specialize_shell = _component(specialize, "Microsoft-Windows-Shell-Setup", architecture)
    _text(specialize_shell, "ComputerName", config.computer_name)
    if config.owner:
        _text(specialize_shell, "RegisteredOwner", config.owner)
    if config.organization:
        _text(specialize_shell, "RegisteredOrganization", config.organization)
    oobe = ET.SubElement(root, "settings", {"pass": "oobeSystem"})
    international = _component(oobe, "Microsoft-Windows-International-Core", architecture)
    for tag, value in (("InputLocale", config.input_locale), ("SystemLocale", config.system_locale), ("UILanguage", config.ui_language), ("UserLocale", config.user_locale)):
        _text(international, tag, value)
    shell = _component(oobe, "Microsoft-Windows-Shell-Setup", architecture)
    options = ET.SubElement(shell, "OOBE")
    _text(options, "HideEULAPage", str(config.hide_eula).lower())
    _text(options, "HideWirelessSetupInOOBE", str(config.hide_wireless).lower())
    _text(options, "ProtectYourPC", config.protect_your_pc)
    if config.hide_online_accounts:
        _text(options, "HideOnlineAccountScreens", "true")
    if context.is_server and config.hide_local_account_screen:
        _text(options, "HideLocalAccountScreen", "true")
    _text(shell, "TimeZone", config.time_zone)
    if config.uses_local_account():
        _add_local_account(shell, config)
    _indent(root)
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding="unicode")


def generate(context, config):
    xml = create_xml(context, config)
    if config.test_only:
        safe_family = "".join(char if char.isalnum() else "-" for char in context.family).strip("-")
        target = Path.home() / "Desktop" / f"JY-Sysprep-{safe_family}-unattend.xml"
    else:
        target = SYSPREP_PATH / "unattend.xml"
    write_unattend(xml, target)
    return str(target)
