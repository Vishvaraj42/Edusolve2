import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"  # Alternatives: "llama-3.3-70b-versatile", "llama-3.1-70b-versatile"

SYSTEM_PROMPT = """
You are EduSolve AI, a tutor for Indian Class 9 and 10 students.
You ONLY answer Science and Mathematics questions.
If the question is not about Science or Maths, reply:
"I only help with Science and Maths doubts!"

Always respond in this exact format:

EXPLANATION:
(explain clearly in simple language for a 15 year old)

KEY FORMULA / FACT:
(the most important formula or fact)

REAL EXAMPLE:
(one simple real life example)
"""


def ask_doubt(question: str, subject: str, grade: int) -> str:
    prompt = f"[Class {grade}] [{subject}] Student doubt: {question}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def get_practice_questions(ai_answer: str, subject: str, grade: int) -> list:
    prompt = f"""
Based on this explanation given to a Class {grade} {subject} student:
{ai_answer}

Generate exactly 3 practice questions.
Return ONLY a JSON array like this, nothing else:
[
  {{"question": "...", "answer": "...", "type": "mcq"}},
  {{"question": "...", "answer": "...", "type": "short"}},
  {{"question": "...", "answer": "...", "type": "short"}}
]
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Return only valid JSON. No explanation, no markdown."},
            {"role": "user", "content": prompt}
        ]
    )
    raw = response.choices[0].message.content
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start != -1 and end != 0:
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            return []
    return []


def solve_doubt(question: str, subject: str, grade: int) -> dict:
    print(f"\n Thinking about: {question}\n")
    answer = ask_doubt(question, subject, grade)
    practice = get_practice_questions(answer, subject, grade)
    return {
        "question": question,
        "subject": subject,
        "grade": grade,
        "answer": answer,
        "practice_questions": practice
    }


def get_grade() -> int:
    """Prompt user for a valid grade (9 or 10)."""
    while True:
        grade_input = input("Enter your Class (9 or 10): ").strip()
        if grade_input in ["9", "10"]:
            return int(grade_input)
        print(" Invalid class. Please enter 9 or 10.")


def get_subject() -> str:
    """Prompt user for a valid subject."""
    while True:
        print("\nChoose Subject:")
        print("  1. Science")
        print("  2. Maths")
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return "Science"
        elif choice == "2":
            return "Maths"
        print(" Invalid choice. Please enter 1 or 2.")


def get_question() -> str:
    """Prompt user for a non-empty question."""
    while True:
        question = input("\nType your doubt/question: ").strip()
        if question:
            return question
        print(" Question cannot be empty. Please try again.")


if __name__ == "__main__":
    print("=" * 60)
    print("         Welcome to EduSolve AI Tutor ")
    print("     For Class 9 & 10 | Science & Maths")
    print("=" * 60)

    while True:
        # Collect inputs
        grade    = get_grade()
        subject  = get_subject()
        question = get_question()

        # Get AI answer
        result = solve_doubt(question=question, subject=subject, grade=grade)

        # Display answer
        print("\n" + "=" * 60)
        print("ANSWER:")
        print("=" * 60)
        print(result["answer"])

        # Display practice questions
        if result["practice_questions"]:
            print("\n" + "=" * 60)
            print("PRACTICE QUESTIONS:")
            print("=" * 60)
            for i, q in enumerate(result["practice_questions"], 1):
                print(f"\nQ{i} [{q['type'].upper()}]: {q['question']}")
                print(f"   Answer: {q['answer']}")

        # Ask if user wants to continue
        print("\n" + "-" * 60)
        again = input("Ask another doubt? (yes/no): ").strip().lower()
        if again not in ["yes", "y"]:
            print("\nGoodbye! Keep studying! ")
            break
        print()