# JavaScript Cleaner - ניטור אוטומטי

הסקריפט `inject_js_cleaner.py` עכשיו כולל פונקציונליות לניטור אוטומטי של קבצי HTML חדשים.

## פונקציונליות חדשה

### 1. אינטגרציה אוטומטית עם main.py
הסקריפט משולב אוטומטית ב-`main.py` ורץ לפני כל commit. אין צורך להפעיל ניטור ידני!

### 2. זרימת העבודה החדשה
1. **Scraping** - איסוף טקסט מהאתר
2. **LLM Processing** - עיבוד עם מודל השפה
3. **HTML Creation** - יצירת קובץ HTML
4. **Auto-fix** - תיקון עיצוב המאמר
5. **JavaScript Injection** - הזרקת קוד ניקוי אוטומטית
6. **Commit & Push** - שמירה לגיטהאב

### 3. שימוש בסיסי

#### הרצה חד פעמית (כל הקבצים הקיימים):
```bash
python3 inject_js_cleaner.py
```

#### ניטור אוטומטי (לשימוש ידני):
```bash
python3 inject_js_cleaner.py --monitor
```

#### ניטור אוטומטי ללא גיבוי:
```bash
python3 inject_js_cleaner.py --monitor --no-backup
```

### 4. ניהול מתקדם (לשימוש ידני)

#### הפעלת הניטור ברקע:
```bash
python3 start_js_cleaner_monitor.py start
```

#### בדיקת סטטוס הניטור:
```bash
python3 start_js_cleaner_monitor.py status
```

#### עצירת הניטור:
```bash
python3 start_js_cleaner_monitor.py stop
```

#### הפעלה מחדש:
```bash
python3 start_js_cleaner_monitor.py restart
```

### 5. סקריפט Shell פשוט

#### הפעלת ניטור אינטראקטיבי:
```bash
./run_js_cleaner_monitor.sh
```

## איך זה עובד

1. **אינטגרציה אוטומטית**: `main.py` מפעיל את הניקוי אוטומטית לפני commit
2. **ניטור קבצים**: הסקריפט משתמש ב-`watchdog` לנטר שינויים בתיקיית `articles`
3. **זיהוי אוטומטי**: כאשר קובץ HTML חדש נוצר, הסקריפט מזהה אותו אוטומטית
4. **עיבוד**: הסקריפט מזריק את קוד ה-JavaScript הנדרש לקובץ
5. **גיבוי**: נוצר קובץ גיבוי `.bak` (אלא אם כן מוגדר `--no-backup`)
6. **לוגים**: כל הפעולות מתועדות בקובץ `js_cleaner.log`

## קבצי לוג

- `js_cleaner.log` - לוג של פעולות הניקוי
- `js_cleaner_daemon.log` - לוג של הדמון (כאשר מריץ ברקע)
- `js_cleaner_monitor.pid` - קובץ PID לניהול התהליך

## אינטגרציה עם main.py

**חדש!** - אין צורך להפעיל ניטור ידני. `main.py` מפעיל את הניקוי אוטומטית:

```bash
# פשוט הרץ את main.py - הכל אוטומטי!
python3 main.py

# או לטיקר ספציפי
python3 main.py AMD
```

### זרימת העבודה האוטומטית:
1. `main.py` יוצר קובץ HTML חדש
2. `main.py` מפעיל את `inject_js_cleaner.py` על הקובץ החדש
3. `main.py` מבצע commit ו-push
4. הקובץ בגיטהאב כבר נקי ומתוקן!

## דוגמה לשימוש מלא

```bash
# הכל אוטומטי - אין צורך בניטור ידני!
python3 main.py AMD
```

## הערות חשובות

- **אינטגרציה אוטומטית**: `main.py` מפעיל את הניקוי אוטומטית לפני commit
- הניטור עובד רק על קבצי HTML (לא על קבצי `.bak` או `.backup`)
- הסקריפט מונע הזרקה כפולה של קוד JavaScript
- כל קובץ HTML חדש יקבל גיבוי אוטומטי (אלא אם כן מוגדר אחרת)
- הניטור פועל רק על תיקיית `articles` (ניתן לשנות עם `--dir`)

---

## כל פקודות ההרצה (Copy-Paste)

```bash
# הרצה חד פעמית על כל הקבצים הקיימים
python3 inject_js_cleaner.py

# ניטור אוטומטי (אינטראקטיבי) - לשימוש ידני
python3 inject_js_cleaner.py --monitor

# ניטור אוטומטי ללא גיבוי - לשימוש ידני
python3 inject_js_cleaner.py --monitor --no-backup

# ניטור אוטומטי דרך סקריפט shell - לשימוש ידני
./run_js_cleaner_monitor.sh

# הפעלת הניטור ברקע (daemon) - לשימוש ידני
python3 start_js_cleaner_monitor.py start

# בדיקת סטטוס הניטור - לשימוש ידני
python3 start_js_cleaner_monitor.py status

# עצירת הניטור - לשימוש ידני
python3 start_js_cleaner_monitor.py stop

# הפעלה מחדש של הניטור - לשימוש ידני
python3 start_js_cleaner_monitor.py restart

# השימוש המומלץ - הכל אוטומטי!
python3 main.py AMD
``` 