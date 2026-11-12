
import streamlit as st
import ollama
import json
import re

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 AI Quiz Generator")
st.caption("Create educational quizzes powered by Ollama and Llama 3.2")

# -----------------------------
# SESSION STATE
# -----------------------------

if "quiz" not in st.session_state:
    st.quiz = None

if "submitted" not in st.session_state:
    st.submitted = False

# -----------------------------
# QUIZ GENERATION FUNCTION
# -----------------------------

def generate_quiz(subject, topic, difficulty, num_questions):

    prompt = f"""
    You are an expert educational quiz generator.

    Generate exactly {num_questions} multiple-choice
    questions for the following requirements:

    Subject: {subject}
    Topic: {topic}
    Difficulty: {difficulty}

    Rules:
    1. Generate exactly {num_questions} questions.
    2. Each question must have four options.
    3. Only one option must be correct.
    4. Questions must be educational and accurate.
    5. Include a short explanation for each answer.
    6. Do not repeat questions.

    Return ONLY valid JSON using this format:

    {{
        "questions": [
            {{
                "question": "Question text",
                "options": [
                    "Option A",
                    "Option B",
                    "Option C",
                    "Option D"
                ],
                "answer": "Correct option",
                "explanation": "Explanation of the answer"
            }}
        ]
    }}
    """

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": "You generate accurate educational quizzes. Return valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"
    )

    content = response["message"]["content"]

    data = json.loads(content)

    questions = data.get("questions", [])

    if len(questions) != num_questions:
        raise ValueError("AI generated an incorrect number of questions.")

    for q in questions:

        if (
            not isinstance(q, dict)
            or not isinstance(q.get("question"), str)
            or not isinstance(q.get("options"), list)
            or len(q["options"]) != 4
            or not all(isinstance(o, str) for o in q["options"])
            or len(set(q["options"])) != 4
            or not isinstance(q.get("answer"), str)
            or q["answer"] not in q["options"]
            or not isinstance(q.get("explanation"), str)
        ):
            raise ValueError("AI generated an invalid question format.")

    return questions


# -----------------------------
# SIDEBAR SETTINGS
# -----------------------------

with st.sidebar:

    st.header("⚙️ Quiz Settings")

    subject = st.selectbox(
        "Select Subject",
        [
            "Mathematics",
            "Physics",
            "Chemistry",
            "Biology",
            "Computer Science",
            "English",
            "History",
            "General Knowledge"
        ]
    )

    topic = st.text_input(
        "Enter Topic",
        placeholder="Example: Python loops"
    )

    difficulty = st.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard"]
    )

    num_questions = st.slider(
        "Number of Questions",
        5,
        20,
        5
    )

    generate_button = st.button(
        "Generate Quiz 🚀",
        use_container_width=True
    )

    if st.button("Clear Quiz", use_container_width=True):
        st.session_state.quiz = None
        st.session_state.submitted = False
        st.rerun()


# -----------------------------
# GENERATE QUIZ
# -----------------------------

if generate_button:

    if not topic.strip():

        st.warning("Please enter a topic first.")

    else:

        try:

            with st.spinner("Generating your quiz..."):

                quiz = generate_quiz(
                    subject,
                    topic,
                    difficulty,
                    num_questions
                )

                st.session_state.quiz = quiz
                st.session_state.submitted = False

            st.success("Quiz generated successfully!")

        except Exception as e:

            st.error(
                "Unable to generate quiz. "
                "Check that Ollama is running "
                "and Llama 3.2 is installed."
            )

            st.exception(e)


# -----------------------------
# DISPLAY QUIZ
# -----------------------------

if st.session_state.quiz:

    quiz = st.session_state.quiz

    st.divider()

    st.subheader("📝 Your Quiz")

    st.write(f"Total Questions: {len(quiz)}")

    if not st.session_state.submitted:

        with st.form("quiz_form"):

            answers = []

            for i, q in enumerate(quiz):

                st.markdown(
                    f"### Question {i + 1}"
                )

                st.write(q["question"])

                selected = st.radio(
                    "Choose your answer:",
                    q["options"],
                    index=None,
                    key=f"question_{i}"
                )

                answers.append(selected)

                st.divider()

            submit = st.form_submit_button(
                "Submit Quiz",
                use_container_width=True
            )

            if submit:

                if any(a is None for a in answers):

                    st.warning(
                        "Please answer all questions."
                    )

                else:

                    st.session_state.answers = answers
                    st.session_state.submitted = True
                    st.rerun()


    # -----------------------------
    # RESULTS
    # -----------------------------

    if st.session_state.submitted:

        answers = st.session_state.answers

        score = 0

        for i, q in enumerate(quiz):

            if answers[i] == q["answer"]:
                score += 1

        percentage = (score / len(quiz)) * 100

        st.subheader("🏆 Quiz Results")

        st.metric(
            "Your Score",
            f"{score}/{len(quiz)}"
        )

        st.progress(percentage / 100)

        st.write(
            f"Percentage: {percentage:.1f}%"
        )

        if percentage >= 80:
            st.success("Excellent work! 🌟")

        elif percentage >= 50:
            st.info("Good effort! Keep practicing. 👍")

        else:
            st.warning("Keep learning. You can improve! 💪")

        st.divider()

        st.subheader("📋 Answer Review")

        for i, q in enumerate(quiz):

            st.markdown(
                f"### Question {i + 1}"
            )

            st.write(q["question"])

            st.write(
                f"Your Answer: {answers[i]}"
            )

            st.write(
                f"Correct Answer: {q['answer']}"
            )

            if answers[i] == q["answer"]:

                st.success("Correct answer!")

            else:

                st.error("Incorrect answer.")

            st.info(
                f"Explanation: {q['explanation']}"
            )

            st.divider()

        if st.button("Generate New Quiz 🔄"):

            st.session_state.quiz = None
            st.session_state.submitted = False
            st.rerun()
