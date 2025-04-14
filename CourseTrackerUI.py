import streamlit as st
import sqlite3
import pandas as pd

class CourseTrackerUI:
    def __init__(self, db_name="courses.db"):
        self.conn = sqlite3.connect(db_name)
        self.user_courses = []

    def load_courses(self):
        query = "SELECT course_name, course_number, credit_points FROM courses"
        df = pd.read_sql(query, self.conn)
        return df

    def course_input_form(self):
        st.title("🎓 BGU GPA & Requirement Tracker")

        course_df = self.load_courses()
        course_names = course_df['course_name'].tolist()

        st.subheader("Add a Course")
        selected_course = st.selectbox("Choose a course:", course_names)
        course_info = course_df[course_df['course_name'] == selected_course].iloc[0]

        course_number = course_info['course_number']
        default_credits = course_info['credit_points']
        updated_credits = st.number_input("Credit points (you can modify if needed):", value=float(default_credits))

        taught_in_english = st.checkbox("Course taught in English")
        binary_pass = st.checkbox("Mark as Pass/Fail (Binary Pass)")
        received_grade = None

        if not binary_pass:
            received_grade = st.slider("Grade (0-100):", 0, 100, 85)

        if st.button("Add Course"):
            self.user_courses.append({
                "course_name": selected_course,
                "course_number": course_number,
                "credit_points": updated_credits,
                "english": taught_in_english,
                "binary": binary_pass,
                "grade": received_grade
            })

        if self.user_courses:
            st.subheader("📘 Your Courses")
            st.dataframe(pd.DataFrame(self.user_courses))

            if st.button("📊 Calculate Summary"):
                self.display_summary()

    def display_summary(self):
        df = pd.DataFrame(self.user_courses)

        total_credits = df['credit_points'].sum()
        english_courses = df[df['english'] == True]
        english_count = len(english_courses)
        english_list = english_courses['course_name'].tolist()

        graded_courses = df[df['binary'] == False]
        weighted_sum = (graded_courses['grade'] * graded_courses['credit_points']).sum()
        graded_credits = graded_courses['credit_points'].sum()
        gpa = weighted_sum / graded_credits if graded_credits else 0

        st.markdown(f"### ✅ Total Credits: {total_credits}")
        st.markdown(f"### 🇬🇧 English-Taught Courses: {english_count}")
        if english_list:
            st.markdown("**English Course List:**")
            for name in english_list:
                st.markdown(f"- {name}")

        st.markdown(f"### 📈 GPA (excluding pass/fail): {gpa:.2f}")
