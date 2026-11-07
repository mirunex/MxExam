# ExamGuard

**Pulsuz, oflayn işləyən imtahan sistemi.** Müəllim sual hovuzu yığır, sistem hər tələbə üçün təsadüfi suallar seçir, imtahan vaxtında açılıb vaxtında bağlanır. Bütün məlumatlar müəssisənin öz kompüterində qalır, internet və abunə tələb olunmur.

> **Status:** aktiv inkişaf mərhələsindədir (v0.x). Aşağıdakı "Hazırkı vəziyyət" bölməsi nəyin işlədiyini və nəyin planlaşdırıldığını açıq göstərir.

---

## Niyə ExamGuard?

- **Oflayn və lokal.** Server müəllimin və ya müəssisənin kompüterində `localhost`-da işləyir. Məlumat kənara çıxmır.
- **Pulsuz.** Aylıq abunə və ya xarici xidmət yoxdur.
- **Real imtahan məntiqi.** Sual hovuzundan təsadüfi seçim, qrup üzrə təyinat, başlama vaxtı və avtomatik bağlanma.
- **Ədalətli nəzarət.** Pozuntu halında dərhal kənarlaşdırma yox, xəbərdarlıq rejimi. Yekun qərarı müəllim verir.

## Hazırkı vəziyyət

| Funksiya | Status |
|---|---|
| Rola əsaslı giriş (müəllim / tələbə) | Hazırdır |
| Müəllim paneli: imtahan yaratma və silmə | Hazırdır |
| Sual modeli (test, yazılı, proqramlaşdırma) və yoxlama qaydaları | Hazırdır |
| Sual hovuzu, qruplar, başlama vaxtı (verilənlər bazası) | Hazırdır |
| Müəllim paneli: qrup yaratma, tələbə hesabları | Hazırdır |
| Qrup üzrə imtahan təyinatı və tələbə paneli | Hazırdır |
| PDF-dən sual yükləmə (önizləmə və təsdiq ilə) | İnkişafdadır |
| Tələbənin imtahan verməsi, server vaxtına görə taymer | Planlaşdırılıb |
| Tab dəyişməsinin izlənməsi, xəbərdarlıq sayğacı | Planlaşdırılıb |
| Proqramlaşdırma sualları (kod redaktoru, testlər, qismən bal) | Planlaşdırılıb |
| Canlı monitor və nəticələr cədvəli | Planlaşdırılıb |
| Kamera əsaslı nəzarət | v2.0 üçün araşdırılır |

## Əsas imkanlar

**Müəllim üçün**
- Sinif qruplarını bir dəfə yaratmaq (məs. `2445a`) və tələbə hesablarını özünün əlavə etməsi
- İmtahan üçün böyük sual hovuzu yığmaq (məs. 300 test sualı)
- Hər tələbəyə hovuzdan neçə sual düşəcəyini seçmək (məs. 50)
- İmtahanı yaradarkən qrup və başlama vaxtı seçmək
- Yazılı cavabları özü qiymətləndirmək

**Tələbə üçün**
- Yalnız öz qrupuna təyin olunmuş imtahanları görmək
- Başlama vaxtından etibarən açılan imtahan, qalan vaxt serverdən hesablanır

**Sual növləri**
- **Test** (A, B, C, D): düzgün cavab tam bal verir
- **Yazılı**: müəllim yoxlayır
- **Proqramlaşdırma** (Python): testlər və kodun quruluşu üzrə qismən bal, ən yaxşı cəhd hesablanır

## Texnologiyalar

| Təbəqə | Texnologiya |
|---|---|
| Backend | Python 3, Django |
| Verilənlər bazası | SQLite |
| Frontend | HTML, CSS (Bootstrap 5), JavaScript |
| Planlaşdırılan | Monaco Editor (kod sualları), `pypdf`/`pdfplumber` (PDF oxuma), `ast` (kodun quruluşunu yoxlama) |

Layihədə kod strukturu üçün dizayn patternləri istifadə olunur: **Factory** (sualların yaradılması) və **Observer** (pozuntuların izlənməsi).

## Quraşdırma (Windows)

Tələblər: Python 3.11+ və Git.

```bash
git clone <repo-ünvanı>
cd ExamGuard

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Sonra brauzerdə `http://127.0.0.1:8000/` ünvanını aç.

**Müəllim hesabı:** hələlik admin paneldən yaradılır (`http://127.0.0.1:8000/admin/`). İstifadəçi yaradanda **Role** sahəsini `teacher` seç. Qrup və tələbə idarəetməsi müəllim panelinə əlavə edildikdən sonra bu addım sadələşəcək.

## Layihə strukturu

```
ExamGuard/
├── manage.py
├── examguard/        layihə ayarları və əsas URL-lər
├── core/             modellər, formlar, view-lar
│   ├── models/       User, Exam, Question, Group
│   └── patterns/     Factory, Observer
├── templates/        HTML şablonları
└── static/           CSS, JS, şəkillər
```

## Yol xəritəsi

1. Müəllim paneli: qruplar, tələbə hesabları, imtahan təyinatı
2. PDF-dən sual yükləmə
3. Tələbənin imtahan verməsi və taymer
4. Tab izləmə və xəbərdarlıq rejimi
5. Canlı monitor və nəticələr cədvəli
6. Proqramlaşdırma sualları
7. v2.0: kamera əsaslı nəzarətin yenidən dəyərləndirilməsi

## Məxfilik və təhlükəsizlik

- Bütün məlumatlar yerli `db.sqlite3` faylında saxlanılır, xarici serverə göndərilmir.
- Şifrələr Django-nun daxili mexanizmi ilə hash edilir.
- Müəllim və tələbə səhifələri rol yoxlaması ilə qorunur.
- `db.sqlite3` və `.env` faylları repozitoriyaya əlavə edilmir.

## Töhfə

Təkliflər və xəta bildirişləri üçün GitHub Issues bölməsindən istifadə edin.

## Lisenziya

Lisenziya hələ müəyyən edilməyib.
