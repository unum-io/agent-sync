"""Tests for minimal YAML parser."""

from agent_sync.parser import parse_yaml


def test_parse_manifest_instructions():
    text = """
instructions:
  - name: general
    file: instructions/general.md
    description: "Core directives"
    always_apply: true

  - name: python
    file: instructions/python.md
    description: "Python"
    globs: "**/*.py"
"""
    data = parse_yaml(text)
    assert len(data["instructions"]) == 2
    assert data["instructions"][0]["name"] == "general"
    assert data["instructions"][0]["always_apply"] is True
    assert data["instructions"][1]["globs"] == "**/*.py"


def test_parse_inline_framework_list():
    text = "frameworks: [copilot, cursor, claude]\n"
    data = parse_yaml(text)
    assert data["frameworks"] == ["copilot", "cursor", "claude"]


def test_parse_scalar_config():
    text = 'project_name: MyProject\n'
    data = parse_yaml(text)
    assert data["project_name"] == "MyProject"
