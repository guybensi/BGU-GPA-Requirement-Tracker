import streamlit as st
import sqlite3
import pandas as pd

class CourseTrackerUI:
    def __init__(self, db_name="courses.db"):
        self.conn = sqlite3.connect(db_name)
        if "user_courses" not in st.session_state:
            st.session_state.user_courses = []
        if "edit_index" not in st.session_state:
            st.session_state.edit_index = None
        if "language" not in st.session_state:
            st.session_state.language = "Hebrew"

    def load_courses(self):
        query = "SELECT course_name, course_number, credit_points FROM courses"
        return pd.read_sql(query, self.conn)

    def course_input_form(self):
        st.title("🎓 BGU GPA & Requirement Tracker")

        # שפת ממשק
        st.sidebar.title("Language / שפה")
        st.session_state.language = st.sidebar.radio("Choose Language", ["Hebrew", "English"])

        course_df = self.load_courses()
        course_names = course_df['course_name'].tolist() + ["🆕 קורס אחר / Other"]

        st.subheader("➕ Add a Course")
        selected_course = st.selectbox("Choose a course:", sorted(set(course_names)))

        if selected_course == "🆕 קורס אחר / Other":
            course_name = st.text_input("📘 Course Name:")
            course_number = st.text_input("🆔 Course Number:")
            updated_credits = st.number_input("🎯 Credit Points:", min_value=0.0, value=3.0)
        else:
            course_info = course_df[course_df['course_name'] == selected_course].iloc[0]
            course_name = course_info['course_name']
            course_number = course_info['course_number']
            default_credits = float(course_info['credit_points'])

            st.markdown(f"📚 נק״ז לפי התוכנית: `{default_credits}`")
            updated_credits = st.number_input("🎯 נק״ז בפועל (ניתן לעריכה):", min_value=0.0, value=default_credits)


        taught_in_english = st.checkbox("🌍 Course taught in English")
        binary_pass = st.checkbox("✔️ Pass/Fail (Binary Grade)")
        received_grade = None

        if not binary_pass:
            received_grade = st.number_input("🎓 Grade (0-100):", min_value=0, max_value=100, value=85)

        if st.button("Add Course"):
            if any(c['course_number'] == course_number for c in st.session_state.user_courses):
                st.warning("⚠️ הקורס כבר קיים ברשימתך")
            else:
                st.session_state.user_courses.append({
                    "course_name": course_name,
                    "course_number": course_number,
                    "credit_points": updated_credits,
                    "english": taught_in_english,
                    "binary": binary_pass,
                    "grade": received_grade
                })
                st.success("✅ קורס נוסף בהצלחה!")
                st.rerun()

        # הצגת הקורסים של המשתמש
        if st.session_state.user_courses:
            st.subheader("📘 Your Courses")
            df = pd.DataFrame(st.session_state.user_courses)

            selected_row = st.radio("Select a course to edit/delete:", options=df.index,
                                    format_func=lambda i: f"{df.loc[i, 'course_name']} ({df.loc[i, 'course_number']})")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Delete Selected"):
                    st.session_state.user_courses.pop(selected_row)
                    st.rerun()
            with col2:
                if st.button("✏️ Edit Selected"):
                    st.session_state.edit_index = selected_row

            editable_mask = [False] * len(df)
            if st.session_state.edit_index is not None:
                editable_mask[st.session_state.edit_index] = True

            edited_df = st.data_editor(
                df.copy(),
                disabled=~pd.Series(editable_mask),
                key="editable_table"
            )

            if st.button("💾 Save Changes"):
                st.session_state.user_courses = edited_df.to_dict(orient="records")
                st.session_state.edit_index = None
                st.success("🎉 Changes saved!")
                st.rerun()

            if st.button("📊 Calculate Summary"):
                self.display_summary()

            if st.button("📥 Download Course List as CSV"):
                df.to_csv("user_courses.csv", index=False)
                st.success("📁 קובץ נוצר בהצלחה: user_courses.csv")

    def display_summary(self):
        df = pd.DataFrame(st.session_state.user_courses)

        total_credits = df['credit_points'].sum()
        english_courses = df[df['english']]
        english_list = english_courses['course_name'].tolist()

        graded_courses = df[~df['binary']]
        weighted_sum = (graded_courses['grade'] * graded_courses['credit_points']).sum()
        graded_credits = graded_courses['credit_points'].sum()
        gpa = weighted_sum / graded_credits if graded_credits else 0

        st.markdown(f"### ✅ Total Credits: `{total_credits}`")
        st.markdown(f"### 🌍 English-Taught Courses: `{len(english_courses)}`")
        if english_list:
            st.markdown("**Course list in English:**")
            for name in english_list:
                st.markdown(f"- {name}")
        st.markdown(f"### 📈 GPA (excluding pass/fail): `{gpa:.2f}`")
