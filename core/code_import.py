import re

FOOTER = re.compile(r'.*Səhifə\s*\d+\s*$')


def parse_code_tasks(text):
    tasks = []
    errors = []
    cur = None
    mode = None  # 'text' | 'code' | 'inputs'

    def finish(t):
        if t is None:
            return
        desc = "\n".join(t['desc']).strip()
        code = "\n".join(t['code']).strip("\n")
        if not desc:
            errors.append(f"Tapşırıq {t['number']}: mətn boşdur")
            return
        if not code.strip():
            errors.append(f"Tapşırıq {t['number']}: 'Kod:' hissəsi boşdur")
            return
        points = 10.0
        m = re.search(r'\(\s*(\d+(?:[.,]\d+)?)\s*bal\s*\)\s*$', desc, re.IGNORECASE)
        if m:
            points = float(m.group(1).replace(',', '.'))
            desc = desc[:m.start()].strip()
        tasks.append({
            'title': desc.split("\n")[0][:80],
            'description': desc,
            'points': points,
            'reference_code': code,
            'starter_code': "\n".join(t['starter']).strip("\n"),
            'inputs': t['inputs'] or [""],
        })

    for raw in text.split("\n"):
        if FOOTER.match(raw.strip()):
            continue
        line = raw.rstrip()
        stripped = line.strip()

        # Yeni tapşırıq: növbəti gözlənilən nömrə ilə başlayan sətir
        m = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        expected = (int(cur['number']) + 1) if cur else 1
        if m and int(m.group(1)) == expected:
            finish(cur)
            cur = {'number': m.group(1), 'desc': [m.group(2)], 'code': [], 'inputs': [], 'starter': []}
            mode = 'text'
            continue

        if cur is None:
            continue

        low = stripped.lower()
        if low in ('başlanğıc:', 'baslangic:', 'başlanğıç:'):
            mode = 'starter'
            continue

        if low == 'kod:':
            mode = 'code'
            continue

        if low == 'test:':
            cur['inputs'].append("#HARNESS\n")
            mode = 'test'
            continue

        if low.startswith('giriş:') or low.startswith('giris:'):
            value = stripped.split(':', 1)[1].strip()
            cur['inputs'].append("\n".join(p.strip() for p in value.split('|')) if value else "")
            mode = 'inputs'
            continue

        if mode == 'text':
            if stripped == '§':
                cur['desc'].append("")
            elif stripped.startswith('~ '):
                cur['desc'][-1] += " " + stripped[2:]
            elif stripped:
                cur['desc'].append(line)
            else:
                cur['desc'].append("")
        elif mode == 'code':
            cur['code'].append(line)
        elif mode == 'test':
            cur['inputs'][-1] += line + "\n"
        elif mode == 'starter':
            cur['starter'].append(line)

    finish(cur)

    if not tasks and not errors:
        errors.append("Heç bir tapşırıq tapılmadı. Format: '1. Mətn (10 bal)', 'Kod:', 'Giriş: ...'")
    return tasks, errors