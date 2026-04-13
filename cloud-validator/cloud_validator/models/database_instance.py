#Defines a schema for a databse instance with cross-filed validation 
#To ensure that the user version of database is compatible with defined schema and 
#To ensure that if deletion protection is enabled, backup must also be enabled, which is a common best practice for database management.






from __future__ import annotations # Without it Python may not recognize the return type hint "DatabaseInstance" in the validate_databse method, as the class is not fully defined at that point  

from typing import Literal #Restricts value to specific fixed options   

from pydantic import BaseModel, Field, field_validator, model_validator #BaseModel-> main class for validation,Field-> add filed level rules like min-max, filed_validator->for validating individual fileds, model_validator-> for validating entire object    

from cloud_validator.constants import ALLOWED_DATABASE_ENGINE_VERSIONS, VALID_REGIONS #Get predefined allowed values


class DatabaseInstance(BaseModel): #Inherit from BaseModel to create a Pydantic model
    """DatabaseInstance model with cross-field model validation."""

    type: Literal["DatabaseInstance"] = "DatabaseInstance" #Only allows this value to ensue that when object is created, it always of this type.   
    name: str = Field(..., min_length=1, max_length=100) #str must be string, and other required conditions      
    region: Literal[VALID_REGIONS[0], VALID_REGIONS[1], VALID_REGIONS[2], VALID_REGIONS[3]] #only allows values from valid regions region is field validator    
    engine: Literal["postgres", "mysql", "mariadb"] #Only these DB engines are allowed engine is field validator to ensure that only these values are accepted for engine type
    engine_version: str = Field(..., min_length=1) #version must be non- empy string 
    storage_gb: int = Field(..., gt=0) #... must be non-empty, gt=0 means greater than 0, so storage must be positive integer 
    backup_enabled: bool #True or False, indicates whether automatic backups are enabled for the database instance, which is important for data recovery and protection.
    deletion_protection: bool #True or False, if True, it prevents accidental deletion of the database instance, which is a critical safety feature for production databases. 

    @field_validator("name", "engine_version") #Apply further validation to name and engine_version fields  
    @classmethod #method is bound to class not object  
    def validate_non_blank_text(cls, value: str, info) -> str:  #cls-> class reference, value-> of the filed being validated, info-> metadata about the field such as its type or name 
        if not value.strip(): # to check if it is empty and contains only whitespace    
            raise ValueError(f"{info.field_name} cannot be empty or whitespace only")
        return value

    @model_validator(mode="after") #Runs after all fileds are validated   
    def validate_database_configuration(self) -> "DatabaseInstance": #Validates the overall db_instance to ensure engine version is compatible with type and deletion protection is not enabled without backup
        valid_versions = ALLOWED_DATABASE_ENGINE_VERSIONS.get(self.engine, ()) #imported from constants.py, .get method used to retrieve valid versions for specified engine 
        if self.engine_version not in valid_versions:
            raise ValueError(
                f"engine_version '{self.engine_version}' is not supported for engine "
                f"'{self.engine}'. Valid versions: {', '.join(valid_versions)}"
            )
        if self.deletion_protection and not self. backup_enabled: #Cross-field validation to ensure that if deletion protection is enabled, backup must also be enabled
            raise ValueError(
                "backup_enabled must be true when deletion_protection is enabled"
            )
        return self #if above condition fulfilled, object is returned   
