from __future__ import annotations

from cloud_validator.types import ValidationStatus
from cloud_validator.validator import validate_resources


def test_validate_resources_returns_pass_and_fail_results() -> None:
    config = {
        "resources": [
            {
                "type": "VirtualMachine",
                "name": "web-server-1",
                "region": "us-east-1",
                "instance_type": "t2.micro",
                "tags": {"env": "prod", "owner": "platform"},
                "ssh_key_name": "team-key",
            },
            {
                "type": "DatabaseInstance",
                "name": "bad-db",
                "region": "us-east-1",
                "engine": "postgres",
                "engine_version": "99",
                "storage_gb": 20,
                "backup_enabled": True,
                "deletion_protection": False,
            },
        ]
    }

    report = validate_resources(config)

    assert len(report) == 2
    assert report[0]["status"] == ValidationStatus.PASS.value
    assert report[1]["status"] == ValidationStatus.FAIL.value
    assert "Field 'model'" in report[1]["errors"][0]


def test_validate_resources_rejects_unknown_resource_type() -> None:
    config = {
        "resources": [
            {
                "type": "LoadBalancer",
                "name": "public-lb",
            }
        ]
    }

    report = validate_resources(config)

    assert report[0]["status"] == ValidationStatus.FAIL.value
    assert "unsupported resource type" in report[0]["errors"][0]
