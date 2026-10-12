
# =====================================================
# INTERVIEWAI - ANSWER EVALUATION
# =====================================================


def evaluate_answer(question, answer):
    """
    Basic InterviewAI answer evaluation.

    This is the initial evaluation system.
    Later, it can be replaced with a real AI API.
    """

    answer = answer.strip()

    # Empty answer
    if not answer:
        return {
            "score": 0,
            "feedback": "No answer was provided.",
            "strength": "No response",
            "improvement": "Try to provide a clear answer."
        }

    # ---------------------------------------------
    # WORD COUNT
    # ---------------------------------------------

    words = answer.split()
    word_count = len(words)


    # ---------------------------------------------
    # SCORE
    # ---------------------------------------------

    if word_count < 5:

        score = 2

    elif word_count < 15:

        score = 4

    elif word_count < 30:

        score = 6

    elif word_count < 50:

        score = 8

    else:

        score = 10


    # ---------------------------------------------
    # FEEDBACK
    # ---------------------------------------------

    if score <= 4:

        feedback = (
            "Your answer is too short. "
            "Try explaining the concept with more details "
            "and include an example."
        )

        strength = "You attempted the question."

        improvement = (
            "Give a more detailed explanation and "
            "support your answer with an example."
        )


    elif score <= 6:

        feedback = (
            "Your answer covers the basic idea, "
            "but it could be explained more clearly."
        )

        strength = "You covered the basic concept."

        improvement = (
            "Add more technical details and examples."
        )


    elif score <= 8:

        feedback = (
            "Good answer. You explained the concept "
            "with reasonable detail."
        )

        strength = "Good explanation and sufficient detail."

        improvement = (
            "Try to make the answer more structured "
            "and technically precise."
        )


    else:

        feedback = (
            "Excellent answer. It is detailed and "
            "provides a strong explanation."
        )

        strength = "Detailed and well-explained response."

        improvement = (
            "Maintain this level of detail while "
            "keeping the answer concise and structured."
        )


    return {
        "score": score,
        "feedback": feedback,
        "strength": strength,
        "improvement": improvement
    }

