import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TIME_LIMIT = 5        # Python üçün saniyə
JAVA_TIME_LIMIT = 10  # Java üçün saniyə (JVM + tərtib daxil)
HARNESS = "#HARNESS\n"
LANGUAGES = ('python', 'java')


def _python_exe():
    """Həqiqi Python faylını tapır (serverdə sys.executable uwsgi ola bilər)."""
    exe = sys.executable
    if exe and os.path.basename(exe).lower().startswith('python'):
        return exe
    for base in (sys.prefix, sys.exec_prefix):
        candidate = os.path.join(base, 'bin', 'python')
        if os.path.exists(candidate):
            return candidate
    return shutil.which('python3') or shutil.which('python') or 'python3'


def _java_exe():
    import glob, os
    exe = shutil.which('java')
    if exe:
        return exe
    home = os.environ.get('JAVA_HOME')
    if home and os.path.exists(os.path.join(home, 'bin', 'java.exe')):
        return os.path.join(home, 'bin', 'java.exe')
    if home and os.path.exists(os.path.join(home, 'bin', 'java')):
        return os.path.join(home, 'bin', 'java')
    pats = [os.path.expanduser(r'~\.jdks\*\bin\java.exe'),
            r'C:\Program Files\Java\*\bin\java.exe',
            r'C:\Program Files\Eclipse Adoptium\*\bin\java.exe',
            r'C:\Program Files\Microsoft\*\bin\java.exe']
    for p in pats:
        found = sorted(glob.glob(p))
        if found:
            return found[-1]
    return 'java'


def _run_python(code, input_data):
    stdin = input_data
    if input_data.startswith(HARNESS):
        # sinif tapşırığı: gizli test kodu tələbənin koduna əlavə olunur
        code = code.rstrip("\n") + "\n\n" + input_data[len(HARNESS):]
        stdin = ""
    with tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp) / "solution.py"
        file.write_text(code, encoding="utf-8")
        try:
            r = subprocess.run(
                [_python_exe(), "-I", "-X", "utf8", str(file)],
                input=stdin, capture_output=True, text=True,
                encoding="utf-8", timeout=TIME_LIMIT, cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return "", "Vaxt limiti aşıldı"
    return r.stdout.strip(), r.stderr.strip()


def _clean_java_error(text, tmp):
    text = text.replace(str(tmp) + os.sep, '').replace(str(tmp), '')
    lines = [ln for ln in text.splitlines() if not ln.startswith('Picked up ')]
    return "\n".join(lines).strip()[:2000]


def _run_java(code, input_data):
    stdin = input_data
    if input_data.startswith(HARNESS):
        stdin = input_data[len(HARNESS):]
    with tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp) / "Main.java"
        file.write_text(code, encoding="utf-8")
        try:
            r = subprocess.run(
                [_java_exe(), "-Xmx256m", "-Xss16m", "-XX:+UseSerialGC", "-XX:TieredStopAtLevel=1",
                 "-Dfile.encoding=UTF-8", str(file)],
                input=stdin, capture_output=True, text=True,
                encoding="utf-8", timeout=JAVA_TIME_LIMIT, cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return "", "Vaxt limiti aşıldı"
        except FileNotFoundError:
            return "", "Serverdə Java tapılmadı"
        # Java xəbərdarlıqları stderr-ə düşür; yalnız uğursuz çıxışı xəta say
        err = _clean_java_error(r.stderr, tmp) if r.returncode != 0 else ""
        if r.returncode != 0 and not err:
            err = f"Proqram {r.returncode} kodu ilə bitdi"
    return r.stdout.strip(), err


def run_code(code, input_data="", language="python"):
    """Kodu işə salır. (nəticə, xəta) qaytarır."""
    if language == 'java':
        return _run_java(code, input_data)
    return _run_python(code, input_data)


def run_python(code, input_data=""):
    """Köhnə ad (geriyə uyğunluq üçün)."""
    return run_code(code, input_data, 'python')


def check_task(task, code):
    """Gizli testləri yoxlayır. (keçən, ümumi) qaytarır.

    Nümunə (görünən) test balda nəzərə alınmır; gizli test yoxdursa hamısı sayılır.
    """
    tests = list(task.test_cases.filter(is_hidden=True).order_by('id'))
    if not tests:
        tests = list(task.test_cases.order_by('id'))
    language = getattr(task, 'language', 'python')
    passed = 0
    for t in tests:
        out, err = run_code(code, t.input_data, language)
        if not err and out == t.expected_output.strip():
            passed += 1
    return passed, len(tests)


def run_generator(code):
    """Giriş generatoru: sonunda `tests` siyahısı olan Python kodu. (siyahı, xəta) qaytarır."""
    wrapper = code.rstrip("\n") + "\n\nimport json as _j\nprint(_j.dumps([str(x) for x in tests]))\n"
    out, err = _run_python(wrapper, "")
    if err:
        return [], err
    try:
        import json
        return json.loads(out.splitlines()[-1]), ""
    except Exception:
        return [], "Generator `tests` siyahısı qaytarmadı"