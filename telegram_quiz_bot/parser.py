import re
import docx

OPTION_RE = re.compile(r'^\s*\(([a-zA-Z])\)\s*(.*)$')
ANSWER_RE = re.compile(r'^\s*Answer\s*:\s*([a-zA-Z](?:\s*,\s*[a-zA-Z])*)', re.IGNORECASE)


def read_text_from_file(path):
    """Reads plain text out of a .txt or .docx file."""
    if path.lower().endswith(".docx"):
        doc = docx.Document(path)
        lines = [p.text for p in doc.paragraphs]
        return "\n".join(lines)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse_quiz_text(text):
    """
    Parses quiz text made of blocks like:

        Question: SI unit of electric current is
        (a) Volt
        (b) Ohm
        (c) Ampere
        (d) Watt
        Answer: c

    Supports:
      - any number of options >= 2 (not fixed to a/b/c/d)
      - multiple correct answers, e.g. "Answer: c,a"
    Question numbering is assigned automatically by the bot, not read from
    the file.

    Returns (questions, errors):
      questions -> list of {"question": str, "options": [str, ...], "correct_indices": [int, ...]}
      errors    -> list of human readable strings describing skipped blocks
    """
    questions = []
    errors = []

    blocks = re.split(r"(?im)^\s*Question\s*:\s*", text)
    blocks = [b for b in blocks[1:] if b.strip()]

    for idx, block in enumerate(blocks, start=1):
        try:
            questions.append(_parse_block(block))
        except ValueError as e:
            errors.append(f"Question {idx}: {e}")

    return questions, errors


def _parse_block(block):
    lines = [l.rstrip() for l in block.splitlines()]
    i, n = 0, len(lines)
    question_lines = []

    while i < n:
        if OPTION_RE.match(lines[i]):
            break
        if lines[i].strip():
            question_lines.append(lines[i].strip())
        i += 1

    if not question_lines:
        raise ValueError("no question text found")
    question_text = " ".join(question_lines)

    options = {}  # letter -> text, insertion order preserved
    answer_letters = None

    while i < n:
        line = lines[i]
        m = OPTION_RE.match(line)
        am = ANSWER_RE.match(line)
        if m:
            options[m.group(1).lower()] = m.group(2).strip()
        elif am:
            answer_letters = [re.sub(r"[^a-zA-Z]", "", tok).lower() for tok in am.group(1).split(",")]
        i += 1

    if len(options) < 2:
        raise ValueError("needs at least 2 options")
    if not answer_letters:
        raise ValueError("missing 'Answer:' line")

    letters_in_order = list(options.keys())
    options_list = [options[l] for l in letters_in_order]

    correct_indices = []
    for letter in answer_letters:
        if letter not in options:
            raise ValueError(f"answer letter '{letter}' does not match any option in this question")
        correct_indices.append(letters_in_order.index(letter))

    return {
        "question": question_text,
        "options": options_list,
        "correct_indices": sorted(set(correct_indices)),
    }
