"""Tapşırığın test siyahısını hazırlayır (yalnız çıxışı olmayan testlər üçün kod işlədilir)."""
from core.code_runner import run_code, run_generator

MAX_GENERATED = 12


def build_tests(index, task):
    """task['tests'] = [(giriş, çıxış, gizlidir), ...] doldurur. Xəta siyahısı qaytarır."""
    errors = []
    lang = task.get('language', 'python')
    entries = task.get('entries')

    if entries is None:                    # PDF yolu: ilk test görünür, qalanı gizli
        entries = [(inp, None, i > 0) for i, inp in enumerate(task['inputs'])]

    tests = []
    for inp, out, hidden in entries:
        if out is None:
            out, err = run_code(task['reference_code'], inp, lang)
            if err:
                errors.append(f"Tapşırıq {index}: etalon kod xəta verdi: {err[:150]}")
                return errors
        tests.append((inp, out.strip(), hidden))

    if task.get('generator'):
        generated, err = run_generator(task['generator'])
        if err:
            errors.append(f"Tapşırıq {index}: generator xəta verdi: {err[:150]}")
            return errors
        for inp in generated[:MAX_GENERATED]:
            out, err = run_code(task['reference_code'], inp, lang)
            if err:
                errors.append(f"Tapşırıq {index}: etalon kod generator girişində xəta verdi: {err[:150]}")
                return errors
            tests.append((inp, out, True))

    task['tests'] = tests
    return errors