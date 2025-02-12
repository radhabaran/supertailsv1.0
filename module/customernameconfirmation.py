# customernameconfirmation

import re

class CustomerNameConfirmation:
    def __init__(self):
        """
        Initialize the CustomerNameConfirmation class with parameter details.
        """
        self.parameter_name = "Customer Name Confirmation"
        self.max_score = 2
        self.subparameters = [
            {"name": "Asked for customer name", "weight": 2},
        ]

    def evaluate_transcripts(self, transcripts):
        """
        Evaluate the transcripts for Customer Name Confirmation.

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

        # Regex pattern to detect if the agent asked for customer name
        pattern = r"(?i)\b(am I speaking to|may I know|can I confirm|what is|your name is|is this)\s+([a-zA-Z]+)"

        for transcript in transcripts:
            # Initialize subparameter-specific scores
            subparameter_scores = []

            # Check if the transcript contains a question about the customer's name
            if re.search(pattern, transcript):
                subparameter_scores.append(2)  # Full weight for "Asked for customer name"
            else:
                subparameter_scores.append(0)  # No score if not asked

            # Calculate the total score (sum of subparameter scores)
            total_score = sum(subparameter_scores)

            # Append the score as a dictionary for this transcript
            scores.append({
                "score": total_score,  # Total score
                "subscores": subparameter_scores,  # Subparameter-specific scores
            })

        # Return results
        return {
            "scores": scores,
            "parameter": self.parameter_name,
            "max_score": self.max_score,
            "subparameters": subparameters,
            "subweights": subweights,
        }