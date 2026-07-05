"""
Script to insert test data into the database
Run this file to populate the database with sample questions
"""

import asyncio
from app.database.connection import get_db
from app.database.models import add_question


async def insert_test_data():
    """Insert sample questions for testing"""
    
    test_questions = [
        {
            "exam": "GNM",
            "subject": "Anatomy",
            "chapter": "Skeletal System",
            "question": "How many bones are there in human skeleton?",
            "option_a": "186",
            "option_b": "206",
            "option_c": "216",
            "option_d": "226",
            "correct_answer": "B",
            "explanation": "Adult human skeleton contains 206 bones",
            "difficulty": "Easy",
            "marks": 1
        },
        {
            "exam": "GNM",
            "subject": "Anatomy",
            "chapter": "Skeletal System",
            "question": "What is the strongest bone in human body?",
            "option_a": "Humerus",
            "option_b": "Femur",
            "option_c": "Tibia",
            "option_d": "Fibula",
            "correct_answer": "B",
            "explanation": "Femur (thighbone) is the longest and strongest bone",
            "difficulty": "Easy",
            "marks": 1
        },
        {
            "exam": "GNM",
            "subject": "Physiology",
            "chapter": "Nervous System",
            "question": "What is the basic functional unit of nervous system?",
            "option_a": "Synapse",
            "option_b": "Neuron",
            "option_c": "Dendrite",
            "option_d": "Axon",
            "correct_answer": "B",
            "explanation": "Neuron is the basic structural and functional unit of nervous system",
            "difficulty": "Medium",
            "marks": 1
        },
        {
            "exam": "GNM",
            "subject": "Physiology",
            "chapter": "Nervous System",
            "question": "How many pairs of spinal nerves are present?",
            "option_a": "30",
            "option_b": "31",
            "option_c": "32",
            "option_d": "33",
            "correct_answer": "B",
            "explanation": "31 pairs of spinal nerves emerge from spinal cord",
            "difficulty": "Medium",
            "marks": 1
        },
        {
            "exam": "GNM",
            "subject": "Pathology",
            "chapter": "Inflammation",
            "question": "What are the cardinal signs of inflammation?",
            "option_a": "Redness, Swelling, Heat",
            "option_b": "Redness, Swelling, Heat, Pain",
            "option_c": "Redness, Swelling, Heat, Pain, Loss of function",
            "option_d": "Only Redness and Swelling",
            "correct_answer": "C",
            "explanation": "5 cardinal signs: Rubor, Tumor, Calor, Dolor, Functio laesa",
            "difficulty": "Easy",
            "marks": 1
        },
        {
            "exam": "GNM",
            "subject": "Pathology",
            "chapter": "Inflammation",
            "question": "Which cells are primarily involved in acute inflammation?",
            "option_a": "Lymphocytes",
            "option_b": "Neutrophils",
            "option_c": "Macrophages",
            "option_d": "Eosinophils",
            "correct_answer": "B",
            "explanation": "Neutrophils are the main cells in acute inflammatory response",
            "difficulty": "Medium",
            "marks": 1
        },
        {
            "exam": "ANM",
            "subject": "Nursing",
            "chapter": "Fundamentals",
            "question": "What is the main goal of nursing?",
            "option_a": "To cure disease",
            "option_b": "To promote health and well-being",
            "option_c": "To administer drugs",
            "option_d": "To perform surgeries",
            "correct_answer": "B",
            "explanation": "Primary goal of nursing is holistic health promotion",
            "difficulty": "Easy",
            "marks": 1
        },
        {
            "exam": "ANM",
            "subject": "Community Health",
            "chapter": "Epidemiology",
            "question": "What is epidemiology?",
            "option_a": "Study of skin diseases",
            "option_b": "Study of disease occurrence in populations",
            "option_c": "Study of genetics",
            "option_d": "Study of anatomy",
            "correct_answer": "B",
            "explanation": "Epidemiology studies disease patterns in communities",
            "difficulty": "Easy",
            "marks": 1
        },
        {
            "exam": "GNM",
            "subject": "Anatomy",
            "chapter": "Cardiovascular System",
            "question": "What is the normal heart rate of an adult at rest?",
            "option_a": "40-60 bpm",
            "option_b": "60-100 bpm",
            "option_c": "100-120 bpm",
            "option_d": "120-140 bpm",
            "correct_answer": "B",
            "explanation": "Normal resting heart rate is 60-100 beats per minute",
            "difficulty": "Easy",
            "marks": 1
        },
        {
            "exam": "GNM",
            "subject": "Physiology",
            "chapter": "Respiratory System",
            "question": "What is the normal respiratory rate of an adult?",
            "option_a": "8-12 breaths/min",
            "option_b": "12-16 breaths/min",
            "option_c": "16-20 breaths/min",
            "option_d": "20-24 breaths/min",
            "correct_answer": "B",
            "explanation": "Normal respiratory rate is 12-16 breaths per minute",
            "difficulty": "Easy",
            "marks": 1
        }
    ]
    
    print("🔄 Inserting test data...")
    
    for q in test_questions:
        await add_question(
            exam=q["exam"],
            subject=q["subject"],
            chapter=q["chapter"],
            question=q["question"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            correct_answer=q["correct_answer"],
            explanation=q["explanation"],
            difficulty=q["difficulty"],
            marks=q["marks"]
        )
        print(f"✅ Added: {q['question'][:50]}...")
    
    print("\n✅ Test data insertion complete!")
    print("📊 10 sample questions added to database")
    print("\nYou can now test the quiz features:")
    print("- /quiz or 📝 Live Quiz")
    print("- 📚 Practice Quiz")


if __name__ == "__main__":
    asyncio.run(insert_test_data())
