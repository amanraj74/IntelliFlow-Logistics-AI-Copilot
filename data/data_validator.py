import json
import os
import pandas as pd
from typing import Dict, List, Any, Optional, Union
import jsonschema


class DataValidator:
    """Validates data against JSON schemas for the logistics system."""
    
    def __init__(self, schemas_dir: str = "data/schemas"):
        """Initialize the validator with schema directory.
        
        Args:
            schemas_dir: Directory containing JSON schema files
        """
        self.schemas_dir = schemas_dir
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self) -> None:
        """Load all JSON schemas from the schemas directory."""
        schema_files = [
            f for f in os.listdir(self.schemas_dir) 
            if f.endswith("_schema.json")
        ]
        
        for schema_file in schema_files:
            entity_type = schema_file.replace("_schema.json", "")
            schema_path = os.path.join(self.schemas_dir, schema_file)
            
            try:
                with open(schema_path, "r") as f:
                    self.schemas[entity_type] = json.load(f)
                print(f"Loaded schema for {entity_type}")
            except Exception as e:
                print(f"Error loading schema {schema_file}: {str(e)}")
    
    def validate_record(self, record: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """Validate a single record against its schema.
        
        Args:
            record: The record to validate
            entity_type: Type of entity (driver, incident, alert)
            
        Returns:
            Dict with validation result and errors if any
        """
        if entity_type not in self.schemas:
            return {"valid": False, "errors": [f"No schema found for {entity_type}"]}
        
        try:
            jsonschema.validate(instance=record, schema=self.schemas[entity_type])
            return {"valid": True, "errors": []}
        except jsonschema.exceptions.ValidationError as e:
            return {"valid": False, "errors": [str(e)]}
    
    def validate_dataframe(self, df: pd.DataFrame, entity_type: str) -> Dict[str, Any]:
        """Validate all records in a pandas DataFrame.
        
        Args:
            df: DataFrame containing records
            entity_type: Type of entity (driver, incident, alert)
            
        Returns:
            Dict with validation results and error details
        """
        if entity_type not in self.schemas:
            return {"valid": False, "errors": [f"No schema found for {entity_type}"]}
        
        records = df.to_dict(orient="records")
        all_valid = True
        errors = []
        
        for i, record in enumerate(records):
            result = self.validate_record(record, entity_type)
            if not result["valid"]:
                all_valid = False
                for error in result["errors"]:
                    errors.append(f"Row {i}: {error}")
        
        return {"valid": all_valid, "errors": errors}
    
    def validate_csv_file(self, file_path: str, entity_type: str) -> Dict[str, Any]:
        """Validate a CSV file against its schema.
        
        Args:
            file_path: Path to the CSV file
            entity_type: Type of entity (driver, incident, alert)
            
        Returns:
            Dict with validation results and error details
        """
        try:
            df = pd.read_csv(file_path)
            return self.validate_dataframe(df, entity_type)
        except Exception as e:
            return {"valid": False, "errors": [f"Error reading CSV file: {str(e)}"]}
    
    def validate_json_file(self, file_path: str, entity_type: str) -> Dict[str, Any]:
        """Validate a JSON file against its schema.
        
        Args:
            file_path: Path to the JSON file
            entity_type: Type of entity (driver, incident, alert)
            
        Returns:
            Dict with validation results and error details
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
            if isinstance(data, list):
                all_valid = True
                errors = []
                
                for i, record in enumerate(data):
                    result = self.validate_record(record, entity_type)
                    if not result["valid"]:
                        all_valid = False
                        for error in result["errors"]:
                            errors.append(f"Item {i}: {error}")
                
                return {"valid": all_valid, "errors": errors}
            else:
                return self.validate_record(data, entity_type)
                
        except Exception as e:
            return {"valid": False, "errors": [f"Error reading JSON file: {str(e)}"]}


def validate_data_directory(directory: str, entity_type: str) -> Dict[str, Any]:
    """Validate all data files in a directory.
    
    Args:
        directory: Directory containing data files
        entity_type: Type of entity (driver, incident, alert)
        
    Returns:
        Dict with validation results and error details
    """
    validator = DataValidator()
    
    if not os.path.exists(directory):
        return {"valid": False, "errors": [f"Directory not found: {directory}"]}
    
    files = [f for f in os.listdir(directory) if f.endswith(".csv") or f.endswith(".json")]
    
    if not files:
        return {"valid": True, "errors": [f"No CSV or JSON files found in {directory}"]}
    
    all_valid = True
    all_errors = []
    
    for file in files:
        file_path = os.path.join(directory, file)
        
        if file.endswith(".csv"):
            result = validator.validate_csv_file(file_path, entity_type)
        else:  # JSON file
            result = validator.validate_json_file(file_path, entity_type)
        
        if not result["valid"]:
            all_valid = False
            all_errors.extend([f"File {file}: {error}" for error in result["errors"]])
    
    return {"valid": all_valid, "errors": all_errors}


if __name__ == "__main__":
    # Example usage
    validator = DataValidator()
    
    # Validate driver data
    driver_result = validator.validate_csv_file("data/streams/drivers/drivers.csv", "driver")
    print(f"Driver validation: {driver_result['valid']}")
    if not driver_result['valid']:
        print("\n".join(driver_result['errors']))
    
    # Validate incident data
    incident_result = validator.validate_csv_file("data/streams/incidents/incidents.csv", "incident")
    print(f"Incident validation: {incident_result['valid']}")
    if not incident_result['valid']:
        print("\n".join(incident_result['errors']))