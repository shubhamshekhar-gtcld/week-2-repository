#This file is responsible for the CLI, takes input from terminal, reads JSON FILE calls the validation logic, formats the output and return success or failure       



from __future__ import annotations #type hint flexibility  

import argparse #read command line arguments
import json #parse JSON files
import sys
from pathlib import Path #handle file path cleanly
from typing import Any #Type hint for flexible data structures

from .types import CloudConfig, ValidationStatus
from .validator import validate_resources #importing necessary funcions   

PASS_SYMBOL = "\u2713" #check mark symbol for pass status
FAIL_SYMBOL = "\u2717" #cross mark symbol for fail status
FALLBACK_PASS_SYMBOL = "[PASS]" #fallback text if terminal doesn't support pass symbol
FALLBACK_FAIL_SYMBOL = "[FAIL]" #fallback text if terminal doesn't support fail symbol


def parse_args() -> argparse.Namespace: #Namespace is a simple class used to store attributes, in this case the command line arguments, #argparse.Namespace is simple container object to store and provide access to the command-line-arguments  
    parser = argparse.ArgumentParser(description="Validate cloud resource JSON files") #argument parser object to handle command line arguments, it provides help messages and error handling 
    parser.add_argument("--file", required=True, help="Path to config JSON file") #user have to provide --file sample_config.json, argument is mandatory,help is description of the argument that will be shown when user runs the script with --help flag
    parser.add_argument(
        "--format", #optional argument to specify output format, user can choose between "text" and "json"
        choices=["text", "json"], #validate that the user input for --format is either "text" or "json"
        default="text", #if user doesn't provide --format, it will default to "text"
        help="Output format", #message displayed when user runs the script with --help flag, describing the purpose of the --format argument
    )
    return parser.parse_args() #parse the command line arguments and return them as a Namespace object, which can be accessed like args.file and args.format in the main function


def load_config(file_path: str) -> CloudConfig: #load the JSON configuration file, validate its structure, and return it as a CloudConfig dictionary
    path = Path(file_path) #convert the file path string into a Path object for easier file handling
    with path.open("r", encoding="utf-8") as handle: #open the file in read mode with UTF-8 encoding, ensuring that the file is properly closed after reading
        data = json.load(handle) #parse the JSON content of the file into a Python dictionary, if the file is not valid JSON, this will raise a json.JSONDecodeError

    if not isinstance(data, dict):
        raise ValueError("Top-level JSON document must be an object")
    if "resources" not in data: #resources is the expected top-level key in the JSON file, if it's missing, we raise a ValueError to indicate that the configuration is invalid
        raise ValueError("Top-level field 'resources' is required")
    if not isinstance(data["resources"], list): #the value associated with the "resources" key must be a list, if it's not, we raise a ValueError to indicate that the configuration is invalid, this ensures that the validation logic can iterate over the resources correctly 
        raise ValueError("Field 'resources' must be a list")

    return {"resources": data["resources"]} #this line constructs and returns a CloudConfig dictionary containing only the "resources" key and its associated list of resources, this ensures that the returned configuration is in the expected format for the validation logic to process, thus normalizing the data  


def build_summary(report: list[dict[str, Any]]) -> dict[str, int]: #function to count the no of passed and failed validations    
    passed = sum(1 for item in report if item["status"] == ValidationStatus.PASS.value)
    failed = len(report) - passed
    return {
        "total_resources": len(report),
        "passed": passed,
        "failed": failed,
    }


def get_status_prefix(status: str) -> str: #function to get the appropriate symbol based on validation status 
    preferred = PASS_SYMBOL if status == ValidationStatus.PASS.value else FAIL_SYMBOL
    fallback = (
        FALLBACK_PASS_SYMBOL
        if status == ValidationStatus.PASS.value
        else FALLBACK_FAIL_SYMBOL
    )

    encoding = sys.stdout.encoding or "utf-8" #determine the encoding of the terminal output, if it's not available, default to UTF-8
    try:
        preferred.encode(encoding)
        return preferred
    except UnicodeEncodeError:
        return fallback #use simple text if unicode fails


def render_text_report(report: list[dict[str, Any]]) -> str: #function to generate a human-readable text report based on the validation results, it includes symbols for pass/fail status and a summary of the results at the end
    lines = ["Cloud Resource Validation Report", "=" * 40] #create a header for the report with a title and a separator line
    for item in report:
        symbol = get_status_prefix(item["status"])
        lines.append(
            f"{symbol} {item['status']} {item['type']} '{item['name']}' "
            f"(resource #{item['index']})"
        )
        if item["status"] == ValidationStatus.FAIL.value:
            for error in item["errors"]:
                lines.append(f"  - {error}")

    summary = build_summary(report)
    lines.append("=" * 40)
    lines.append(
        "Summary: "
        f"{summary['passed']} passed, {summary['failed']} failed, "
        f"{summary['total_resources']} total"
    )
    return "\n".join(lines) #join the list of lines into a single string with newline characters separating each line, creating the final text report that can be printed to the terminal
 

def render_json_report(report: list[dict[str, Any]]) -> str: #convert raw validation results into a structured JSON format, including a summary of the results, which can be easily consumed by other tools or systems that expect JSON input, input is list of objects(dictionaries)   
    payload = {
        "summary": build_summary(report),
        "results": report,
    }
    return json.dumps(payload, indent=2) #json.dumps converts the Python dictionary into a JSON-formatted string, with an indentation of 2 spaces for better readability   


def main() -> int:
    args = parse_args() #parse the command line arguments to get the file path and output format specified by the user, then load the configuration, validate the resources, and generate the report based on the specified format. Finally, it returns an exit code of 0 for success or 1 for failure based on whether any validations failed.

    try:
        config = load_config(args.file) #script attempts to open the file & run the validation    
        report = validate_resources(config)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr) #sys.stderr sends the output msg to error stream instead of output stream os that error msgs on't get mixed with normal output, good development practice to be incorporated   
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in '{args.file}': {exc}", file=sys.stderr) #handles the case where the provided file is not valid JSON, it catches the json.JSONDecodeError and prints an error message to stderr, including the exception message for more details about what went wrong with the JSON parsing
        return 1 
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1 #handles other value errors that may occur during the loading and validation process, such as missing required fields or incorrect data types in the JSON configuration, it catches the ValueError and prints the error message to stderr before returning an exit code of 1 to indicate failure

    if args.format == "json": #checks what the user asked for in the --format argument in the cli    
        print(render_json_report(report))
    else:
        print(render_text_report(report))

    summary = build_summary(report)
    return 0 if summary["failed"] == 0 else 1 #returns an exit code of 0 if all validations passed  


if __name__ == "__main__": #ensures script only runs when executed directly, not when imported as a module, it calls the main function and exits with the appropriate exit code based on the validation results
    raise SystemExit(main())
