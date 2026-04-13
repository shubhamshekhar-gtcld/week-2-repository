# Cloud Validator

`cloud_validator` validates cloud infrastructure configuration files before deployment. It is built with Pydantic v2, packaged with `pyproject.toml`, and exposes a `cloud-validate` CLI command.

## Supported Resources

- `VirtualMachine`
- `StorageBucket`
- `DatabaseInstance`

## Features

- Pydantic v2 `BaseModel`, `Field`, `@field_validator`, and `@model_validator`
- `Literal` constraints for regions and resource-specific choices
- Mixed resource validation from a top-level `resources` list
- Clear field-level error reporting in both text and JSON formats
- Importable package modules for direct Python use

## Installation

```bash
pip install -e .
```

For development and automated testing:

```bash
pip install -e ".[dev]"
```

## Import Example

```python
from cloud_validator.models import VirtualMachine

vm = VirtualMachine(
    name="web-server-1",
    region="us-east-1",
    instance_type="t2.micro",
    tags={"env": "prod", "owner": "platform"},
    ssh_key_name="team-key",
)

print(vm.model_dump())
```

## CLI Usage

Text output:

```bash
./venv/Scripts/activate

```bash
cloud-validate --file sample_config.json --format text
```

JSON output:

```bash
cloud-validate --file sample_config.json --format json
```

Run the automated test suite:

```bash
python -m pytest
```

## Input Format

```json
{
  "resources": [
    {
      "type": "VirtualMachine",
      "name": "web-server-1",
      "region": "us-east-1",
      "instance_type": "t2.micro",
      "tags": {
        "env": "prod",
        "owner": "platform"
      },
      "ssh_key_name": "team-key"
    }
  ]
}
```

## Example Output

```text
Cloud Resource Validation Report
========================================
[PASS] PASS VirtualMachine 'web-server-1' (resource #1)
[FAIL] FAIL DatabaseInstance 'bad-db' (resource #6)
  - Field 'model': Value error, engine_version '99' is not supported for engine 'postgres'. Valid versions: 13, 14, 15, 16
========================================
Summary: 3 passed, 5 failed, 8 total
```

## Validation Rules

- `region` must be one of the supported cloud regions
- `tags` must be `dict[str, str]`
- Virtual machine tags must include `env` and `owner`
- Tag keys must follow a safe naming pattern
- Storage values must be greater than zero
- Database `engine_version` must match the selected `engine`
- `backup_enabled` must be `true` when `deletion_protection` is enabled

## Test Coverage

- `tests/test_models.py` checks model-level validation rules for all three resource types
- `tests/test_validator.py` checks mixed-resource validation and unknown resource handling
- `tests/test_cli.py` checks config loading and report rendering
- `pytest.ini` keeps test discovery consistent for evaluators

## Project Structure

```text
cloud_validator/
|-- __init__.py
|-- cli.py
|-- constants.py
|-- types.py
|-- validator.py
|-- tests/
|   |-- test_models.py
|   |-- test_validator.py
|   `-- test_cli.py
|-- pytest.ini
`-- models/
    |-- __init__.py
    |-- virtual_machine.py
    |-- storage_bucket.py
    `-- database_instance.py
```
