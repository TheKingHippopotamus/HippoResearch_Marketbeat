# JavaScript Cleaner - ניטור אוטומטי

הסקריפט `inject_js_cleaner.py` עכשיו כולל פונקציונליות לניטור אוטומטי של קבצי HTML חדשים.

## פונקציונליות חדשה

### 1. ניטור אוטומטי
הסקריפט יכול לנטר את תיקיית `articles` ולזהות קבצי HTML חדשים באופן אוטומטי. כאשר קובץ HTML חדש נוצר, הסקריפט יבצע את התיקון אוטומטית.

### 2. שימוש בסיסי

#### הרצה חד פעמית (כל הקבצים הקיימים):
```bash
python3 inject_js_cleaner.py
```

#### ניטור אוטומטי:
```bash
python3 inject_js_cleaner.py --monitor
```

#### ניטור אוטומטי ללא גיבוי:
```bash
python3 inject_js_cleaner.py --monitor --no-backup
```

### 3. ניהול מתקדם

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

### 4. סקריפט Shell פשוט

#### הפעלת ניטור אינטראקטיבי:
```bash
./run_js_cleaner_monitor.sh
```

## איך זה עובד

1. **ניטור קבצים**: הסקריפט משתמש ב-`watchdog` לנטר שינויים בתיקיית `articles`
2. **זיהוי אוטומטי**: כאשר קובץ HTML חדש נוצר, הסקריפט מזהה אותו אוטומטית
3. **עיבוד**: הסקריפט מזריק את קוד ה-JavaScript הנדרש לקובץ
4. **גיבוי**: נוצר קובץ גיבוי `.bak` (אלא אם כן מוגדר `--no-backup`)
5. **לוגים**: כל הפעולות מתועדות בקובץ `js_cleaner.log`

## קבצי לוג

- `js_cleaner.log` - לוג של פעולות הניקוי
- `js_cleaner_daemon.log` - לוג של הדמון (כאשר מריץ ברקע)
- `js_cleaner_monitor.pid` - קובץ PID לניהול התהליך

## אינטגרציה עם main.py

כדי שהניטור יעבוד אוטומטית עם `main.py`, הפעל את הניטור לפני הרצת `main.py`:

```bash
# הפעל את הניטור ברקע
python3 start_js_cleaner_monitor.py start

# הרץ את main.py
python3 main.py

# כאשר סיימת, עצור את הניטור
python3 start_js_cleaner_monitor.py stop
```

## דוגמה לשימוש מלא

```bash
# 1. הפעל את הניטור האוטומטי
python3 start_js_cleaner_monitor.py start

# 2. בדוק שהניטור פועל
python3 start_js_cleaner_monitor.py status

# 3. הרץ את main.py (כל קבצי HTML חדשים יטופלו אוטומטית)
python3 main.py

# 4. עצור את הניטור
python3 start_js_cleaner_monitor.py stop
```

## הערות חשובות

- הניטור עובד רק על קבצי HTML (לא על קבצי `.bak` או `.backup`)
- הסקריפט מונע הזרקה כפולה של קוד JavaScript
- כל קובץ HTML חדש יקבל גיבוי אוטומטי (אלא אם כן מוגדר אחרת)
- הניטור פועל רק על תיקיית `articles` (ניתן לשנות עם `--dir`)

---

## כל פקודות ההרצה (Copy-Paste)

```bash
# הרצה חד פעמית על כל הקבצים הקיימים
python3 inject_js_cleaner.py

# ניטור אוטומטי (אינטראקטיבי)
python3 inject_js_cleaner.py --monitor

# ניטור אוטומטי ללא גיבוי
python3 inject_js_cleaner.py --monitor --no-backup

# ניטור אוטומטי דרך סקריפט shell
./run_js_cleaner_monitor.sh

# הפעלת הניטור ברקע (daemon)
python3 start_js_cleaner_monitor.py start

# בדיקת סטטוס הניטור
python3 start_js_cleaner_monitor.py status

# עצירת הניטור
python3 start_js_cleaner_monitor.py stop

# הפעלה מחדש של הניטור
python3 start_js_cleaner_monitor.py restart

# דוגמה לשילוב עם main.py
python3 start_js_cleaner_monitor.py start
python3 main.py
python3 start_js_cleaner_monitor.py stop
``` 