from pypdf import PdfReader
from core.services.pdf_import import parse_test_questions

reader = PdfReader("test_suallar.pdf")

full_text = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        full_text += text + "\n"

questions, errors = parse_test_questions(full_text)

print(f"Düzgün sual sayı: {len(questions)}")
print(f"Xətaların siyahısı: {errors}\n")

if questions:
    print("İlk sualın lüğət forması (questions[0]):")
    print(questions[0])