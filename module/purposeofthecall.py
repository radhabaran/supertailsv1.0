# purposeofthecall.py

import os
import re
from langchain_anthropic import ChatAnthropic  # Import the Anthropic model
from dotenv import load_dotenv  # For loading environment variables

# Load environment variables
load_dotenv()

# Set Anthropic API key
anthro_api_key = os.environ.get('ANTHRO_KEY')
os.environ['ANTHROPIC_API_KEY'] = anthro_api_key


class PurposeOftheCall:
    def __init__(self, model_name="claude-3-5-haiku-20241022"):
        """
        Initialize the PurposeOfTheCall class with subparameter details and LLM setup.
        """
        self.parameter_name = "Purpose of the Call"
        self.max_score = 8
        self.subparameters = [
            {"name": "Explained purpose of the call", "weight": 8},
        ]

        # Initialize the Anthropic LLM
        self.llm = ChatAnthropic(model=model_name, temperature=0)

    def evaluate_transcripts(self, transcripts):
        """
        Evaluate the transcripts for the purpose of the call.

        Args:
            transcripts (list[str]): List of transcript strings.

        Returns:
            dict: Evaluation results containing scores, subparameters, and subweights.
        """
        scores = []
        subparameters = []
        subweights = []

        # Fetch subparameter details
        for subparam in self.subparameters:
            subparameters.append(subparam["name"])
            subweights.append(subparam["weight"])

        for transcript in transcripts:
            # Step 1: Use LLM to extract purpose of the call
            llm_response = self.call_llm(transcript)
            extracted_text = llm_response.get("text", "")
            explains_purpose = llm_response.get("explains_purpose", False)

            # Step 2: Grade the LLM response
            subparameter_scores = [0]  # Initialize scores for the subparameter

            if explains_purpose:
                subparameter_scores[0] = self.grade_response(extracted_text, explains_purpose)

                # Calculate the total score (sum of subparameter scores)
            total_score = sum(subparameter_scores)

            # Ensure the total score does not exceed the max score
            total_score = min(total_score, self.max_score)

            # Append the results
            scores.append({
                'score': total_score,  # Total score
                'subscores': subparameter_scores,  # Subparameter-specific scores
            })

        # Return results
        return {
            "scores": scores,
            "parameter": self.parameter_name,
            "max_score": self.max_score,
            "subparameters": subparameters,
            "subweights": subweights,
        }

    def call_llm(self, transcript):
        """
        Use the Anthropic LLM to determine if the purpose of the call is explained and extract it.

        Args:
            transcript (str): The transcript text.

        Returns:
            dict: LLM result with keys "explains_purpose" (bool) and "text" (relevant text if purpose is explained).
        """
        # Prompt for the LLM
        prompt = f"""
        Determine if the purpose of the call is explained in the following transcript.
        If yes, return "Yes" along with the relevant text explaining the purpose. If partially explained, return "Partial" and the text.
        If not explained, return "No."

        Transcript: {transcript}
        """

        try:
            # Call the Anthropic LLM
            response = self.llm.invoke(prompt)
            response_content = response.content.strip()

            print("*" * 100)
            print("\nLLM response on the purpose of the call:", response_content)

            if "Yes" in response_content:
                return {"explains_purpose": True, "text": response_content}
            elif "Partial" in response_content:
                return {"explains_purpose": True, "text": response_content}
            else:
                return {"explains_purpose": False, "text": ""}
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return {"explains_purpose": False, "text": ""}

    def grade_response(self, extracted_text, explains_purpose):
        """
        Grade the LLM response based on the extracted text.

        Args:
            extracted_text (str): The text extracted by the LLM.
            explains_purpose (bool): Whether the LLM indicates the purpose is explained.

        Returns:
            int: Score based on the level of explanation.
        """
        if not explains_purpose or not extracted_text:
            return 0  # Not provided

        # Check for explicit purpose-related phrases
        explicit_pattern = r"(?i)\b(this is in regards to|it's a verification call|purpose of this call|this call is about|calling regarding the order)\b"
        if re.search(explicit_pattern, extracted_text):
            return 8  # Adequate (Full points)

        # If not explicit, but partially provided, assign partial score
        return 4  # Partial (Half points)