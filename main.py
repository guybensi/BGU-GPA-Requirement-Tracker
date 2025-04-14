from CourseTrackerUI import CourseTrackerUI
from CourseDatabase import CourseDatabase

# שלב ראשון - יצירת בסיס הנתונים והוספת דוגמה אחת (אפשר למחוק)
db = CourseDatabase()
db.add_course("מבוא למדעי המחשב", "204000", 3.5)
db.add_course("חדו\"א 1", "201001", 5)
db.close()

# שלב שני - הרצת ממשק המשתמש
tracker = CourseTrackerUI()
tracker.course_input_form()
