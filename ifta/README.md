# مشروع مطابقة معيار ابن المجدي ببيانات دار الإفتاء المصرية

| الملف | المضمون |
|---|---|
| `template/ifta_data_template.xlsx` | قالب إدخال قرارات دار الإفتاء: صفٌّ لكل شهر هجري |
| `majdi_engine.py` | حساب متغيرات ابن المجدي ومعيار عودة لأي تاريخ وموضع (Astronomy Engine) |
| `run_ifta.py` | قراءة البيانات، واستنتاج نتيجة تحري مساء 29 من أطوال الشهور، والمطابقة، واستخراج معيار دار الإفتاء |
| `make_template.py` | إنشاء القالب، والبيانات التجريبية (`--demo`) |
| `demo/` | **بيانات تجريبية مولّدة من معيار عودة — ليست بيانات دار الإفتاء** — ونتائج تشغيل البرنامج عليها |

منهج المشروع مفصّل في `study/ibn_al_majdi_ifta_project.pdf`.

```bash
pip install astronomy-engine openpyxl numpy matplotlib
```

```bash
python3 ifta/run_ifta.py ifta_data.xlsx ifta_results
```

```bash
python3 ifta/run_ifta.py ifta_data.xlsx ifta_results_vision_only --exclude-calc
```
