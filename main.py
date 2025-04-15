from CourseDatabase import populate_courses
from CourseTrackerUI import CourseTrackerUI

if __name__ == "__main__":
    populate_courses() 
    tracker = CourseTrackerUI()
    tracker.course_input_form()
