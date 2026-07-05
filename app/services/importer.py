from app.services.excel_import import import_questions as import_excel
from app.services.docx_import import import_questions as import_docx
from app.services.txt_import import import_questions as import_txt


async def import_file(
    file_path,
    exam,
    subject,
    chapter,
    marks,
    negative
):

    file_path = file_path.lower()

    if file_path.endswith(".xlsx"):

        return await import_excel(
            file_path=file_path,
            exam=exam,
            subject=subject,
            chapter=chapter,
            marks=marks,
            negative=negative
        )

    elif file_path.endswith(".docx"):

        return await import_docx(
            file_path=file_path,
            exam=exam,
            subject=subject,
            chapter=chapter,
            marks=marks,
            negative=negative
        )

    elif file_path.endswith(".txt"):

        return await import_txt(
            file_path=file_path,
            exam=exam,
            subject=subject,
            chapter=chapter,
            marks=marks,
            negative=negative
        )

    else:
        raise Exception("Unsupported File Format")