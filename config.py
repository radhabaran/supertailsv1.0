# config.py

# Parameters and their details
PARAMETERS_CONFIG = {
    "parameters": [
        {
            "name": "Self Introduction",
            "max_score": 2,
            "subparameters": [
                {"name": "Greeting", "weight": 1},
                {"name": "Introduction of self", "weight": 1},
            ],
        },
        {
            "name": "Company Introduction",
            "max_score": 2,
            "subparameters": [
                {"name": "Company name mentioned", "weight": 2},
            #     {"name": "Company mission mentioned", "weight": 1},
            ],
        },
        {
            "name": "Customer Name Confirmation",
            "max_score": 2,
            "subparameters": [
                {"name": "Asked for customer name", "weight": 2},
            ],
        },
        {
            "name": "Order Confirmation",
            "max_score": 2,
            "subparameters": [
                {"name": "Asked for order details", "weight": 2},
                # {"name": "Confirmed order is correct", "weight": 1},
            ],
        },
        {
            "name": "Purpose Of the Call (Context)",
            "max_score": 8,
            "subparameters": [
                {"name": "Explained purpose of the call", "weight": 8},
                # {"name": "Provided proper context", "weight": 4},
            ],
        },
        {
            "name": "Pet Name, Age and Gender",
            "max_score": 5,
            "subparameters": [
                {"name": "Asked for pet's name", "weight": 2},
                {"name": "Asked for pet's age", "weight": 1.5},
                {"name": "Asked for pet's gender", "weight": 1.5},
            ],
        },
        {
            "name": "Pet Body Weight",
            "max_score": 5,
            "subparameters": [
                {"name": "Vet's questions about body weight", "weight": 2.5},
                {"name": "User's responses about body weight", "weight": 2.5},
            ],
        },
        {
            "name": "Health Concern",
            "max_score": 5,
            "subparameters": [
                {"name": "Vet's questions about health concern", "weight": 3},
                {"name": "User's description of health concern", "weight": 2},
            ],
        },
        {
            "name": "Diet Confirmation",
            "max_score": 5,
            "subparameters": [
                {"name": "Asked about diet confirmation", "weight": 2.5},
                {"name": "Confirmed diet information", "weight": 2.5},
            ],
        },
        {
            "name": "Food Brand Name",
            "max_score": 5,
            "subparameters": [
                # {"name": "Asked for food brand", "weight": 2.5},
                {"name": "Confirmed food brand", "weight": 5},
            ],
        },
        {
            "name": "Tone & Voice Modulation",
            "max_score": 8,
            "subparameters": [
                {"name": "Maintains friendly tone", "weight": 4},
                {"name": "Maintains engaging tone", "weight": 4},
            ],
        },
        # {
        #     "name": "Clear Communication",
        #     "max_score": 8,
        #     "subparameters": [
        #         {"name": "Uses simple language", "weight": 4},
        #         {"name": "Avoids jargon", "weight": 4},
        #     ],
        # },
        # {
        #     "name": "Engagement & Rapport Building",
        #     "max_score": 8,
        #     "subparameters": [
        #         {"name": "Connects personally using pet's name", "weight": 4},
        #         {"name": "Acknowledges pet parent's feelings", "weight": 4},
        #     ],
        # },
        # {
        #     "name": "Patience & Attentiveness",
        #     "max_score": 8,
        #     "subparameters": [
        #         {"name": "Remains calm", "weight": 4},
        #         {"name": "Addresses concerns fully", "weight": 4},
        #     ],
        # },
        # {
        #     "name": "Empathy & Compassion",
        #     "max_score": 10,
        #     "subparameters": [
        #         {"name": "Shows genuine care", "weight": 5},
        #         {"name": "Shows concern for pet's well-being", "weight": 5},
        #     ],
        # },
        # {
        #     "name": "Dosage and Frequency",
        #     "max_score": 5,
        #     "subparameters": [
        #         {"name": "Explains dosage", "weight": 2.5},
        #         {"name": "Explains frequency", "weight": 2.5},
        #     ],
        # },
        # {
        #     "name": "Treatment Plan and Instructions PSP",
        #     "max_score": 7,
        #     "subparameters": [
        #         {"name": "Explains treatment plan", "weight": 3.5},
        #         {"name": "Provides PSP instructions", "weight": 3.5},
        #     ],
        # },
        # {
        #     "name": "Provided 'Chat with the Vet' Reminder at Call Closing",
        #     "max_score": 2,
        #     "subparameters": [
        #         {"name": "Reminds about 'Chat with the Vet'", "weight": 2},
        #     ],
        # },
        # {
        #     "name": "Audio Clarity",
        #     "max_score": 3,
        #     "subparameters": [
        #         {"name": "Audio is clear", "weight": 3},
        #     ],
        # },
    ]
}