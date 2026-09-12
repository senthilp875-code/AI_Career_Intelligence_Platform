"""
==========================================
TalentIQ AI
AI Interview Question Generator
Version 1.0 Premium
==========================================
"""


def generate_interview_questions(predicted_job):

    job = predicted_job.lower()

    questions = {

        "technical": [],

        "hr": [],

        "coding": []

    }

    # ==========================================
    # Python Developer
    # ==========================================

    if "python" in job:

        questions["technical"] = [

            "Explain Python decorators.",

            "What is multithreading in Python?",

            "Difference between List and Tuple.",

            "Explain OOP concepts in Python.",

            "What are generators in Python?"

        ]

        questions["coding"] = [

            "Reverse a string without using slicing.",

            "Find duplicate numbers in a list.",

            "Write a palindrome checker.",

            "Build a simple REST API using Flask."

        ]

    # ==========================================
    # Data Scientist
    # ==========================================

    elif "data" in job:

        questions["technical"] = [

            "Difference between Supervised and Unsupervised Learning.",

            "Explain Random Forest.",

            "What is Overfitting?",

            "Difference between Pandas and NumPy.",

            "Explain Cross Validation."

        ]

        questions["coding"] = [

            "Load a CSV using Pandas.",

            "Remove missing values.",

            "Plot a graph using Matplotlib.",

            "Train a Linear Regression model."

        ]

    # ==========================================
    # AI / ML Engineer
    # ==========================================

    elif "ai" in job or "machine" in job:

        questions["technical"] = [

            "Explain Neural Networks.",

            "Difference between CNN and RNN.",

            "What is Gradient Descent?",

            "Explain Transformers.",

            "What is Deep Learning?"

        ]

        questions["coding"] = [

            "Build a simple ANN.",

            "Load an image dataset.",

            "Train a classification model.",

            "Predict using TensorFlow."

        ]

    # ==========================================
    # Default
    # ==========================================

    else:

        questions["technical"] = [

            "Explain your final year project.",

            "What technologies have you used?",

            "Describe your strongest skill.",

            "How do you debug code?",

            "Explain Git."

        ]

        questions["coding"] = [

            "Reverse a string.",

            "Check Prime Number.",

            "Find Maximum Number.",

            "Remove Duplicates."

        ]

    # ==========================================
    # HR Questions
    # ==========================================

    questions["hr"] = [

        "Tell me about yourself.",

        "Why should we hire you?",

        "Describe a challenging project.",

        "Where do you see yourself in five years?",

        "What are your strengths and weaknesses?"

    ]

    return questions