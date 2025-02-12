# dietconfirmation.py

import os
import json
import re
from langchain_anthropic import ChatAnthropic  # Import the Anthropic model
from dotenv import load_dotenv  # For loading environment variables

# Load environment variables
load_dotenv()

# Set Anthropic API key
anthro_api_key = os.environ.get("ANTHRO_KEY")
os.environ["ANTHROPIC_API_KEY"] = anthro_api_key

# Dynamically load the PARAMETERS_CONFIG from `config.py`
import importlib.util

CONFIG_PATH = "config.py"
spec = importlib.util.spec_from_file_location("config", CONFIG_PATH)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
PARAMETERS_CONFIG = config.PARAMETERS_CONFIG


class FoodBrandName:
    def __init__(self, model_name="claude-3-5-haiku-20241022"):
        """
        Initialize the FoodBrandName class by dynamically loading subparameter details from config.py.
        """
        self.parameter_name = "Food Brand Name"
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
        Evaluate the transcripts for pet food brand mentions.

        Args:
            transcripts (list[str]): List of transcript strings.

        Returns:
            dict: Evaluation results containing scores, subparameters, and subweights.
        """
        scores = []  # List to hold scores for each transcript
        subparameters = [sub["name"] for sub in self.subparameters]
        subweights = [sub["weight"] for sub in self.subparameters]

        for transcript in transcripts:
            # Detect brands using the LLM
            detected_brands = self.detect_pet_food_brands_using_llm(transcript)

            # Subparameter-specific scores
            subparameter_scores = [0] * len(subparameters)

            # Subparameter 1: "Confirmed food brand"
            if "Confirmed food brand" in subparameters:
                index = subparameters.index("Confirmed food brand")
                subparameter_scores[index] = len(detected_brands) * subweights[index]

            # Calculate the total score (sum of subparameter scores)
            total_score = sum(subparameter_scores)

            # Ensure the total score does not exceed the max score
            total_score = min(total_score, self.max_score)

            # Append results for this transcript
            scores.append({
                "score": total_score,  # Total score
                "subscores": subparameter_scores,  # Subparameter-specific scores
                "detected_brands": detected_brands,  # List of detected brand names
            })

        # Return results
        return {
            "scores": scores,
            "parameter": self.parameter_name,  # Parameter name
            "max_score": self.max_score,       # Maximum score
            "subparameters": subparameters,   # List of subparameters
            "subweights": subweights,         # Subparameter weights
        }

    def detect_pet_food_brands_using_llm(self, transcript):
        """
        Use LLM to detect pet food brands in the transcript.

        Args:
            transcript (str): The transcript text.

        Returns:
            list[str]: List of detected pet food brands.
        """
        # Prompt for the LLM
        prompt = f"""
        Analyze the following transcript and extract only pet food brand names mentioned and ignore any other pet 
        related product brand names.
        Return the result as a JSON array of detected brand names.

        Transcript: {transcript}

        Output format:
        ["brand_name_1", "brand_name_2", ...]
        """

        try:
            # Call the Anthropic LLM using `invoke`
            response = self.llm.invoke(prompt)

            # Extract the content of the response
            response_content = response.content.strip()
            print("*" * 100)
            print("\nLLM response on detected pet food brands:", response_content)

            # Use regex to extract the JSON block from the response
            json_match = re.search(r"\[.*?\]", response_content, re.DOTALL)  # Match JSON array format
            if not json_match:
                raise ValueError("No JSON array found in the response")

            # Parse the extracted JSON
            json_str = json_match.group(0)
            detected_brands = json.loads(json_str)

            # Return the list of detected brands
            return detected_brands
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM response: {e}")
            print(f"LLM Response: {response_content}")
            return []
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return []

    def grade_brand_detection(self, detected_brands):
        """
        Grade the detection of pet food brands.

        Args:
            detected_brands (list[str]): List of detected pet food brands.

        Returns:
            int: Score based on the number of detected brands.
        """
        brand_weight = next((sub["weight"] for sub in self.subparameters if sub["name"] == "Confirmed food brand"), 0)
        return min(len(detected_brands) * brand_weight, self.max_score)