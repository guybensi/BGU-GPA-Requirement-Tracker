import sqlite3

class CourseDatabase:
    def __init__(self, db_name="courses.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            course_number TEXT NOT NULL UNIQUE,
            credit_points REAL NOT NULL
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_course(self, course_name, course_number, credit_points):
        query = """
        INSERT INTO courses (course_name, course_number, credit_points)
        VALUES (?, ?, ?);
        """
        try:
            self.conn.execute(query, (course_name, course_number, credit_points))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"Course number {course_number} already exists.")

    def close(self):
        self.conn.close()

# אתחול בסיס הנתונים וטעינת הקורסים
if __name__ == "__main__":
    db = CourseDatabase()

    courses = {
        "202-10011": ("בקיאות במתמטיקה", 0.0),
        "202-11011": ("מבוא למדעי המחשב", 5.0),
        "202-11021": ("יישומים מתמטיים במדעי המחשב", 1.0),
        "202-11031": ("מבני נתונים", 5.0),
        "202-11061": ("מבנים בדידים וקומבינטוריקה", 5.0),
        "202-12011": ("מודלים חישוביים", 5.0),
        "202-12031": ("תכנות מערכות", 5.0),
        "202-10021": ("מבוא לאלגוריתמים: יסודות ההסתברות", 0.0),
        "202-12041": ("תכנון אלגוריתמים", 5.0),
        "202-12051": ("עקרונות שפות תכנות", 5.0),
        "202-12081": ("מעבדה מורחבת בתכנות מערכות", 2.0),
        "361-13131": ("מערכות ספרתיות", 3.5),
        "361-13301": ("מבוא למחשבים למדעי המחשב", 3.5),
        "201-12361": ("חדו\"א א'1 למדעי המחשב והנדסת תוכנה", 5.0),
        "201-12371": ("חדו\"א א'2 למדעי המחשב והנדסת תוכנה", 5.0),
        "201-10201": ("מבוא ללוגיקה ותורת הקבוצות למדעי המחשב והנדסת תכנה", 5.0),
        "201-17011": ("אלגברה 1 למדעי המחשב", 5.0),
        "201-17021": ("אלגברה 2 למדעי המחשב", 5.0),
        "201-13011": ("מבוא להסתברות למדעי המחשב", 4.5),
        "201-13021": ("הסתברות וסטטיסטיקה למדעי המחשב", 5.0),
        "202-13011": ("מבוא לאנליזה נומרית", 5.0),
        "202-13021": ("עקרונות הקומפילציה", 5.0),
        "202-13031": ("מערכות הפעלה", 5.0),
        "202-13081": ("עקרונות מדעי המחשב", 5.0),
        "202-13091": ("תכנות קצה (P)", 5.0),
        "202-13101": ("מבוא ללמידה חישובית", 5.0),
        "299-11121": ("הדרכה בספריה", 0.0),
        "153-15051": ("אנגלית מתקדמים ב", 2.0),
        "201-19321": ("אלגברה לינארית להנדסה", 4.5),
        "202-15031": ("למידה עמוקה יישומית", 4.0),
        "202-15032": ("תרגול בלמידה עמוקה יישומית למדעי הנתונים", 0.5),
        "202-13051": ("יסודות הנדסת תוכנה", 3.5),
        "202-13061": ("מבוא לאימות תוכנה בשיטות פורמליות", 5.0),
        "202-15141": ("סדנא ליישום פרוייקט תוכנה", 3.0),
        "202-15181": ("תיכון תוכנה מונחה עצמים", 3.0),
        "372-11105": ("מבוא להנדסת תוכנה", 4.0),
        "372-13401": ("ניתוח ועיצוב מערכות להנדסת תוכנה", 5.0),
        "372-13501": ("הנדסת איכות תוכנה", 3.5),
        "373-14401": ("פרויקט בהנדסת תוכנה 1", 4.0),
        "373-14402": ("פרויקט בהנדסת תוכנה 2", 4.0),
        "372-13041": ("מבוא לתקשורת נתונים", 3.5),
        "000": ("קורס אחר", 2),
    }

    for number, (name, credits) in courses.items():
        db.add_course(name, number, credits)

    db.close()