from __future__ import annotations

import pytest
from pydantic import ValidationError

from cloud_validator.models import DatabaseInstance, StorageBucket, VirtualMachine


def test_virtual_machine_valid_model() -> None:
    vm = VirtualMachine(
        name="web-server-1",
        region="us-east-1",
        instance_type="t2.micro",
        tags={"env": "prod", "owner": "platform"},
        ssh_key_name="team-key",
    )

    assert vm.name == "web-server-1"


def test_virtual_machine_rejects_missing_required_tag() -> None:
    with pytest.raises(ValidationError) as exc_info:
        VirtualMachine(
            name="web-server-1",
            region="us-east-1",
            instance_type="t2.micro",
            tags={"env": "prod"},
            ssh_key_name="team-key",
        )

    assert "tags is missing mandatory keys: owner" in str(exc_info.value)


def test_storage_bucket_rejects_invalid_name() -> None:
    with pytest.raises(ValidationError) as exc_info:
        StorageBucket(
            name="Invalid_Bucket",
            region="us-west-2",
            versioning_enabled=True,
            public_access_blocked=True,
            size_gb=100,
        )

    assert "name must use lowercase letters, numbers, and hyphens only" in str(
        exc_info.value
    )


def test_database_instance_rejects_invalid_engine_version() -> None:
    with pytest.raises(ValidationError) as exc_info:
        DatabaseInstance(
            name="orders-db",
            region="eu-west-1",
            engine="postgres",
            engine_version="99",
            storage_gb=100,
            backup_enabled=True,
            deletion_protection=False,
        )

    assert "engine_version '99' is not supported for engine 'postgres'" in str(
        exc_info.value
    )


def test_database_instance_requires_backup_when_deletion_protection_enabled() -> None:
    with pytest.raises(ValidationError) as exc_info:
        DatabaseInstance(
            name="orders-db",
            region="eu-west-1",
            engine="mysql",
            engine_version="8.0",
            storage_gb=100,
            backup_enabled=False,
            deletion_protection=True,
        )

    assert "backup_enabled must be true when deletion_protection is enabled" in str(
        exc_info.value
    )
