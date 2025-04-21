# engine.py

class SuperChatbot:
    def __init__(self):
        self.qa_pairs = {
            "what are good warm-up exercises": "Try jumping jacks, arm circles, and light jogging.",
            "what should i eat after a workout": "A balanced meal with protein and carbs, like chicken with rice or a smoothie.",
            "what classes are available": "We offer yoga, strength training, and HIIT classes throughout the week.",
        }

    def answer_question(self, question: str) -> str:
        question = question.strip().lower()
        for key in self.qa_pairs:
            if key in question:
                return self.qa_pairs[key]
        return "Please ask a question related to workouts, fitness, or nutrition."
