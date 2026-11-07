import re
def parse_test_questions(text):
    questions = []
    errors = []
    number = 0
    
    current_q = {}
    lines = text.split("\n")

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        if clean_line[0].isdigit() and ". " in clean_line:
            number += 1
            current_q = {
                'text': clean_line.split(". ", 1)[1].strip(),
                'option_a': '',
                'option_b': '',
                'option_c': '',
                'option_d': '',
                'correct_option': ''
            }

        elif clean_line.startswith("A)"):
            current_q['option_a'] = clean_line[2:].strip()
        elif clean_line.startswith("B)"):
            current_q['option_b'] = clean_line[2:].strip()
        elif clean_line.startswith("C)"):
            current_q['option_c'] = clean_line[2:].strip()
        elif clean_line.startswith("D)"):
            current_q['option_d'] = clean_line[2:].strip()

        elif clean_line.startswith("Cavab:"):
            current_q['correct_option'] = clean_line.split(":")[1].strip().upper()

            if not all([current_q['option_a'], current_q['option_b'], current_q['option_c'], current_q['option_d']]):
                errors.append(f"Sual {number}: bəzi variantı çatışmır")
            else:
                questions.append(current_q)

            current_q = {}

    return questions, errors


def parse_written_questions(text):
    questions = []
    errors = []
    current = None

    def finish(q):
        if q is None:
            return
        body = " ".join(q['parts']).strip()
        points = 1.0
        m = re.search(r'\(\s*(\d+(?:[.,]\d+)?)\s*bal\s*\)\s*$', body, re.IGNORECASE)
        if m:
            points = float(m.group(1).replace(',', '.'))
            body = body[:m.start()].strip()
        if not body:
            errors.append(f"Sual {q['number']}: mətn boşdur")
            return
        questions.append({'text': body, 'points': points})

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(\d+)[.)]\s+(.*)$', line)
        if m:
            finish(current)
            current = {'number': m.group(1), 'parts': [m.group(2)]}
        elif current is not None:
            current['parts'].append(line)

    finish(current)

    if not questions and not errors:
        errors.append("Heç bir sual tapılmadı. Format: '1. Sualın mətni (5 bal)'")
    return questions, errors