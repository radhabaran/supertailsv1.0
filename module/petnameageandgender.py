# petnameageandgender.py

import os
import re
from langchain_anthropic import ChatAnthropic  # Import the Anthropic model
from dotenv import load_dotenv  # For loading environment variables
from config import PARAMETERS_CONFIG

# Load environment variables
load_dotenv()

# Set Anthropic API key
anthro_api_key = os.environ.get('ANTHRO_KEY')
os.environ['ANTHROPIC_API_KEY'] = anthro_api_key


class PetNameAgeandGender:
    def __init__(self, model_name="claude-3-5-haiku-20241022"):
        """
        Initialize the PetIdentification class with subparameter details and LLM setup.
        """
        # Extract the configuration for "Pet Name, Age, and Gender"
        self.parameter_config = next(
            param for param in PARAMETERS_CONFIG["parameters"] if param["name"] == "Pet Name, Age and Gender"
        )
        self.parameter_name = self.parameter_config["name"]
        self.max_score = self.parameter_config["max_score"]
        self.subparameters = [subparam["name"] for subparam in self.parameter_config["subparameters"]]
        self.subweights = [subparam["weight"] for subparam in self.parameter_config["subparameters"]]

        # Initialize the Anthropic LLM
        self.llm = ChatAnthropic(model=model_name, temperature=0)

    def evaluate_transcripts(self, transcripts):
        """
        Evaluate the transcripts for the pet's name, age, and gender.

        Args:
            transcripts (list[str]): List of transcript strings.

        Returns:
            dict: Evaluation results containing scores, subparameters, and subweights.
        """
        scores = []  # List to hold scores for each transcript

        for transcript in transcripts:

            # Subparameter 1: Pet's Name
            pet_name = self.check_pet_name(transcript)

            # Subparameter 2: Pet's Age
            pet_age = self.check_pet_age(transcript)

            # Subparameter 3: Pet's Gender
            pet_gender = self.check_pet_gender(transcript)

            # Subparameter-specific scores
            subparameter_scores = [0, 0, 0]  # Initialize scores for each subparameter

            if pet_name:
                subparameter_scores[0] = self.subweights[0]
            if pet_age:
                subparameter_scores[1] = self.subweights[1]
            if pet_gender:
                subparameter_scores[2] = self.subweights[2]

            # Calculate the total score (sum of subparameter scores)
            total_score = sum(subparameter_scores)

            # Ensure the total score does not exceed the max score
            total_score = min(total_score, self.max_score)

            # Append results for this transcript
            scores.append({
                'score': total_score,  # Total score
                'subscores': subparameter_scores,  # Subparameter-specific scores
            })

        return {
            'scores': scores,
            'parameter': self.parameter_name,
            'max_score': self.max_score,
            'subparameters': self.subparameters,
            'subweights': self.subweights,
        }

    def check_pet_name(self, transcript):
        """
        Check if the name of the pet is mentioned in the transcript.
        """
        # Updated regex to handle indirect mentions like "Is it for the same pet, Albus?"
        pattern = r"(?i)\b(my pet's name is|this is|her name is|his name is|is it for the same pet,)\s+([A-Za-z]+)"
        match = re.search(pattern, transcript)
        return match.group(2) if match else None

    def check_pet_age(self, transcript):
        """
        Identify if the pet's age is mentioned in the transcript using an LLM.

        Args:
            transcript (str): The transcript string.

        Returns:
            str: The pet's age if mentioned, or None otherwise.
        """
        # Use the LLM to extract pet's age
        llm_response = self.call_llm_for_age(transcript)
        extracted_text = llm_response.get("text", "")
        age_mentioned = llm_response.get("age_mentioned", False)

        return extracted_text if age_mentioned else None

    def check_pet_gender(self, transcript):
        """
        Check if the gender of the pet is mentioned in the transcript.
        """
        # Updated regex to consider indirect mentions like "his liver" or "her prescription"
        pattern = r"(?i)\b(she is|he is|my pet is|his|her)\s+(male|female)?"
        match = re.search(pattern, transcript)
        if match:
            # If "male" or "female" is explicitly mentioned
            if match.group(2):
                return match.group(2).lower()
            # Infer gender from possessive pronouns
            elif match.group(1).lower() in ["he is", "his"]:
                return "male"
            elif match.group(1).lower() in ["she is", "her"]:
                return "female"
        return None

    def call_llm_for_age(self, transcript):
        """
        Use the Anthropic LLM to determine if the pet's age is mentioned and extract it.

        Args:
            transcript (str): The transcript text.

        Returns:
            dict: LLM result with keys "age_mentioned" (bool) and "text" (relevant text if age is mentioned).
        """
        # Prompt for the LLM
        prompt = f"""
        Determine if the pet's age is mentioned in the following transcript.
        If yes, return "Yes" and extract the age (e.g., '3 years old', '6 months', etc.).
        If no age is mentioned, return "No."

        Transcript: {transcript}
        """

        try:
            # Call the Anthropic LLM
            response = self.llm.invoke(prompt)
            response_content = response.content.strip()

            print("*" * 100)
            print("\nLLM response on age of the pet :", response_content)

            if "Yes" in response_content:
                # Extract the relevant age text
                return {"age_mentioned": True, "text": response_content}
            else:
                return {"age_mentioned": False, "text": ""}
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return {"age_mentioned": False, "text": ""}