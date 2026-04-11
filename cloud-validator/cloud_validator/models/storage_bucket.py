#Defines rules for validating a storage bucket configuration    


from __future__ import annotations #allow type hints to refer to the class being defined even when the calss is not fully defined  

from typing import Literal #Restricts value to specific fixed options 

from pydantic import BaseModel, Field, field_validator #BaseModel-> main class for validation,Field-> add filed level rules like min-max, filed_validator->for validating individual fileds 

from cloud_validator.constants import VALID_REGIONS #cross-imported this function    


class StorageBucket(BaseModel):
    """StorageBucket model with field-level constraints."""

    type: Literal["StorageBucket"] = "StorageBucket" #Only allows this value to ensure that when object is created, it always of this type 
    name: str = Field(..., min_length=1, max_length=63) #non empty string with length between 1 & 63 chars 
    region: Literal[VALID_REGIONS[0], VALID_REGIONS[1], VALID_REGIONS[2], VALID_REGIONS[3]] #Only allows values from valid regions 
    versioning_enabled: bool #Indicates whether versioning is enabled for the storage bucket 
    public_access_blocked: bool #Indicates whether public access is blocked for the storage bucket 
    size_gb: int = Field(..., gt=0) #Size of the storage bucket in gigabytes, must be a positive integer 

    @field_validator("name") #further validation to ensure name is not empty or whitespace only, and follows naming conventions (lowercase letters, numbers, hyphens only, cannot start or end with hyphen) 
    @classmethod
    def validate_bucket_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name cannot be empty or whitespace only")
        if "_" in value or any(char.isupper() for char in value):
            raise ValueError("name must use lowercase letters, numbers, and hyphens only")
        if value.startswith("-") or value.endswith("-"):
            raise ValueError("name cannot start or end with a hyphen")
        return value #Returns the validated value if all checks are passed 
