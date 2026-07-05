from app.database.models import add_question


async def import_questions(
    file_path,
    exam,
    subject,
    chapter,
    marks,
    negative
):

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    questions = text.split("---------------------------------")

    imported = 0

    for q in questions:

        lines = [line.strip() for line in q.split("\n") if line.strip()]

        if len(lines) < 6:
            continue

        question = lines[0]

        option_a = lines[1].replace("A)", "").strip()
        option_b = lines[2].replace("B)", "").strip()
        option_c = lines[3].replace("C)", "").strip()
        option_d = lines[4].replace("D)", "").strip()

        answer = lines[5].replace("Answer:", "").strip()

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
            explanation=None,
            difficulty="Easy",
            marks=marks,
            negative_marks=negative
        )

        imported += 1

    return imported