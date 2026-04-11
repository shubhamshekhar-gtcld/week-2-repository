"""Shared enums and typed structures used by the package."""
#this file defines shared data structures like typed dict and enumerations that are used across the cloud validation tool  
from __future__ import annotations #refer to classes even before they are defined 

from enum import Enum
from typing import TypedDict #a way to define dictionary types with specific keys and value types, it helps with type checking and code readability

#enum is a way to define a set of named constant values, in this case we define a ValidationStatus enum with two members PASS and FAIL, and a ResourceType enum with three members representing different types of cloud resources, it is better as it prevents typos and provides a clear set of allowed values for these concepts in the codebase, it also improves code readability and maintainability by giving meaningful names to these constant values
class ValidationStatus(str, Enum): #create enum where each member is a string 
    PASS = "PASS" #usage is ValidationStatus.PASS.value which will give the string "PASS"
    FAIL = "FAIL" #usage is ValidationStatus.FAIL.value which will give the string "FAIL"


class ResourceType(str, Enum):
    VIRTUAL_MACHINE = "VirtualMachine"   
    STORAGE_BUCKET = "StorageBucket"
    DATABASE_INSTANCE = "DatabaseInstance"

#typed dicts are a way to define the expected structure of dictionaries in Python, they allow us to specify the keys and their corresponding value types, which can help with type checking and code readability, in this case we define a ResourceConfig typed dict that has optional keys "type" and "name", both of which are strings, and a CloudConfig typed dict that has a required key "resources" which is a list of ResourceConfig dictionaries
class ResourceConfig(TypedDict, total=False): #argument total=FALSE means keys defined in this TypedDict are optional  
    type: str 
    name: str


class CloudConfig(TypedDict): #all fields in this typeddict are required by default      
    resources: list[ResourceConfig]
