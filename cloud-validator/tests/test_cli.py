from __future__ import annotations

import json

from cloud_validator.cli import build_summary, load_config, render_json_report, render_text_report
from cloud_validator.validator import validate_resources


def test_load_config_requires_resources_key(tmp_path) -> None:
    config_file = tmp_path / "invalid.json"
    config_file.write_text(json.dumps({"invalid": []}), encoding="utf-8")

    try:
        load_config(str(config_file))
    except ValueError as exc:
        assert "Top-level field 'resources' is required" in str(exc)
    else:
        raise AssertionError("Expected load_config to raise ValueError")


def test_render_text_report_contains_summary() -> None:
    report = [
        {
            "index": 1,
            "name": "web-server-1",
            "type": "VirtualMachine",
            "status": "PASS",
            "errors": [],
        }
    ]

    rendered = render_text_report(report)

    assert "Cloud Resource Validation Report" in rendered
    assert "Summary: 1 passed, 0 failed, 1 total" in rendered


def test_render_json_report_contains_results_and_summary() -> None:
    config = {
        "resources": [
            {
                "type": "VirtualMachine",
                "name": "web-server-1",
                "region": "us-east-1",
                "instance_type": "t2.micro",
                "tags": {"env": "prod", "owner": "platform"},
                "ssh_key_name": "team-key",
            }
        ]
    }

    report = validate_resources(config)
    payload = json.loads(render_json_report(report))

    assert payload["summary"] == build_summary(report)
    assert payload["results"][0]["status"] == "PASS"
