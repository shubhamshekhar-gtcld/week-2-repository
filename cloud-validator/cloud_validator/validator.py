"""Validation workflow for mixed cloud resource configuration files."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError #to handle validation errors from pydantic models

from .models import DatabaseInstance, StorageBucket, VirtualMachine
from .types import CloudConfig, ResourceType, ValidationStatus

RESOURCE_MODELS = { #import structure and enums from types.py  
    ResourceType.VIRTUAL_MACHINE.value: VirtualMachine, #dictionary mapping resource type string to their model class, used instead of if else for more cleaner, scalable, extensible code for eg if we are given a resource type which model should validate it, eg resource_type="VirtualMachine" model_cls = RESOURCE_MODELS[resource_type], model_cls = VirtualMachine   
    ResourceType.STORAGE_BUCKET.value: StorageBucket,
    ResourceType.DATABASE_INSTANCE.value: DatabaseInstance,
}


def _format_pydantic_errors(exc: ValidationError) -> list[str]: #converts complex pydantic error to human readable errors, ValidationError is exception raised by pydantic model when validation fails    
    errors: list[str] = [] #empty list to store formatted error msgs 
    for error in exc.errors(include_url=False): #exc.errors() returns list of error dicts, include_url = false to exclude error type URLS from output 
        location = error.get("loc", ()) #to extract which field caused the error 
        field = ".".join(str(item) for item in location) if location else "model" #convert location tuple to string for eg "field1.field2" or "model" if location is empty
        message = error.get("msg", "Validation error")
        errors.append(f"Field '{field}': {message}")
    return errors


def validate_resources(config: CloudConfig) -> list[dict[str, Any]]: #main function to validate resources defined in the cloud config, it iterates through each resource, checks if the type is supported, validates against the corresponding pydantic model, and compiles a report of validation results 
    report: list[dict[str, Any]] = []

    for index, resource_data in enumerate(config["resources"], start=1): #enumerate to get both index and resource data, start=1 to make index 1 based for better readability in reports
        resource_type = resource_data.get("type")
        resource_name = resource_data.get("name") or f"resource-{index}" #if name is not provided, use a default name based on index for better error reporting and identification in the report 

        if resource_type not in RESOURCE_MODELS:
            report.append(
                {
                    "index": index,
                    "name": resource_name,
                    "type": resource_type or "unknown",
                    "status": ValidationStatus.FAIL.value,
                    "errors": [
                        "Field 'type': unsupported resource type. "
                        f"Expected one of: {', '.join(RESOURCE_MODELS)}"
                    ],
                }
            )
            continue

        model_cls = RESOURCE_MODELS[resource_type]
        try:
            model_cls.model_validate(resource_data) #validate the resource data against the corresponding pydantic model, if validation fails it will raise a ValidationError which we catch to format and include in the report
            report.append(
                {
                    "index": index,
                    "name": resource_name,
                    "type": resource_type,
                    "status": ValidationStatus.PASS.value,
                    "errors": [],
                }
            )
        except ValidationError as exc:
            report.append(
                {
                    "index": index,
                    "name": resource_name,
                    "type": resource_type,
                    "status": ValidationStatus.FAIL.value,
                    "errors": _format_pydantic_errors(exc),
                }
            )

    return report
