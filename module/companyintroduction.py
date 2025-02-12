import re

class CompanyIntroduction:
    def __init__(self):
        """
        Initialize the CompanyIntroduction class with parameter details.
        """
        self.parameter_name = "Company Introduction"
        self.max_score = 2  # Maximum possible score for "Company Introduction"
        self.subparameters = [
            {"name": "Company name mentioned", "weight": 2},
        ]

    def evaluate_transcripts(self, transcripts):
        """
        Evaluate the transcripts for Company Introduction.

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

        # Regex pattern to detect if the company name is mentioned
        pattern = r"(?i)\b(calling from|representing|working with|on behalf of|from)\s+(Supertails|Super Tails|Supertales|Super Tales|Supertales Pet Pharmacy|Supertel's|Supertel's Pet Pharmacy)\b"

        for transcript in transcripts:
            # Initialize score for this transcript
            subparameter_scores = []

            # Check if the transcript contains a company name mention
            if re.search(pattern, transcript):
                subparameter_scores.append(2)  # Full weight for "Company name mentioned"
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