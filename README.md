# Downloads Organizer

منظّم ذكي وبسيط لمجلد التنزيلات، مكتوب بلغة Python، يقوم بفرز الملفات تلقائيًا حسب نوعها، مع واجهة رسومية متعددة التبويبات لإدارة التصنيفات والإعدادات بسهولة.

> **المنصة الأساسية:** Windows
**اللغة:** Python 3.10 أو أحدث
**الواجهة:** Tkinter / ttk
**المراقبة اللحظية:** watchdog

---

## المحتويات

- [فكرة المشروع](#%D9%81%D9%83%D8%B1%D8%A9-%D8%A7%D9%84%D9%85%D8%B4%D8%B1%D9%88%D8%B9)

- [المميزات](#%D8%A7%D9%84%D9%85%D9%85%D9%8A%D8%B2%D8%A7%D8%AA)

- [شكل المشروع](#%D8%B4%D9%83%D9%84-%D8%A7%D9%84%D9%85%D8%B4%D8%B1%D9%88%D8%B9)

- [المتطلبات](#%D8%A7%D9%84%D9%85%D8%AA%D8%B7%D9%84%D8%A8%D8%A7%D8%AA)

- [التثبيت](#%D8%A7%D9%84%D8%AA%D8%AB%D8%A8%D9%8A%D8%AA)

- [تشغيل الواجهة الرسومية](#%D8%AA%D8%B4%D8%BA%D9%8A%D9%84-%D8%A7%D9%84%D9%88%D8%A7%D8%AC%D9%87%D8%A9-%D8%A7%D9%84%D8%B1%D8%B3%D9%88%D9%85%D9%8A%D8%A9)

- [استخدام الواجهة](#%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D8%A7%D9%84%D9%88%D8%A7%D8%AC%D9%87%D8%A9)

- [تشغيل الأوامر من PowerShell](#%D8%AA%D8%B4%D8%BA%D9%8A%D9%84-%D8%A7%D9%84%D8%A3%D9%88%D8%A7%D9%85%D8%B1-%D9%85%D9%86-powershell)

- [التشغيل التلقائي مع Windows](#%D8%A7%D9%84%D8%AA%D8%B4%D8%BA%D9%8A%D9%84-%D8%A7%D9%84%D8%AA%D9%84%D9%82%D8%A7%D8%A6%D9%8A-%D9%85%D8%B9-windows)

- [إدارة التصنيفات](#%D8%A5%D8%AF%D8%A7%D8%B1%D8%A9-%D8%A7%D9%84%D8%AA%D8%B5%D9%86%D9%8A%D9%81%D8%A7%D8%AA)

- [ملف الإعدادات configjson](#%D9%85%D9%84%D9%81-%D8%A7%D9%84%D8%A5%D8%B9%D8%AF%D8%A7%D8%AF%D8%A7%D8%AA-configjson)

- [التعامل مع الملفات المكررة](#%D8%A7%D9%84%D8%AA%D8%B9%D8%A7%D9%85%D9%84-%D9%85%D8%B9-%D8%A7%D9%84%D9%85%D9%84%D9%81%D8%A7%D8%AA-%D8%A7%D9%84%D9%85%D9%83%D8%B1%D8%B1%D8%A9)

- [سجل العمليات](#%D8%B3%D8%AC%D9%84-%D8%A7%D9%84%D8%B9%D9%85%D9%84%D9%8A%D8%A7%D8%AA)

- [إنشاء اختصار على سطح المكتب](#%D8%A5%D9%86%D8%B4%D8%A7%D8%A1-%D8%A7%D8%AE%D8%AA%D8%B5%D8%A7%D8%B1-%D8%B9%D9%84%D9%89-%D8%B3%D8%B7%D8%AD-%D8%A7%D9%84%D9%85%D9%83%D8%AA%D8%A8)

- [استكشاف الأخطاء وإصلاحها](#%D8%A7%D8%B3%D8%AA%D9%83%D8%B4%D8%A7%D9%81-%D8%A7%D9%84%D8%A3%D8%AE%D8%B7%D8%A7%D8%A1-%D9%88%D8%A5%D8%B5%D9%84%D8%A7%D8%AD%D9%87%D8%A7)

- [تنبيهات مهمة](#%D8%AA%D9%86%D8%A8%D9%8A%D9%87%D8%A7%D8%AA-%D9%85%D9%87%D9%85%D8%A9)[](#%D8%AA%D8%B1%D8%AE%D9%8A%D8%B5-%D8%A7%D9%84%D9%85%D8%B4%D8%B1%D9%88%D8%B9)

---

## فكرة المشروع

يقوم البرنامج بمراقبة مجلد `Downloads`، ثم ينقل الملفات إلى مجلدات منظمة حسب امتداد الملف.

مثال:

```
Downloads/
├── صورة.jpg       → Images/Photos/صورة.jpg
├── ملف.pdf        → Documents/PDF/ملف.pdf
├── ملف.docx       → Documents/Word/ملف.docx
├── فيديو.mp4      → Media/Video/فيديو.mp4
├── أغنية.mp3      → Media/Audio/أغنية.mp3
├── برنامج.exe     → Software/Installers/برنامج.exe
└── ملف.zip        → Archives/ملف.zip
```

البرنامج يعمل بطريقتين:

1. **فرز مرة واحدة:** تنظيم الملفات الموجودة حاليًا.

1. **مراقبة مستمرة:** تنظيم الملفات الجديدة تلقائيًا بمجرد اكتمال تنزيلها.

---

## المميزات

- فرز الملفات حسب الامتداد.

- مراقبة مجلد التنزيلات لحظيًا.

- انتظار اكتمال تنزيل الملف قبل نقله.

- واجهة رسومية حديثة باللغة العربية.

- لوحة تحكم للمعاينة والفرز والمراقبة.

- إدارة التصنيفات والامتدادات من الواجهة.

- إضافة تصنيف جديد.

- تعديل أو حذف تصنيف.

- حفظ الإعدادات فورًا في `config.json`.

- تقسيم الملفات حسب السنة والشهر.

- التعامل مع الملفات المكررة بطريقتين.

- دعم التشغيل التلقائي مع Windows.

- تسجيل العمليات في ملف Log.

- دعم أسماء الملفات العربية.

- منع الكتابة فوق الملفات الموجودة.

- خيار المعاينة بدون نقل الملفات.

---

## شكل المشروع

يجب أن يحتوي مجلد المشروع على الملفات التالية:

```
DownloadsOrganizer/
├── downloads_organizer.py
├── downloads_organizer_gui.py
├── install_and_run_downloads_organizer.bat
└── README.md
```

### وظيفة كل ملف

| الملف | الوظيفة |
| --- | --- |
| `downloads_organizer.py` | المحرك الأساسي للفرز والمراقبة |
| `downloads_organizer_gui.py` | الواجهة الرسومية متعددة التبويبات |
| `install_and_run_downloads_organizer.bat` | تثبيت المكتبة وتشغيل الواجهة بسرعة |
| `README.md` | شرح المشروع وطريقة استخدامه |

> يجب أن يبقى الملفان `downloads_organizer.py` و`downloads_organizer_gui.py` في نفس المجلد.

---

## المتطلبات

- Windows 10 أو Windows 11.

- Python 3.10 أو أحدث.

- مكتبة `watchdog`.

- مكوّن `tkinter`، وهو يأتي عادةً مع تثبيت Python على Windows.

### التحقق من Python

افتح PowerShell ونفّذ:

```
python --version
```

يُفترض أن تظهر نتيجة مشابهة:

```
Python 3.14.0
```

إذا لم يتعرف Windows على الأمر `python`، ثبّت Python من الموقع الرسمي:

[https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

أثناء التثبيت فعّل الخيار:

```
Add Python to PATH
```

وتأكد من تثبيت:

```
tcl/tk and IDLE
```

---

## التثبيت

### 1. إنشاء مجلد المشروع

يمكن استخدام المجلد التالي:

```
C:\Tools
```

أنشئه من PowerShell إذا لم يكن موجودًا:

```
New-Item -ItemType Directory -Force C:\Tools
```

### 2. نسخ ملفات المشروع

ضع الملفات داخل:

```
C:\Tools
```

بحيث يصبح المسار مثلًا:

```
C:\Tools\downloads_organizer.py
C:\Tools\downloads_organizer_gui.py
```

### 3. تثبيت watchdog

نفّذ:

```
python -m pip install watchdog
```

إذا ظهرت الرسالة التالية، فهذا يعني أن المكتبة مثبتة بالفعل:

```
Requirement already satisfied: watchdog
```

### 4. اختبار tkinter

```
python -c "import tkinter; print('TKINTER يعمل' )"
```

إذا ظهرت:

```
TKINTER يعمل
```

فإن الواجهة جاهزة للتشغيل.

---

## تشغيل الواجهة الرسومية

انتقل إلى مجلد المشروع:

```
Set-Location C:\Tools
```

ثم شغّل الواجهة:

```
python .\downloads_organizer_gui.py
```

يمكن أيضًا تشغيلها بالنقر مرتين على الملف:

```
install_and_run_downloads_organizer.bat
```

> لا تغلق نافذة PowerShell أثناء تشغيل الواجهة من خلالها. أغلق الواجهة من زر `X` عند الانتهاء.

---

## استخدام الواجهة

### تبويب لوحة التحكم

يحتوي على:

- **اختيار مجلد:** تحديد Downloads أو مجلد آخر.

- **معاينة بدون نقل:** عرض النتائج المتوقعة دون تحريك أي ملف.

- **فرز الملفات الآن:** تنفيذ النقل الفعلي.

- **بدء المراقبة:** مراقبة الملفات الجديدة.

- **إيقاف المراقبة:** إيقاف المراقبة الحالية.

- **فتح السجل:** فتح ملف العمليات.

### الاستخدام الموصى به أول مرة

1. افتح الواجهة.

1. اضغط **معاينة بدون نقل**.

1. راجع مسارات الملفات الظاهرة في سجل العمليات.

1. إذا كانت النتائج صحيحة، اضغط **فرز الملفات الآن**.

1. بعد ذلك فعّل التشغيل التلقائي مع Windows.

### تبويب إدارة التصنيفات

يظهر جدول يحتوي على:

- اسم التصنيف.

- الامتدادات المرتبطة به.

- عدد الامتدادات.

الأزرار المتاحة:

- **إضافة تصنيف:** إنشاء تصنيف جديد.

- **تعديل المحدد:** تعديل اسم التصنيف أو امتداداته.

- **حذف المحدد:** حذف التصنيف من الإعدادات، دون حذف الملفات الموجودة.

- **إعادة تحميل:** قراءة الإعدادات من جديد.

مثال لإضافة تصنيف:

```
اسم التصنيف: Design/3D
الامتدادات: .blend, .obj, .fbx, .stl
```

### تبويب الإعدادات

يمكن تفعيل:

- التقسيم حسب السنة والشهر.

- نقل المكرر إلى `_Duplicates`.

- أو إضافة رقم تسلسلي مثل `(1)`.

يتم حفظ التعديلات تلقائيًا.

---

## تشغيل الأوامر من PowerShell

انتقل أولًا إلى مجلد المشروع:

```
Set-Location C:\Tools
```

### معاينة بدون نقل

```
python .\downloads_organizer.py --dry-run --once
```

هذا الأمر يعرض ما سيحدث دون نقل أي ملف.

### فرز الملفات الحالية

```
python .\downloads_organizer.py --once
```

### تشغيل المراقبة المستمرة يدويًا

```
python .\downloads_organizer.py
```

تستمر المراقبة حتى تضغط:

```
Ctrl + C
```

### استخدام مجلد مختلف

```
python .\downloads_organizer.py --path "C:\Users\Admin\Desktop\MyFiles" --once
```

### عرض المساعدة

```
python .\downloads_organizer.py --help
```

---

## التشغيل التلقائي مع Windows

لتشغيل المحرك تلقائيًا عند تسجيل الدخول إلى Windows:

```
Set-Location C:\Tools
python .\downloads_organizer.py --install
```

سينشئ البرنامج ملفًا في مجلد Startup الخاص بالمستخدم الحالي.

### التأكد من التفعيل

```
$startup = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\DownloadsOrganizer.vbs"
Test-Path $startup
```

إذا ظهرت:

```
True
```

فالتشغيل التلقائي مفعّل.

### اختبار التشغيل بعد إعادة تشغيل الكمبيوتر

1. أعد تشغيل Windows.

1. انتظر حتى يظهر سطح المكتب.

1. افتح PowerShell.

1. نفّذ:

```
Get-Process pythonw -ErrorAction SilentlyContinue
```

إذا ظهرت عملية `pythonw.exe`، فالمحرك يعمل في الخلفية.

يمكن اختبار البرنامج بتنزيل صورة أو ملف ZIP جديد، ثم الانتظار بضع ثوانٍ.

### إلغاء التشغيل التلقائي

```
Set-Location C:\Tools
python .\downloads_organizer.py --uninstall
```

> الواجهة الرسومية والمحرك شيئان مختلفان. لا تحتاج إلى إبقاء الواجهة مفتوحة حتى يعمل الفرز التلقائي.

---

## إدارة التصنيفات

يمكن تعديل التصنيفات من الواجهة، أو تعديل ملف الإعدادات مباشرة.

### مكان ملف الإعدادات

```
%LOCALAPPDATA%\DownloadsOrganizer\config.json
```

لفتحه:

```
notepad "$env:LOCALAPPDATA\DownloadsOrganizer\config.json"
```

### مثال على ملف إعدادات

```json
{
  "version": 2,
  "categories": {
    "Images/Photos": [
      ".jpg",
      ".jpeg",
      ".png",
      ".webp",
      ".jfif"
    ],
    "Documents/PDF": [
      ".pdf"
    ],
    "Design/3D": [
      ".blend",
      ".obj",
      ".fbx",
      ".stl"
    ]
  },
  "group_by_year_month": false,
  "duplicate_mode": "duplicates_folder",
  "other_folder": "Other",
  "duplicates_folder": "_Duplicates"
}
```

### قواعد مهمة لكتابة الامتدادات

- يجب كتابة الامتداد بنقطة، مثل `.pdf`.

- يمكن كتابة أكثر من امتداد في قائمة.

- لا تضع امتدادًا واحدًا في تصنيفين مختلفين؛ سيستخدم البرنامج آخر تصنيف يقرأه.

- يُفضل استخدام أسماء مجلدات باللغة الإنجليزية مثل `Images/Photos` لتقليل مشاكل التوافق.

---

## التعامل مع الملفات المكررة

يدعم البرنامج طريقتين:

### نقل إلى مجلد `_Duplicates`

```json
"duplicate_mode": "duplicates_folder"
```

إذا كان الملف مطابقًا تمامًا للملف الموجود، سينقل إلى:

```
_Duplicates
```

### إضافة رقم تسلسلي

```json
"duplicate_mode": "serial"
```

في هذه الحالة يصبح الاسم مثلًا:

```
report.pdf
report (1).pdf
report (2).pdf
```

---

## التنظيم حسب التاريخ

عند تفعيل:

```json
"group_by_year_month": true
```

ستصبح البنية مثل:

```
Images/
└── Photos/
    └── 2026-10/
        └── image.jpg
```

وعند تعطيله:

```json
"group_by_year_month": false
```

ستصبح:

```
Images/
└── Photos/
    └── image.jpg
```

يمكن تغيير الخيار من تبويب **الإعدادات** دون تعديل الملف يدويًا.

---

## سجل العمليات

يُحفظ السجل في:

```
%LOCALAPPDATA%\DownloadsOrganizer\organizer.log
```

### فتح السجل باستخدام Notepad

```
notepad "$env:LOCALAPPDATA\DownloadsOrganizer\organizer.log"
```

### عرض آخر 30 سطرًا

```
Get-Content "$env:LOCALAPPDATA\DownloadsOrganizer\organizer.log" -Tail 30
```

### متابعة السجل لحظيًا

```
Get-Content "$env:LOCALAPPDATA\DownloadsOrganizer\organizer.log" -Wait
```

لإيقاف المتابعة:

```
Ctrl + C
```

---

## إنشاء اختصار على سطح المكتب

يمكن إنشاء Shortcut للواجهة من PowerShell باستخدام الكود التالي:

```
$python = (Get-Command python).Source
$pythonw = Join-Path (Split-Path $python) "pythonw.exe"

if (-not (Test-Path $pythonw)) {
    $pythonw = $python
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Downloads Organizer.lnk"

$ws = New-Object -ComObject WScript.Shell
$shortcut = $ws.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $pythonw
$shortcut.Arguments = '"C:\Tools\downloads_organizer_gui.py"'
$shortcut.WorkingDirectory = "C:\Tools"
$shortcut.Description = "فتح واجهة Downloads Organizer"
$shortcut.IconLocation = "$pythonw,0"
$shortcut.Save()
```

سيظهر اختصار باسم:

```
Downloads Organizer
```

بعد ذلك يمكن فتح الواجهة بالنقر مرتين على الاختصار.

---

## استكشاف الأخطاء وإصلاحها

### الخطأ: `No module named watchdog`

نفّذ:

```
python -m pip install watchdog
```

### الخطأ: `No module named tkinter`

أعد تثبيت Python وتأكد من اختيار:

```
tcl/tk and IDLE
```

ثم اختبر:

```
python -c "import tkinter; print('TKINTER يعمل')"
```

### الخطأ: `نسخة أخرى تعمل بالفعل`

هذا يعني أن نسخة أخرى من المحرك تعمل بالفعل، غالبًا من التشغيل التلقائي.

تحقق من العمليات:

```
Get-Process python, pythonw -ErrorAction SilentlyContinue
```

لا تشغّل نسخة مراقبة ثانية يدويًا. استخدم الواجهة لإدارة الإعدادات فقط، أو أوقف النسخة الحالية قبل تشغيل نسخة جديدة.

### الواجهة لا تظهر

تأكد من تشغيلها من مجلد المشروع:

```
Set-Location C:\Tools
python .\downloads_organizer_gui.py
```

وتحقق من وجود الملفين:

```
Get-ChildItem C:\Tools\downloads_organizer*
```

### البرنامج لا ينقل ملفًا

تحقق من التالي:

- الملف ليس داخل مجلد فرعي؛ المراقبة غير تكرارية.

- الملف انتهى من التحميل.

- امتداد الملف موجود في التصنيفات.

- راجع ملف السجل.

- استخدم المعاينة:

```
python .\downloads_organizer.py --dry-run --once
```

### الملف ذهب إلى `Other`

هذا يعني أن امتداده غير موجود في التصنيفات. أضفه من تبويب **إدارة التصنيفات** أو داخل `config.json`.

مثال:

```json
"Images/Photos": [
  ".jpg",
  ".png",
  ".jfif"
]
```

### توقّف البرنامج أثناء التشغيل

البرنامج ينتظر ثبات حجم الملف للتأكد من انتهاء التنزيل. قد يستغرق ذلك بضع ثوانٍ، خصوصًا مع الملفات الكبيرة.

---

## تنبيهات مهمة

- البرنامج ينقل الملفات ولا يحذفها.

- استخدم المعاينة قبل الفرز الفعلي، خصوصًا بعد تعديل التصنيفات.

- احتفظ بنسخة احتياطية من الملفات المهمة.

- لا تستخدم البرنامج لتنظيم مجلد يحتوي على ملفات النظام.

- لا تضع ملف `config.json` بصياغة JSON غير صحيحة.

- لا تشغّل أكثر من نسخة مراقبة في نفس الوقت.

- انتبه إلى الملفات الحساسة مثل مفاتيح API وكلمات المرور.

- إذا كان لديك ملف مثل `api-keys.csv`، راجعه يدويًا واحفظه في مكان آمن.

- لا ترفع ملفات السجل أو الإعدادات إلى GitHub إذا كانت تحتوي على بيانات خاصة.

### ملفات يُفضل إضافتها إلى `.gitignore`

```
__pycache__/
*.pyc
.env
organizer.log
config.json
.DS_Store
```

---

## التطوير والمساهمة

لإضافة تصنيف جديد، يمكنك تعديل `DEFAULT_CATEGORIES` داخل `downloads_organizer.py`، أو الأفضل استخدام الواجهة الرسومية حتى يتم حفظ التعديل في `config.json`.

قبل إرسال أي تعديل:

1. شغّل فحص الصياغة:

```
python -m py_compile downloads_organizer.py downloads_organizer_gui.py
```

1. اختبر المعاينة:

```
python .\downloads_organizer.py --dry-run --once
```

1. جرّب على مجلد اختبار وليس على ملفات مهمة.

[](https://opensource.org/license/mit)

---

## ملخص سريع

```
# الانتقال إلى المشروع
Set-Location C:\Tools

# تثبيت المتطلبات
python -m pip install watchdog

# تشغيل الواجهة
python .\downloads_organizer_gui.py

# معاينة بدون نقل
python .\downloads_organizer.py --dry-run --once

# فرز الملفات الحالية
python .\downloads_organizer.py --once

# تفعيل التشغيل مع Windows
python .\downloads_organizer.py --install

# فتح السجل
notepad "$env:LOCALAPPDATA\DownloadsOrganizer\organizer.log"
```

---

**تم إنشاء المشروع بهدف جعل تنظيم مجلد التنزيلات أسهل وأكثر وضوحًا، مع الحفاظ على إمكانية التحكم الكامل في التصنيفات والإعدادات.**

