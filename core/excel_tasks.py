"""Tapşırıq bankı Excel-dən oxunur (şablon: tapsiriq_sablon.xlsx)."""
from openpyxl import load_workbook

HARNESS = "#HARNESS\n"
MAX_TESTS = 12


def _norm(s):
    s = str(s or '').strip()
    s = s.replace('İ', 'i').replace('I', 'i').replace('ı', 'i').lower()
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
        return [], ["Excel faylını oxumaq olmadı (.xlsx olmalıdır)."]

    if 'Problems' in wb.sheetnames:          # akademiya formatı (Problems / Students vərəqləri)
        return _parse_academy(wb['Problems'])

    ws = wb['Tapşırıqlar'] if 'Tapşırıqlar' in wb.sheetnames else wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return [], ["Fayl boşdur."]

    col = {}
    for i, h in enumerate(rows[0]):
        col.setdefault(_norm(h), i)

    def need(name):
        if _norm(name) not in col:
            errors.append(f"Sütun tapılmadı: '{name}'")

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
        pref = f"Sətir {n}"

        lang = _s(get(row, "Dil")).strip().lower()
        if lang not in ('python', 'java'):
            errors.append(f"{pref}: Dil 'python' və ya 'java' olmalıdır.")
        kind = _s(get(row, "Növ")).strip().lower()
        if kind not in ('stdin', 'sinif'):
            errors.append(f"{pref}: Növ 'stdin' və ya 'sinif' olmalıdır.")
        if kind == 'sinif' and lang == 'java':
            errors.append(f"{pref}: Java üçün yalnız 'stdin' növü dəstəklənir.")

        try:
            points = float(_s(get(row, "Bal")).replace(',', '.'))
            if points <= 0:
                raise ValueError
        except ValueError:
            errors.append(f"{pref}: Bal müsbət ədəd olmalıdır.")
            points = 0

        title = _s(get(row, "Başlıq (az)")).strip()
        desc = _nl(get(row, "Təsvir (az)"))
        ref = _nl(get(row, "Düzgün kod"))
        if not title:
            errors.append(f"{pref}: Başlıq (az) boşdur.")
        if not desc:
            errors.append(f"{pref}: Təsvir (az) boşdur.")
        if not ref:
            errors.append(f"{pref}: Düzgün kod boşdur.")

        sample = _nl(get(row, "Nümunə giriş"))
        sample_out = _nl(get(row, "Nümunə çıxış (ixtiyari)"))
        hidden_in = [_nl(get(row, f"Gizli test {k} giriş")) for k in (1, 2, 3)]
        hidden_out = [_nl(get(row, f"Gizli test {k} çıxış (ixtiyari)")) for k in (1, 2, 3)]
        generator = _nl(get(row, "Giriş generatoru (ixtiyari)"))

        if sample == '' and kind == 'sinif':
            errors.append(f"{pref}: Sinif tapşırığında 'Nümunə giriş' (test kodu) boş ola bilməz.")

        entries = [(sample, sample_out or None, False)]
        for hi, ho in zip(hidden_in, hidden_out):
            # giriş sətri boşdursa test atlanır (yalnız stdin üçün boş giriş icazəlidir)
            if hi == '' and ho == '':
                continue
            entries.append((hi, ho or None, True))
        if len(entries) < 2 and not generator:
            errors.append(f"{pref}: Ən azı bir gizli test və ya generator lazımdır.")

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
        errors.append("Heç bir tapşırıq tapılmadı.")
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


def _first_example(examples):
    """Examples sütunundan ilk (giriş, çıxış) cütünü çıxarır."""
    t = examples.replace('```', '')
    if 'Input:' not in t or 'Output:' not in t:
        return None
    a = t.split('Input:', 1)[1]
    inp, out = a.split('Output:', 1)
    out = out.split('Input:')[0]
    return inp.strip('\n'), out.strip('\n')


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
        "        break\n"
        "    elif _cur is not None:\n"
        "        _cur.append(_ln)\n"
        "tests = ['\\n'.join(c) + '\\n' for c in _all]\n"
    )


def _parse_academy(ws):
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        return [], ["Problems vərəqi boşdur."]
    col = {}
    for i, h in enumerate(rows[0]):
        col.setdefault(_norm(h), i)
    errors = []
    for name in ("Title", "Description", "Score", "Solution", "Test Cases"):
        if _norm(name) not in col:
            errors.append(f"Sütun tapılmadı: '{name}'")
    if errors:
        return [], errors

    def get(row, name):
        i = col.get(_norm(name))
        return row[i] if i is not None and i < len(row) else None

    tasks = []
    for n, row in enumerate(rows[1:], start=2):
        if not any(c not in (None, '') for c in row):
            continue
        pref = f"Sətir {n}"
        title_en = _s(get(row, "Title")).strip()
        title_az = _s(get(row, "Title AZ")).strip() or title_en
        title_ru = _s(get(row, "Title RU")).strip()
        d_en = _norm_desc(get(row, "Description"))
        d_az = _norm_desc(get(row, "Description AZ")) or d_en
        d_ru = _norm_desc(get(row, "Description RU"))
        examples = _nl(get(row, "Examples"))
        ref = _nl(get(row, "Solution"))
        gen = _nl(get(row, "Test Cases"))
        try:
            points = float(_s(get(row, "Score")).replace(',', '.'))
            if points <= 0:
                raise ValueError
        except ValueError:
            errors.append(f"{pref}: Score müsbət ədəd olmalıdır.")
            continue
        if not title_en or not d_en or not ref or not gen:
            errors.append(f"{pref}: Title, Description, Solution və Test Cases boş ola bilməz.")
            continue
        ex = _first_example(examples)
        entries = [(ex[0], ex[1], False)] if ex else []
        tasks.append({
            'number': _s(get(row, "Name")).strip() or str(len(tasks) + 1),
            'language': 'python', 'kind': 'stdin',
            'title': title_az[:150], 'title_en': title_en[:150], 'title_ru': title_ru[:150],
            'description': _with_examples(d_az, examples, 'az'),
            'description_en': _with_examples(d_en, examples, 'en'),
            'description_ru': _with_examples(d_ru, examples, 'ru'),
            'starter_code': '', 'reference_code': ref, 'points': points,
            'entries': entries, 'generator': _academy_generator(gen),
        })
    if not tasks and not errors:
        errors.append("Heç bir tapşırıq tapılmadı.")
    return tasks, errors