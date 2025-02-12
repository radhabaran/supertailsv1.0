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


class ToneVoiceModulation:
    def __init__(self, model_name="claude-3-5-haiku-20241022"):
        """
        Initialize the VetTone class by dynamically loading subparameter details from config.py.
        """
        self.parameter_name = "Tone & Voice Modulation"
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
        Evaluate the tone of the vet in the provided transcripts.

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
            # Initialize subscores for this transcript
            subscores = []

            # Evaluate each subparameter separately using the LLM
            for subparam in self.subparameters:
                subscore = self.evaluate_subparameter(transcript, subparam["name"], subparam["weight"])
                subscores.append(subscore)

            # Calculate the total score for this transcript
            total_score = sum(subscores)

            # Append the total score and subscores for this transcript
            scores.append({
                "score": total_score,
                "subscores": subscores  # Subscores for each subparameter
            })

        # Return results
        return {
            "scores": scores,
            "parameter": self.parameter_name,
            "max_score": self.max_score,
            "subparameters": subparameters,
            "subweights": subweights,
        }

    def evaluate_subparameter(self, transcript, subparameter_name, weight):
        """
        Use the LLM to evaluate a specific subparameter for the given transcript.

        Args:
            transcript (str): The transcript text.
            subparameter_name (str): The name of the subparameter.
            weight (int): The weight of the subparameter.

        Returns:
            int: Score obtained for the subparameter.
        """
        # Prompt for the LLM
        prompt = f"""
        Analyze the following transcript to evaluate the subparameter: "{subparameter_name}".

        Subparameter details:
        - "{subparameter_name}": {self.get_subparameter_description(subparameter_name)}

        Classify the vet's performance into one of the following categories:
          - "Excellent": Fully meets the subparameter requirements.
          - "Very Good": Mostly meets the subparameter requirements with minor lapses.
          - "Average": Partially meets the subparameter requirements.
          - "Poor": Fails to meet the subparameter requirements.

        Transcript: {transcript}

        Return the result as a JSON string in the following format:
        {{
            "classification": "Excellent" | "Very Good" | "Average" | "Poor"
        }}
        """

        try:
            # Call the Anthropic LLM
            response = self.llm.invoke(prompt)

            # Extract the content of the response
            response_content = response.content.strip()
            print(f"LLM response for '{subparameter_name}' analysis:", response_content)

            # Use regex to extract the JSON block from the response
            json_match = re.search(r"{.*?}", response_content, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in the response")

            # Parse the extracted JSON
            json_str = json_match.group(0)
            parsed_response = json.loads(json_str)

            # Extract the classification and compute the score
            classification = parsed_response.get("classification", "Poor")
            return self.grade_subparameter(classification, weight)
        except Exception as e:
            print(f"Error evaluating subparameter '{subparameter_name}': {e}")
            return 0  # Return 0 score in case of any error

    def get_subparameter_description(self, subparameter_name):
        """
        Return a description for the given subparameter.

        Args:
            subparameter_name (str): The name of the subparameter.

        Returns:
            str: Description of the subparameter.
        """
        descriptions = {
            "Maintains friendly tone": "The vet maintains a friendly and warm tone throughout the conversation.",
            "Maintains engaging tone": "The vet maintains an engaging and lively tone throughout the conversation.",
        }
        return descriptions.get(subparameter_name, "No description available.")

    def grade_subparameter(self, classification, weight):
        """
        Grade a subparameter based on its classification.

        Args:
            classification (str): Classification of the vet's performance.
            weight (int): Weight of the subparameter.

        Returns:
            int: Score based on the classification and weight.
        """
        if classification == "Excellent":
            return weight  # Full score (100% of the weight)
        elif classification == "Very Good":
            return int(weight * 0.75)  # 75% of the weight
        elif classification == "Average":
            return int(weight * 0.5)  # 50% of the weight
        elif classification == "Poor":
            return int(weight * 0.25)  # 25% of the weight
        return 0  # Default to 0 if no valid classification