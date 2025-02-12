# orderconfirmation

import re

class OrderConfirmation:
    def __init__(self):
        """
        Initialize the OrderConfirmation class with parameter details.
        """
        self.parameter_name = "Order Confirmation"
        self.max_score = 2
        self.subparameters = [
            {"name": "Asked for order details", "weight": 2},
        ]

    def evaluate_transcripts(self, transcripts):
        """
        Evaluate the transcripts for Order Confirmation.

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

        # Regex pattern to detect order confirmation text
        pattern = r"(?i)\b(this (call|is|conversation) (is|was)? (regarding|about|in regards to)|you have ordered|your order (is|was)? (for|about)|order details|confirm your order|verify your order|this is in regards to the order you have placed)\b"

        for transcript in transcripts:
            # Initialize subparameter-specific scores
            subparameter_scores = []

            # Check if the transcript contains text related to order confirmation
            if re.search(pattern, transcript):
                subparameter_scores.append(2)  # Full weight for "Asked for order details"
            else:
                subparameter_scores.append(0)  # No score if not mentioned

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