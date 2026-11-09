"""Tapşırıq bankı Excel-dən oxunur (şablon: tapsiriq_sablon.xlsx)."""
from openpyxl import load_workbook
import re

HARNESS = "#HARNESS\n"
MAX_TESTS = 12


def _norm(s):
    s = str(s or '').strip()
    s = s.replace('İ', 'i').replace('I', 'i').replace('ı', 'i').lower()
    s = re.sub(r'[_\-/()]+', ' ', s)
    return ' '.join(s.split())


def _s(v):
    if v is None:
        return ''
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).replace('\r\n', '\n').replace('\r', '\n')


def _nl(v):
    """Hüceyrə mətnini saxlayır, yalnız kənar boş sətirləri atır."""
    return _s(v).strip('\n')


def parse_tasks_excel(file):
    """(tasks, errors) qaytarır. Tapşırıq strukturu parse_code_tasks ilə uyğundur."""
    errors = []
    try:
        wb = load_workbook(file, data_only=True, read_only=True)
    except Exception:
        return [], ["Could not read the Excel file (it must be .xlsx)."]

    if 'Problems' in wb.sheetnames:          # akademiya formatı (Problems / Students vərəqləri)
        return _parse_academy(wb['Problems'])

    ws = wb['Tapşırıqlar'] if 'Tapşırıqlar' in wb.sheetnames else wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return [], ["The file is empty."]

    col = {}
    for i, h in enumerate(rows[0]):
        col.setdefault(_norm(h), i)

    def need(name):
        if _norm(name) not in col:
            errors.append(f"Column not found: '{name}'")

    for name in ("Dil", "Bal", "Növ", "Başlıq (az)", "Təsvir (az)", "Düzgün kod", "Nümunə giriş"):
        need(name)
    if errors:
        return [], errors

    def get(row, name):
        i = col.get(_norm(name))
        return row[i] if i is not None and i < len(row) else None

    tasks = []
    for n, row in enumerate(rows[1:], start=2):
        if not any(c not in (None, '') for c in row):
            continue
        err_before = len(errors)
        pref = f"Row {n}"

        lang = _s(get(row, "Dil")).strip().lower()
        if lang not in ('python', 'java'):
            errors.append(f"{pref}: Language must be 'python' or 'java'.")
        kind = _s(get(row, "Növ")).strip().lower()
        if kind not in ('stdin', 'sinif'):
            errors.append(f"{pref}: Type must be 'stdin' or 'class'.")
        if kind == 'sinif' and lang == 'java':
            errors.append(f"{pref}: Only 'stdin' tasks are supported for Java.")

        try:
            points = float(_s(get(row, "Bal")).replace(',', '.'))
            if points <= 0:
                raise ValueError
        except ValueError:
            errors.append(f"{pref}: Bal must be a positive number.")
            points = 0

        title = _s(get(row, "Başlıq (az)")).strip()
        desc = _nl(get(row, "Təsvir (az)"))
        ref = _nl(get(row, "Düzgün kod"))
        if not title:
            errors.append(f"{pref}: Title is required.")
        if not desc:
            errors.append(f"{pref}: Description is required.")
        if not ref:
            errors.append(f"{pref}: Reference solution is required.")

        sample = _nl(get(row, "Nümunə giriş"))
        sample_out = _nl(get(row, "Nümunə çıxış (ixtiyari)"))
        hidden_in = [_nl(get(row, f"Gizli test {k} giriş")) for k in (1, 2, 3)]
        hidden_out = [_nl(get(row, f"Gizli test {k} çıxış (ixtiyari)")) for k in (1, 2, 3)]
        generator = _nl(get(row, "Giriş generatoru (ixtiyari)"))

        if sample == '' and kind == 'sinif':
            errors.append(f"{pref}: The sample input (test harness) is required for class-based tasks.")

        entries = [(sample, sample_out or None, False)]
        for hi, ho in zip(hidden_in, hidden_out):
            # giriş sətri boşdursa test atlanır (yalnız stdin üçün boş giriş icazəlidir)
            if hi == '' and ho == '':
                continue
            entries.append((hi, ho or None, True))
        if len(entries) < 2 and not generator:
            errors.append(f"{pref}: Add at least one hidden test or a test generator.")

        if kind == 'sinif':
            entries = [((e[0] if e[0].startswith(HARNESS) else HARNESS + e[0] + "\n"), e[1], e[2])
                       for e in entries]

        if len(errors) > err_before:
            continue

        tasks.append({
            'number': _s(get(row, "№")).strip() or str(len(tasks) + 1),
            'language': lang,
            'kind': kind,
            'title': title[:150],
            'title_en': _s(get(row, "Başlıq (en)")).strip()[:150],
            'title_ru': _s(get(row, "Başlıq (ru)")).strip()[:150],
            'description': desc,
            'description_en': _nl(get(row, "Təsvir (en) (ixtiyari)")),
            'description_ru': _nl(get(row, "Təsvir (ru) (ixtiyari)")),
            'starter_code': _nl(get(row, "Başlanğıc kod (ixtiyari)")),
            'reference_code': ref,
            'points': points,
            'entries': entries[:MAX_TESTS],     # (giriş, çıxış|None, gizlidir)
            'generator': generator,
        })

    if not tasks and not errors:
        errors.append("No tasks were found.")
    return tasks, errors


