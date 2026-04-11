#validates virtual machine configuration          


from __future__ import annotations #allowing for flexible type hints  

import re #importing regular expression module  
from typing import Literal #Restrict values to fixed options  

from pydantic import BaseModel, Field, field_validator

from cloud_validator.constants import (
    MANDATORY_TAG_KEYS,
    TAG_KEY_PATTERN,
    VALID_REGIONS,
    VALID_VM_INSTANCE_TYPES,
)  #importing constants for validation rules 


class VirtualMachine(BaseModel):
    """VirtualMachine model with field and tag validators."""

    type: Literal["VirtualMachine"] = "VirtualMachine" #Ensures that the type field always is of virtual machine type 
    name: str = Field(..., min_length=1, max_length=100)#Name of the virtual machine, must be a non-empty string with length between 1 and 100 characters
    region: Literal[VALID_REGIONS[0], VALID_REGIONS[1], VALID_REGIONS[2], VALID_REGIONS[3]]
    instance_type: Literal[
        VALID_VM_INSTANCE_TYPES[0], #only allows values from valid instance types  
        VALID_VM_INSTANCE_TYPES[1],
        VALID_VM_INSTANCE_TYPES[2],
        VALID_VM_INSTANCE_TYPES[3],
    ]
    tags: dict[str, str] = Field(...) #Tags for the virtual machine, must be a dictionary with string keys and values
    ssh_key_name: str = Field(..., min_length=1, max_length=100) #Name of the SSH key, must be a non-empty string with length between 1 and 100 characters  

    @field_validator("name", "ssh_key_name") #Apply further validation to name and ssh_key_name fields
    @classmethod #method is bound to class not object
    def validate_non_blank_text(cls, value: str, info) -> str: #cls-> class reference, value-> of the filed being validated, info-> metadata about the field such as its type or name
        if not value.strip(): # to check if it is empty and contains only whitespace
            raise ValueError(f"{info.field_name} cannot be empty or whitespace only")
        return value

    @field_validator("tags")
    @classmethod #in pydantic v2 field validators are defined as class methods, and the @classmethod decorator is used to indicate that the method is a class method   
    def validate_tags(cls, value: dict[str, str]) -> dict[str, str]:
        if not isinstance(value, dict):
            raise ValueError("tags must be a dictionary")

        missing_keys = [key for key in MANDATORY_TAG_KEYS if key not in value] #Check if all mandatory keys are present in the tags dictionary, if not, it creates a list of missing keys by iterating over the MANDATORY_TAG_KEYS and checking if each key is in the provided tags dictionary. If a key is missing, it is added to the missing_keys list.
        if missing_keys:
            raise ValueError(
                "tags is missing mandatory keys: " + ", ".join(missing_keys)
            ) #if required keys are missing error is raised   

        for key, tag_value in value.items():
            if not isinstance(key, str) or not isinstance(tag_value, str):
                raise ValueError("All tag keys and values must be strings")
            if not re.match(TAG_KEY_PATTERN, key): #matches the tag key against a predefined pattern   
                raise ValueError(
                    f"Tag key '{key}' is invalid. Must start with alphanumeric and contain only alphanumeric, _, ., -"
                )
            if not tag_value.strip():
                raise ValueError(f"Tag '{key}' must have a non-empty string value") #tag value should be non-empty          
            if len(key) > 128 or len(tag_value) > 256:
                raise ValueError(f"Tag key '{key}' or value exceeds length limits") #enforcing size limits in a key  

        return value
