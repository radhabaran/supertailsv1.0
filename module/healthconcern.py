# healthconcern.py

import os
import re
import json
import importlib.util
from langchain_anthropic import ChatAnthropic  # Import the Anthropic model
from dotenv import load_dotenv  # For loading environment variables

# Load environment variables
load_dotenv()

# Set Anthropic API key
anthro_api_key = os.environ.get("ANTHRO_KEY")
os.environ["ANTHROPIC_API_KEY"] = anthro_api_key

# Dynamically load the PARAMETERS_CONFIG from `config.py`
CONFIG_PATH = "config.py"
spec = importlib.util.spec_from_file_location("config", CONFIG_PATH)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
PARAMETERS_CONFIG = config.PARAMETERS_CONFIG


class HealthConcern:
    def __init__(self, model_name="claude-3-5-haiku-20241022"):
        """
        Initialize the HealthConcern class by dynamically loading subparameter details from config.py.
        """
        self.parameter_name = "Health Concern"
        self.max_score = self.get_max_score(self.parameter_name)
        self.subparameters = self.get_subparameters(self.parameter_name)

        # Initialize the Anthropic LLM
        self.llm = ChatAnthropic(model=model_name, temperature=0)

    def get_max_score(self, parameter_name):
        """
        Retrieve the maximum score for a given parameter from PARAMETERS_CONFIG.

        Args:
            parameter_name (str): The name of the parameter.

        Returns:
            int: The maximum score for the parameter.
        """
        for parameter in PARAMETERS_CONFIG["parameters"]:
            if parameter["name"] == parameter_name:
                return parameter["max_score"]
        return 0

    def get_subparameters(self, parameter_name):
        """
        Retrieve the subparameters and their weights for a given parameter from PARAMETERS_CONFIG.

        Args:
            parameter_name (str): The name of the parameter.

        Returns:
            list[dict]: List of subparameters with their weights.
        """
        for parameter in PARAMETERS_CONFIG["parameters"]:
            if parameter["name"] == parameter_name:
                return parameter.get("subparameters", [])
        return []

    def evaluate_transcripts(self, transcripts):
        """
        Evaluate the transcripts for health concerns.

        Args:
            transcripts (list[str]): List of transcript strings.

        Returns:
            dict: Evaluation results containing scores, subparameters, and subweights.
        """
        scores = []
        subparameters = []
        subweights = []

        # Extract subparameter details
        for subparam in self.subparameters:
            subparameters.append(subparam["name"])
            subweights.append(subparam["weight"])

        for transcript in transcripts:
            # Step 1: Use regex to detect vet's questions
            vet_questions = self.detect_vet_questions(transcript)

            # Step 2: Use LLM to classify user's description
            user_description_classification = self.detect_user_description_using_llm(transcript)

            # Step 3: Grade the response
            vet_score = self.grade_vet_questions(vet_questions)
            user_score = self.grade_user_description(user_description_classification)

            # Append the total score for this transcript
            total_score = vet_score + user_score
            # scores.append({"score": total_score})
            scores.append({
                "score": total_score,
                "subscores": [vet_score, user_score]  # Subparameter-specific scores
            })

        # Return results
        return {
            "scores": scores,
            "subparameters": subparameters,
            "subweights": subweights,
        }

    def detect_vet_questions(self, transcript):
        """
        Use regex to detect vet's health-related questions in the transcript.

        Args:
            transcript (str): The transcript text.

        Returns:
            list[str]: List of detected vet's health-related questions.
        """
        pattern = r"(?i)\b(health concerns|any other concerns|skin infection|cough|itching|rash|diet|weight)\b"
        return re.findall(pattern, transcript)

    import re
    import json

    def detect_user_description_using_llm(self, transcript):
        """
        Use LLM to classify the user's description of health concerns.

        Args:
            transcript (str): The transcript text.

        Returns:
            str: Classification of user's health concern description.
        """
        # Prompt for the LLM
        prompt = f"""
        Analyze the following transcript and classify the user's description of health concerns into one of three categories:
           - "Full Description": The user explicitly describes a health concern in detail.
           - "Partial Description": The user mentions a health concern briefly or indirectly.
           - "No Description": The user does not describe any health concern.

        Transcript: {transcript}

        Return the result as a JSON string in the following format:
        {{
            "user_description_classification": "Full Description" | "Partial Description" | "No Description"
        }}
        """

        try:
            # Call the Anthropic LLM using `invoke`
            response = self.llm.invoke(prompt)

            # Extract the content of the response
            response_content = response.content  # Extract the actual text response
            print("*" * 100)
            print("\nLLM response on User's description of health concern :", response_content)

            # Use regex to extract the JSON block from the response
            json_match = re.search(r"{.*?}", response_content, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in the response")

            # Parse the extracted JSON
            json_str = json_match.group(0)
            parsed_response = json.loads(json_str)

            # Extract the classification
            return parsed_response.get("user_description_classification", "No Description")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM response: {e}")
            print(f"LLM Response: {response_content}")
            return "No Description"
        except ValueError as e:
            print(f"Error extracting JSON: {e}")
            print(f"LLM Response: {response_content}")
            return "No Description"
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "No Description"

    def grade_vet_questions(self, vet_questions):
        """
        Grade the vet's questions about health concerns.

        Args:
            vet_questions (list[str]): List of vet's health-related questions.

        Returns:
            int: Score for vet's questions.
        """
        vet_weight = next((sub["weight"] for sub in self.subparameters if sub["name"] == "Vet's questions about health concern"), 0)
        if len(vet_questions) >= 3:
            return vet_weight  # Full score
        elif len(vet_questions) > 0:
            return vet_weight / 2  # Partial score
        return 0  # No questions

    def grade_user_description(self, user_description_classification):
        """
        Grade the user's description of health concerns.

        Args:
            user_description_classification (str): Classification of the user's health concern description.

        Returns:
            int: Score based on the classification.
        """
        user_weight = next((sub["weight"] for sub in self.subparameters if sub["name"] == "User's description of health concern"), 0)
        if user_description_classification == "Full Description":
            return user_weight  # Full score
        elif user_description_classification == "Partial Description":
            return user_weight / 2  # Partial score
        return 0  # No description