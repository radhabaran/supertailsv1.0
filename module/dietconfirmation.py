# dietconfirmation.py

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


class DietConfirmation:
    def __init__(self, model_name="claude-3-5-haiku-20241022"):
        """
        Initialize the DietPlanConfirmation class by dynamically loading subparameter details from config.py.
        """
        self.parameter_name = "Diet Confirmation"
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
        Evaluate the transcripts for diet confirmation.

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
            # Step 1: Use regex to detect diet-related questions
            diet_questions = self.detect_diet_questions(transcript)

            # Step 2: Use LLM to classify user's description of diet
            diet_description_classification = self.detect_diet_description_using_llm(transcript)

            # Step 3: Grade the response
            question_score = self.grade_diet_questions(diet_questions)
            description_score = self.grade_diet_description(diet_description_classification)

            # Append the total score for this transcript
            total_score = question_score + description_score
            total_score = min(total_score, self.max_score)  # Ensure the total score does not exceed max_score
            scores.append({
                "score": total_score,
                "subscores": [question_score, description_score],  # Subparameter-specific scores
            })

        # Return results
        return {
            "scores": scores,
            "subparameters": subparameters,
            "subweights": subweights,
        }

    def detect_diet_questions(self, transcript):
        """
        Use regex to detect diet-related questions in the transcript.

        Args:
            transcript (str): The transcript text.

        Returns:
            list[str]: List of detected diet-related questions.
        """
        pattern = r"(?i)\b(what.*food|feeding|diet|homemade.*food|commercial.*diet|specific.*diet)\b"
        return re.findall(pattern, transcript)

    def detect_diet_description_using_llm(self, transcript):
        """
        Use LLM to classify the user's description of diet.
        """
        # Prompt for the LLM
        prompt = f"""
        Analyze the following transcript and classify the user's description of diet into one of three categories:
           - "Full Description": The user explicitly describes the diet plan in detail (e.g., homemade, commercial, or specific foods).
           - "Partial Description": The user briefly mentions the diet (e.g., mentions homemade food but lacks specifics).
           - "No Description": The user provides no information about the diet.

        Transcript: {transcript}

        Return the result as a JSON string in the following format:
        {{
            "diet_description_classification": "Full Description" | "Partial Description" | "No Description"
        }}
        """

        try:
            # Call the LLM
            response = self.llm.predict(prompt)

            # Log the raw response
            print(f"Raw LLM Response: {response}")

            # Use regex to extract the JSON block from the response
            json_match = re.search(r"{.*?}", response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in the response")

            # Parse the extracted JSON
            json_str = json_match.group(0)
            parsed_response = json.loads(json_str)

            # Extract the classification
            return parsed_response.get("diet_description_classification", "No Description")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM response: {e}")
            print(f"LLM Response: {response}")
            return "No Description"
        except ValueError as e:
            print(f"Error extracting JSON: {e}")
            print(f"LLM Response: {response}")
            return "No Description"
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "No Description"

    def grade_diet_questions(self, diet_questions):
        """
        Grade the vet's questions about diet confirmation.

        Args:
            diet_questions (list[str]): List of diet-related questions.

        Returns:
            int: Score for diet-related questions.
        """
        question_weight = next((sub["weight"] for sub in self.subparameters if sub["name"] == "Asked about diet confirmation"), 0)
        if len(diet_questions) >= 1:
            return question_weight  # Full score for at least one relevant question
        return 0  # No questions

    def grade_diet_description(self, diet_description_classification):
        """
        Grade the user's description of the diet.

        Args:
            diet_description_classification (str): Classification of the user's diet description.

        Returns:
            int: Score based on the classification.
        """
        description_weight = next((sub["weight"] for sub in self.subparameters if sub["name"] == "Confirmed diet information"), 0)
        if diet_description_classification == "Full Description":
            return description_weight  # Full score
        elif diet_description_classification == "Partial Description":
            return description_weight / 2  # Partial score
        return 0  # No description