# ---------------------------------------------------------------- akademiya formatı
_LABELS = {'az': ("Nümunələr", "Giriş:", "Çıxış:"), 'en': ("Examples", "Input:", "Output:"),
           'ru': ("Примеры", "Ввод:", "Вывод:")}


def _norm_desc(text):
    lines = []
    for ln in _nl(text).split('\n'):
        if ln.startswith('### '):
            ln = '## ' + ln[4:]
        lines.append(ln)
    return '\n'.join(lines)


def _with_examples(desc, examples, lang):
    if not desc:
        return ''
    if not examples:
        return desc
    title, i_lbl, o_lbl = _LABELS[lang]
    ex = examples.replace('Input:', i_lbl).replace('Output:', o_lbl)
    return desc + "\n\n## " + title + "\n" + ex


def _all_examples(examples):
    """Examples sütunundan bütün public (giriş, çıxış) cütlərini çıxarır."""
    text = examples.replace('```', '').strip()
    if not text or 'Input:' not in text or 'Output:' not in text:
        return []

    # Prefer the documented multiline format where each label has its own line.
    blocks = re.split(r'(?im)^[ \t]*Input:[ \t]*$', text)
    pairs = []
    for block in blocks:
        parts = re.split(r'(?im)^[ \t]*Output:[ \t]*$', block, maxsplit=1)
        if len(parts) == 2:
            pairs.append((parts[0].strip('\r\n'), parts[1].strip('\r\n')))
    if pairs:
        return pairs

    # Keep accepting older inline labels such as "Input: 1 Output: 2".
    for block in text.split('Input:')[1:]:
        if 'Output:' not in block:
            continue
        inp, out = block.split('Output:', 1)
        pairs.append((inp.strip('\r\n '), out.split('Input:', 1)[0].strip('\r\n ')))
    return pairs


def _academy_generator(code):
    """`INPUT ... END` formatında çap edən generatoru bizim `tests` formatına çevirir."""
    return (
        "import io, contextlib\n"
        "_b = io.StringIO()\n"
        "with contextlib.redirect_stdout(_b):\n"
        f"    exec(compile({code!r}, 'gen', 'exec'), {{}})\n"
        "_all = []\n"
        "_cur = None\n"
        "for _ln in _b.getvalue().split('\\n'):\n"
        "    if _ln == 'INPUT':\n"
        "        if _cur is not None:\n"
        "            _all.append(_cur)\n"
        "        _cur = []\n"
        "    elif _ln == 'END':\n"
        "        if _cur is not None:\n"
        "            _all.append(_cur)\n"
        "        _cur = None\n"
        "    elif _cur is not None:\n"
        "        _cur.append(_ln)\n"
        "tests = ['\\n'.join(c) + '\\n' for c in _all]\n"
    )


