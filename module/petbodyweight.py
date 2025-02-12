import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PetBodyWeight:
    def __init__(self):
        # Define subparameters and weights
        self.subparameters = ["Vet's questions about body weight", "User's responses about body weight"]
        self.subweights = [2.5, 2.5]
        self.max_score = 5

    def evaluate_transcripts(self, transcripts):
        scores = []  # List to hold scores for each transcript

        for transcript in transcripts:

            # Subparameter 1: Vet's question about body weight
            vet_question = self.check_vet_question_on_bodyweight(transcript)

            # Subparameter 2: User's response about body weight
            user_response = self.check_user_response(transcript)

            # Scoring logic (based on subweights)
            subparameter_scores = [0, 0]  # Initialize scores for each subparameter

            if vet_question:
                subparameter_scores[0] = self.subweights[0]  # Assign weight for subparameter 1
            if user_response:
                subparameter_scores[1] = self.subweights[1]  # Assign weight for subparameter 2

                # Calculate the total score (sum of subparameter scores)
            total_score = sum(subparameter_scores)

            # Ensure the total score does not exceed the max score
            total_score = min(total_score, self.max_score)

            # Append the results
            scores.append({
                'score': total_score,  # Total score
                'subscores': subparameter_scores,  # Subparameter-specific scores
            })

        return {
            'scores': scores,
            'subparameters': self.subparameters,
            'subweights': self.subweights
        }

    def check_vet_question_on_bodyweight(self, transcript):
        # Look for specific questions about the pet's body weight
        pattern = r"(?i)\b(body weight|how much does your pet weigh|what is the weight|weight of the pet)\b"
        return bool(re.search(pattern, transcript))

    def check_user_response(self, transcript):
        # Look for specific responses indicating that the user provided information about weight
        pattern = r"(?i)(\b\d+\s*(kg|kgs|pounds|lbs|kilograms|grams|ounces)\b|around|about|approximately|he weighs|she weighs)"
        match = re.search(pattern, transcript)
        return match.group(0) if match else None