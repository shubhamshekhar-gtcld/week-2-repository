"""Cloud infrastructure configuration validator package."""

#defines the public API of the cloud_validator package, making it easier for users to import the necessary components without needing to know the internal structure of the package. By importing the models and validation function here, users can simply import from cloud_validator instead of having to navigate through submodules.

from .models import DatabaseInstance, StorageBucket, VirtualMachine #re-exports the models for easier imports in other modules
from .validator import validate_resources #re-exports the validate_resources function for easier imports in other modules

__all__ = [
    "DatabaseInstance",
    "StorageBucket",
    "VirtualMachine",
    "validate_resources",
] #defines the scope of what is available when users import from cloud_validator, part of good development practice to control the public API and prevent unintended usage of internal components 
