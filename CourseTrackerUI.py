import streamlit as st
import sqlite3
import pandas as pd
import json
import os

class CourseTrackerUI:
    def __init__(self, db_name="courses.db"):
        self.conn = sqlite3.connect(db_name)
        if "user_courses" not in st.session_state:
            # נסה לטעון מידע שמור מקובץ אם קיים
            if os.path.exists("saved_courses.json"):
                with open("saved_courses.json", "r", encoding="utf-8") as f:
                    st.session_state.user_courses = json.load(f)
            else:
                st.session_state.user_courses = []
        
        if "language" not in st.session_state:
            st.session_state.language = "Hebrew"
        if "filter_mode" not in st.session_state:
            st.session_state.filter_mode = "All"
        if "course_to_delete" not in st.session_state:
            st.session_state.course_to_delete = None
        if "edit_index" not in st.session_state:
            st.session_state.edit_index = None

    def load_courses(self):
        query = "SELECT course_name, course_number, credit_points FROM courses"
        return pd.read_sql(query, self.conn)

    def save_user_courses(self):
        """שמירת קורסי המשתמש לקובץ"""
        with open("saved_courses.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.user_courses, f, ensure_ascii=False, indent=2)
        st.success("✅ הנתונים נשמרו בהצלחה!")

    def course_input_form(self):
        st.title("🎓 BGU GPA & Requirement Tracker")

        # שפת ממשק
        st.sidebar.title("Language / שפה")
        st.session_state.language = st.sidebar.radio("Choose Language", ["Hebrew", "English"])

        # פילטרים בסרגל הצד
        st.sidebar.title("🔍 פילטרים / Filters")
        st.session_state.filter_mode = st.sidebar.radio(
            "הצג קורסים:",
            ["הכל / All", "ציון רגיל / Graded", "עובר/נכשל / Pass-Fail", "באנגלית / English"]
        )

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

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add Course", key="add_course"):
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
                    self.save_user_courses()
                    st.success("✅ קורס נוסף בהצלחה!")
                    st.rerun()

        # אם יש קורס למחיקה, נציג דיאלוג אישור
        if st.session_state.course_to_delete is not None:
            index = st.session_state.course_to_delete
            course_name = st.session_state.user_courses[index]['course_name']
            
            st.warning(f"האם אתה בטוח שברצונך למחוק את הקורס '{course_name}'?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("כן, מחק"):
                    st.session_state.user_courses.pop(index)
                    self.save_user_courses()
                    st.session_state.course_to_delete = None
                    st.success(f"✅ קורס {course_name} נמחק בהצלחה!")
                    st.rerun()
            with col2:
                if st.button("לא, בטל"):
                    st.session_state.course_to_delete = None
                    st.rerun()

        # הצגת הקורסים של המשתמש
        if st.session_state.user_courses:
            st.subheader("📘 Your Courses")
            
            # פילטור קורסים לפי הבחירה
            filtered_courses = st.session_state.user_courses
            if st.session_state.filter_mode == "ציון רגיל / Graded":
                filtered_courses = [c for c in filtered_courses if not c['binary']]
            elif st.session_state.filter_mode == "עובר/נכשל / Pass-Fail":
                filtered_courses = [c for c in filtered_courses if c['binary']]
            elif st.session_state.filter_mode == "באנגלית / English":
                filtered_courses = [c for c in filtered_courses if c['english']]
            
            # הכנת הנתונים לטבלה
            courses_for_table = []
            for i, course in enumerate(filtered_courses):
                # מציאת האינדקס האמיתי ברשימה המקורית
                real_index = st.session_state.user_courses.index(course)
                
                grade_display = "עובר ✓" if course['binary'] else f"{course['grade']}"
                english_display = "כן ✓" if course['english'] else "לא ✗"
                
                courses_for_table.append({
                    "index": real_index,  # שומרים את האינדקס האמיתי לשימוש בפעולות
                    "שם הקורס": course['course_name'],
                    "מספר קורס": course['course_number'],
                    "נק״ז": course['credit_points'],
                    "באנגלית": english_display,
                    "ציון": grade_display
                })
                
            # יצירת dataframe לתצוגה בטבלה
            if courses_for_table:
                df = pd.DataFrame(courses_for_table)
                
                # הטבלה המוצגת לא תכלול את עמודת האינדקס
                display_df = df.drop(columns=["index"])
                
                # הוספת פונקציונליות עריכה ומחיקה ישירות בטבלה
                edited_df = st.data_editor(
                    display_df,
                    column_config={
                        "פעולות": st.column_config.CheckboxColumn(
                            "פעולות",
                            help="סמן להסרת הקורס",
                            default=False
                        ),
                    },
                    hide_index=True,
                    disabled=["שם הקורס", "מספר קורס", "נק״ז", "באנגלית", "ציון"],
                    key="courses_table"
                )
                
                # בדיקה אם המשתמש סימן קורס למחיקה
                for i, checkbox_status in enumerate(st.session_state.courses_table.get("edited_rows",{}).values()):
                    if checkbox_status.get("פעולות", False):
                        # קבלת האינדקס האמיתי של הקורס
                        real_index = df.iloc[i]["index"]
                        st.session_state.course_to_delete = int(real_index)
                        st.rerun()

                # כפתורי פעולה כלליים
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📊 חשב סיכום"):
                        self.display_summary()
                with col2:
                    if st.button("✏️ ערוך קורסים"):
                        st.session_state.edit_mode = True
                        st.rerun()
                with col3:
                    if st.button("📥 הורד כקובץ CSV"):
                        df.to_csv("user_courses.csv", index=False, encoding="utf-8-sig")
                        st.success("📁 קובץ נוצר בהצלחה: user_courses.csv")
            else:
                st.info("אין קורסים שתואמים את הפילטר הנבחר")

            # מצב עריכת קורסים
            if "edit_mode" in st.session_state and st.session_state.edit_mode:
                st.subheader("✏️ עריכת קורסים")
                
                for i, course in enumerate(st.session_state.user_courses):
                    with st.expander(f"{course['course_name']} ({course['course_number']})"):
                        edited_name = st.text_input("שם הקורס:", value=course['course_name'], key=f"name_{i}")
                        edited_number = st.text_input("מספר הקורס:", value=course['course_number'], key=f"number_{i}")
                        edited_credits = st.number_input("נק״ז:", min_value=0.0, value=course['credit_points'], key=f"credits_{i}")
                        edited_english = st.checkbox("קורס באנגלית", value=course['english'], key=f"english_{i}")
                        edited_binary = st.checkbox("ציון עובר/נכשל", value=course['binary'], key=f"binary_{i}")
                        
                        edited_grade = None
                        if not edited_binary:
                            default_grade = course['grade'] if course['grade'] is not None else 85
                            edited_grade = st.number_input("ציון:", min_value=0, max_value=100, value=default_grade, key=f"grade_{i}")
                        
                        if st.button("שמור שינויים", key=f"save_{i}"):
                            st.session_state.user_courses[i] = {
                                "course_name": edited_name,
                                "course_number": edited_number,
                                "credit_points": edited_credits,
                                "english": edited_english,
                                "binary": edited_binary,
                                "grade": edited_grade
                            }
                            self.save_user_courses()
                            st.success("✅ השינויים נשמרו בהצלחה!")
                            st.rerun()
                
                if st.button("סיום עריכה"):
                    st.session_state.edit_mode = False
                    st.rerun()

    def display_summary(self):
        df = pd.DataFrame(st.session_state.user_courses)
        
        if df.empty:
            st.warning("⚠️ אין קורסים להצגה. אנא הוסף קורסים תחילה.")
            return

        total_credits = df['credit_points'].sum()
        
        # טיפול בקורסים באנגלית
        english_courses = df[df['english']] if 'english' in df.columns else pd.DataFrame()
        english_credits = english_courses['credit_points'].sum() if not english_courses.empty else 0
        english_list = english_courses['course_name'].tolist() if not english_courses.empty else []

        # טיפול בקורסים עם ציון (לא בינאריים)
        binary_courses = df[df['binary']] if 'binary' in df.columns else pd.DataFrame()
        binary_credits = binary_courses['credit_points'].sum() if not binary_courses.empty else 0
        
        graded_courses = df[~df['binary']] if 'binary' in df.columns else df
        
        # חישוב ממוצע משוקלל
        gpa = 0
        if not graded_courses.empty and 'grade' in graded_courses.columns:
            graded_credits = graded_courses['credit_points'].sum()
            if graded_credits > 0:  # מניעת חלוקה באפס
                weighted_sum = (graded_courses['grade'] * graded_courses['credit_points']).sum()
                gpa = weighted_sum / graded_credits

        # הצגת הסיכום
        st.subheader("📊 סיכום")
        st.markdown(f"### ✅ סך הכל נק״ז: `{total_credits:.1f}`")
        st.markdown(f"### 🌍 נק״ז בקורסים באנגלית: `{english_credits:.1f}`")
        st.markdown(f"### 📝 נק״ז בקורסים עם ציון עובר/נכשל: `{binary_credits:.1f}`")
        st.markdown(f"### 📈 ממוצע משוקלל (ללא קורסי עובר/נכשל): `{gpa:.2f}`")
        
        if english_list:
            st.markdown("**רשימת הקורסים באנגלית:**")
            for name in english_list:
                st.markdown(f"- {name}")
                
        # סימולציית שינוי בממוצע
        st.subheader("🔮 סימולציית שינוי ממוצע")
        st.markdown("בדוק כיצד ישתנה הממוצע אם תהפוך קורסים נוספים לעובר/נכשל:")
        
        # הצג רק קורסים עם ציון (לא בינאריים)
        simulation_courses = []
        if not graded_courses.empty:
            for _, course in graded_courses.iterrows():
                if st.checkbox(f"הפוך ל-עובר/נכשל: {course['course_name']} (ציון: {course['grade']})", key=f"sim_{course['course_number']}"):
                    simulation_courses.append(course)
        
        if simulation_courses:
            # חשב ממוצע חדש ללא הקורסים שנבחרו
            remaining_graded = graded_courses[~graded_courses['course_number'].isin([c['course_number'] for c in simulation_courses])]
            
            new_gpa = 0
            if not remaining_graded.empty:
                remaining_credits = remaining_graded['credit_points'].sum()
                if remaining_credits > 0:
                    weighted_sum = (remaining_graded['grade'] * remaining_graded['credit_points']).sum()
                    new_gpa = weighted_sum / remaining_credits
            
            st.markdown(f"### 🚀 הממוצע החדש יהיה: `{new_gpa:.2f}`")
            
            removed_credits = sum(course['credit_points'] for course in simulation_courses)
            st.markdown(f"### 📉 שינוי בממוצע: `{new_gpa - gpa:.2f}`")
            st.markdown(f"### 📊 נק״ז שיהפכו לעובר/נכשל: `{removed_credits:.1f}`")