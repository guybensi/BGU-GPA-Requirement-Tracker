from CourseDatabase import CourseDatabase

# Initialize DB with courses (only creates table and inserts if needed)
CourseDatabase()  # Just running this will create/populate the table if not already

from CourseTrackerUI import CourseTrackerUI

if __name__ == "__main__":
    tracker = CourseTrackerUI()
    tracker.course_input_form()
