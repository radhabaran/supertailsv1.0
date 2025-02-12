# selfintroduction.py

import re

class SelfIntroduction:
    def __init__(self):
        # Define subparameters and weights from config
        self.subparameters = ["Greeting", "Introduction of self"]
        self.subweights = [1, 1]
        self.max_score = 2  # Maximum possible score

    def evaluate_transcripts(self, transcripts):
        scores = []  # List to hold scores for each transcript

        for transcript in transcripts:

            # Subparameter 1: Greeting
            greeting = self.check_greeting(transcript)

            # Subparameter 2: Introduction of self
            introduction = self.check_introduction_of_self(transcript)

            # Subparameter-specific scores
            subparameter_scores = [0, 0]  # Initialize scores for each subparameter

            if greeting:
                subparameter_scores[0] = self.subweights[0]
            if introduction:
                subparameter_scores[1] = self.subweights[1]

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

    def check_greeting(self, transcript):
        """
        Check if the vet greeted the customer at the beginning of the call.
        """
        # Look for common greetings
        pattern = r"(?i)\b(hello|hi|good morning|good afternoon|good evening)\b"
        match = re.search(pattern, transcript)
        return match.group(0) if match else None

    def check_introduction_of_self(self, transcript):
        """
        Check if the vet introduced themselves to the customer.
        """
        # Look for self-introduction phrases, including contractions
        pattern = r"(?i)\b(I am Dr\.|I'm Dr\.|This is Dr\.|My name is Dr\.|I am a veterinarian|This is a veterinarian)\s+[A-Za-z]+"
        match = re.search(pattern, transcript)
        return match.group(0) if match else None