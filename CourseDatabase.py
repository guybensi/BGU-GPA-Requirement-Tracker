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

    def get_all_courses(self):
        query = "SELECT course_name, course_number, credit_points FROM courses;"
        cursor = self.conn.execute(query)
        return cursor.fetchall()

    def close(self):
        self.conn.close()