def _parse_academy(ws):
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        return [], ["The Problems sheet is empty."]
    col = {}
    for i, h in enumerate(rows[0]):
        col.setdefault(_norm(h), i)
    def get(row, *names):
        for name in names:
            i = col.get(_norm(name))
            if i is not None and i < len(row):
                value = row[i]
                if value is not None and str(value).strip() != '':
                    return value
        return None

    errors = []
    for label, aliases in (
        ('Title (EN)', ('Title EN', 'Title', 'Title English')),
        ('Description (EN)', ('Description EN', 'Description', 'Description English')),
        ('Score', ('Score',)),
        ('Solution', ('Solution',)),
        ('Test Cases', ('Test Cases',)),
    ):
        if not any(_norm(alias) in col for alias in aliases):
            errors.append(f"Column not found: '{label}'")
    if errors:
        return [], errors

    tasks = []
    for n, row in enumerate(rows[1:], start=2):
        if not any(c not in (None, '') for c in row):
            continue
        pref = f"Row {n}"
        title_en = _s(get(row, 'Title EN', 'Title (EN)', 'Title English', 'Title (English)', 'Title')).strip()
        title_az = _s(get(row, 'Title AZ', 'Title (AZ)', 'Title Azerbaijani', 'Başlıq (az)')).strip()
        title_ru = _s(get(row, 'Title RU', 'Title (RU)', 'Title Russian', 'Заголовок RU')).strip()
        title_en = title_en or title_az or title_ru
        title_az = title_az or title_en
        title_ru = title_ru or title_en

        language_raw = _s(get(row, 'Language', 'Programming Language', 'Code Language', 'Dil')).strip().lower()
        if not language_raw or language_raw.startswith('python') or language_raw == 'py':
            language = 'python'
        elif language_raw.startswith('java'):
            language = 'java'
        else:
            language = language_raw
        if language not in ('python', 'java'):
            errors.append(f"{pref}: Language must be Python or Java.")
            continue
        d_en = _norm_desc(get(row, 'Description EN', 'Description (EN)', 'Description English', 'Description (English)', 'Description', 'Təsvir (en)'))
        d_az = _norm_desc(get(row, 'Description AZ', 'Description (AZ)', 'Description Azerbaijani', 'Təsvir (az)')) or d_en
        d_ru = _norm_desc(get(row, 'Description RU', 'Description (RU)', 'Description Russian', 'Описание RU')) or d_en
        examples = _nl(get(row, "Examples"))
        ref = _nl(get(row, "Solution"))
        gen = _nl(get(row, "Test Cases"))
        try:
            points = float(_s(get(row, "Score")).replace(',', '.'))
            if points <= 0:
                raise ValueError
        except ValueError:
            errors.append(f"{pref}: Score must be a positive number.")
            continue
        if not title_en or not d_en or not ref or not gen:
            errors.append(f"{pref}: Title, Description, Solution, and Test Cases are required.")
            continue
        entries = [(inp, out, False) for inp, out in _all_examples(examples)]
        tasks.append({
            'number': _s(get(row, "Name")).strip() or str(len(tasks) + 1),
            'language': language, 'kind': 'stdin',
            'title': title_az[:150], 'title_en': title_en[:150], 'title_ru': title_ru[:150],
            'description': _with_examples(d_az or d_en, examples, 'az'),
            'description_en': _with_examples(d_en, examples, 'en'),
            'description_ru': _with_examples(d_ru, examples, 'ru'),
            'starter_code': _nl(get(row, "Starter Code")), 'reference_code': ref, 'points': points,
            'entries': entries, 'generator': _academy_generator(gen),
        })
    if not tasks and not errors:
        errors.append("No tasks were found.")
    return tasks, errors
