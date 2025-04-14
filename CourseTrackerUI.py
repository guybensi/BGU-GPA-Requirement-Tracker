import streamlit as st
import sqlite3
import pandas as pd

class CourseTrackerUI:
    def __init__(self, db_name="courses.db"):
        self.conn = sqlite3.connect(db_name)
        if "user_courses" not in st.session_state:
            st.session_state.user_courses = []
        if "selected_index" not in st.session_state:
            st.session_state.selected_index = None
        if "edit_mode" not in st.session_state:
            st.session_state.edit_mode = False

    def load_courses(self):
        query = "SELECT course_name, course_number, credit_points FROM courses"
        df = pd.read_sql(query, self.conn)
        return df

    def course_input_form(self):
        st.title("🎓 BGU GPA & Requirement Tracker")

        course_df = self.load_courses()
        course_names = course_df['course_name'].tolist()

        st.subheader("➕ Add a Course")
        selected_course = st.selectbox("Choose a course:", course_names)

        if selected_course not in course_names:
            st.error("❌ Course not found in the database.")
            return

        course_info = course_df[course_df['course_name'] == selected_course].iloc[0]

        course_number = course_info['course_number']
        default_credits = course_info['credit_points']
        updated_credits = st.number_input("Credit points (you can modify if needed):", value=float(default_credits))

        taught_in_english = st.checkbox("Course taught in English")
        binary_pass = st.checkbox("Mark as Pass/Fail (Binary Pass)")
        received_grade = None

        if not binary_pass:
            received_grade = st.number_input("Grade (0-100):", min_value=0, max_value=100, value=85)

        if st.button("Add Course"):
            if not binary_pass and (received_grade < 0 or received_grade > 100):
                st.error("❌ Invalid grade. Must be between 0 and 100.")
            else:
                st.session_state.user_courses.append({
                    "course_name": selected_course,
                    "course_number": course_number,
                    "credit_points": updated_credits,
                    "english": taught_in_english,
                    "binary": binary_pass,
                    "grade": received_grade
                })

        if st.session_state.user_courses:
            st.subheader("📘 Your Courses")
            df = pd.DataFrame(st.session_state.user_courses)

            # תיבת סימון ליד כל קורס
            selected_course_index = st.radio(
                "Select a course:",
                options=range(len(df)),
                format_func=lambda i: f"{df.loc[i, 'course_name']} ({df.loc[i, 'course_number']})"
            )

            if st.button("Edit Selected Course"):
                st.session_state.selected_index = selected_course_index
                st.session_state.edit_mode = True

            if st.button("Delete Selected Course"):
                st.session_state.user_courses.pop(selected_course_index)
                st.experimental_rerun()

            if st.session_state.edit_mode and st.session_state.selected_index is not None:
                course = st.session_state.user_courses[st.session_state.selected_index]
                st.markdown("### ✏️ Edit Course")
                new_name = st.text_input("Course Name", value=course["course_name"])
                new_number = st.text_input("Course Number", value=course["course_number"])
                new_credits = st.number_input("Credit Points", value=float(course["credit_points"]))
                new_english = st.checkbox("Taught in English", value=course["english"])
                new_binary = st.checkbox("Binary Pass", value=course["binary"])
                new_grade = None
                if not new_binary:
                    new_grade = st.number_input("Grade (0-100)", min_value=0, max_value=100, value=course["grade"])

                if st.button("💾 Save Changes"):
                    st.session_state.user_courses[st.session_state.selected_index] = {
                        "course_name": new_name,
                        "course_number": new_number,
                        "credit_points": new_credits,
                        "english": new_english,
                        "binary": new_binary,
                        "grade": new_grade
                    }
                    st.session_state.edit_mode = False
                    st.session_state.selected_index = None
                    st.experimental_rerun()

            st.dataframe(df)

            if st.button("📊 Calculate Summary"):
                self.display_summary()

    def display_summary(self):
        df = pd.DataFrame(st.session_state.user_courses)

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
