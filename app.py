# app.py

import os
import importlib
from config import PARAMETERS_CONFIG
from audit_report import generate_audit_excel_report
import re


def extract_vet_name(transcript_file):
    """
    Extracts the vet's name from the transcript file name.

    Args:
        transcript_file (str): The name of the transcript file.

    Returns:
        str: Extracted vet name or 'Unknown' if parsing fails.
    """
    if not transcript_file:
        return "Unknown"

    # Split the file name into parts using underscores
    parts = transcript_file.split("_")

    # Vet's name appears after the timestamp (index 2 and 3 based on the example)
    if len(parts) > 4:  # Ensure the file name has enough parts
        first_name = parts[3]
        last_name = parts[4]
        return f"{first_name.title()} {last_name.title()}"  # Combine and title-case the name

    return "Unknown"

def main():
    # Path to the directory containing transcript files
    transcripts_dir = './data/transcription'

    # List to hold all transcripts and corresponding vet names
    transcripts = []
    vets = []

    # Read all transcript files from the directory
    for filename in os.listdir(transcripts_dir):
        if filename.endswith('.txt'):  # Assuming transcripts are stored as .txt files
            file_path = os.path.join(transcripts_dir, filename)
            with open(file_path, 'r') as file:
                transcript = file.read().strip()  # Read and strip whitespace
                transcripts.append(transcript)

                # Extract the doctor's name from the transcript
                doctor_name = extract_vet_name(filename)
                vets.append({'name': doctor_name, 'transcript_file': filename})

    # Initialize results lists
    all_scores = []  # Stores scores for all parameters
    all_subparameters = []  # Subparameters for all parameters
    all_subweights = []  # Subweights for all parameters

    # Iterate through all parameters defined in config.py
    for parameter in PARAMETERS_CONFIG["parameters"]:
        parameter_name = parameter["name"]

        if "(" in parameter_name or "," in parameter_name:
            parameter_name = re.sub(r"\(.*?\)", "", parameter_name)  # Remove text within parentheses
            parameter_name = parameter_name.replace(",", "")  # Remove commas

        # Existing normalization logic for class_name and module_name
        class_name = parameter_name.replace(" ", "").replace("&", "").replace("-", "").strip()
        module_name = f"module.{class_name.lower()}"  # Assuming each parameter is implemented in the 'module' folder

        try:
            # Dynamically import the module and class
            module = importlib.import_module(module_name)
            ParameterClass = getattr(module, class_name)

            # Initialize the parameter class and evaluate transcripts
            agent = ParameterClass()
            result = agent.evaluate_transcripts(transcripts)

            # Append scores, subparameters, and subweights to the respective lists
            all_scores.append(result["scores"])

            # Handle parameters without subparameters
            if "subparameters" in result:
                all_subparameters.append(result["subparameters"])
                all_subweights.append(result["subweights"])
            else:
                all_subparameters.append(None)  # No subparameters for this parameter
                all_subweights.append(None)

        except ModuleNotFoundError:
            print(f"Module '{module_name}' for parameter '{parameter_name}' not found. Skipping...")
        except AttributeError:
            print(f"Class '{class_name}' not found in module '{module_name}'. Skipping...")
        except Exception as e:
            print(f"Unexpected error while processing parameter '{parameter_name}': {e}")

    # Extract parameters and max scores from config
    parameters = [param["name"] for param in PARAMETERS_CONFIG["parameters"]]
    max_scores = [param["max_score"] for param in PARAMETERS_CONFIG["parameters"]]

    # Generate the audit report without normalizing scores
    generate_audit_excel_report(
        vets=vets,
        parameters=parameters,
        weights=max_scores,  # Pass max_scores as weights
        subparameters=all_subparameters,
        subweights=all_subweights,
        scores=all_scores  # Pass raw scores directly
    )

if __name__ == "__main__":
    main()