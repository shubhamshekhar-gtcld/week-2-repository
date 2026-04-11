"""Shared constants for cloud resource validation."""
#defines constants for cloud validation tool  
from __future__ import annotations #refer to classes even before they are defined 

from typing import Final #final is used to indicate that a variable is constant and should not be reassigned, it helps with type checking and code readability

VALID_REGIONS: Final[tuple[str, ...]] = ( #the ... means that tuple can contain any no of strings   
    "us-east-1",
    "us-west-2",
    "eu-west-1",
    "ap-south-1",
)

TAG_KEY_PATTERN: Final[str] = r"^[A-Za-z0-9][A-Za-z0-9_.-]*$"

MANDATORY_TAG_KEYS: Final[tuple[str, ...]] = (
    "env",
    "owner",
)

ALLOWED_DATABASE_ENGINE_VERSIONS: Final[dict[str, tuple[str, ...]]] = { #dict where key is string and value is tuple of strings   
    "postgres": ("13", "14", "15", "16"),
    "mysql": ("5.7", "8.0", "8.4"),
    "mariadb": ("10.5", "10.6", "11.0"),
}

VALID_VM_INSTANCE_TYPES: Final[tuple[str, ...]] = ( #... means tuple can contain any no of strings  
    "t2.micro",
    "t2.small",
    "t2.medium",
    "m5.large",
)
