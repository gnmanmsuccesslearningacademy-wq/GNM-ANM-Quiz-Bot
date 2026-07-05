import pandas as pd

from app.database.models import add_question


async def import_questions(
    file_path,
    exam,
    subject,
    chapter,
    marks,
    negative
):

    df = pd.read_excel(file_path)

    imported = 0

    for _, row in df.iterrows():

        question = str(row["Question"]).strip()

        option_a = str(row["A"]).strip()
        option_b = str(row["B"]).strip()
        option_c = str(row["C"]).strip()
        option_d = str(row["D"]).strip()

        answer = str(row["Answer"]).strip()

        explanation = None

        if "Explanation" in df.columns:
            value = row["Explanation"]

            if pd.notna(value):
                explanation = str(value).strip()

        difficulty = "Easy"

        if "Difficulty" in df.columns:
            value = row["Difficulty"]

            if pd.notna(value):
                difficulty = str(value).strip()

        await add_question(
            exam=exam,
            subject=subject,
            chapter=chapter,
            question=question,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=answer,
            explanation=explanation,
            difficulty=difficulty,
            marks=marks,
            negative_marks=negative
        )

        imported += 1

    return imported