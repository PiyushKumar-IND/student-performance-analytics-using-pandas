import io
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="📊",
    layout="wide",
)

REQUIRED_COLUMNS = [
    "Student_ID", "Name", "Age", "Gender", "City",
    "Math", "Science", "English", "Attendance"
]
NUMERIC_COLUMNS = ["Age", "Math", "Science", "English", "Attendance"]
SUBJECT_COLUMNS = ["Math", "Science", "English"]


@st.cache_data
def load_default_data():
    return pd.read_csv(Path(__file__).with_name("dataset.csv"))


def prepare_data(raw):
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing_columns:
        raise ValueError("Missing required columns: " + ", ".join(missing_columns))

    data = raw.copy()
    data["Name"] = data["Name"].astype("string").str.strip()
    data["City"] = data["City"].astype("string").str.strip()
    data["Gender"] = data["Gender"].astype("string").str.strip()

    for col in NUMERIC_COLUMNS + ["Student_ID"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    # Apply the validation rules used in the original Pandas project.
    data.loc[~data["Age"].between(15, 30), "Age"] = pd.NA
    for col in SUBJECT_COLUMNS + ["Attendance"]:
        data.loc[~data[col].between(0, 100), col] = pd.NA

    for col in SUBJECT_COLUMNS:
        data[col] = data[col].fillna(data[col].mean())

    data = data.dropna(subset=["Student_ID", "Name", "Age"])
    data = data.drop_duplicates(subset=["Student_ID"])
    data = data.reset_index(drop=True)

    data["Total"] = data[SUBJECT_COLUMNS].sum(axis=1)
    data["Percentage"] = data["Total"] / len(SUBJECT_COLUMNS)

    def grade(value):
        if value >= 90:
            return "A+"
        if value >= 80:
            return "A"
        if value >= 70:
            return "B"
        if value >= 60:
            return "C"
        if value >= 50:
            return "D"
        return "Needs improvement"

    data["Grade"] = data["Percentage"].apply(grade)
    return data


st.title("📊 Student Performance Analytics")
st.caption("Explore student records, clean data, compare results and download reports.")

with st.sidebar:
    st.header("Data")
    uploaded_file = st.file_uploader("Upload another student CSV", type=["csv"])
    st.caption("Expected columns: Student_ID, Name, Age, Gender, City, Math, Science, English, Attendance.")

try:
    raw_df = pd.read_csv(uploaded_file) if uploaded_file else load_default_data()
    df = prepare_data(raw_df)
except Exception as exc:
    st.error(f"Could not load or process the data: {exc}")
    st.stop()

if df.empty:
    st.warning("No valid student records remain after cleaning.")
    st.stop()

with st.sidebar:
    st.divider()
    st.header("Filters")
    cities = sorted(df["City"].dropna().astype(str).unique().tolist())
    selected_cities = st.multiselect("City", cities, default=cities)
    grades = sorted(df["Grade"].unique().tolist())
    selected_grades = st.multiselect("Grade", grades, default=grades)
    search_name = st.text_input("Search student name")

filtered = df[
    df["City"].astype(str).isin(selected_cities)
    & df["Grade"].isin(selected_grades)
]
if search_name:
    filtered = filtered[filtered["Name"].str.contains(search_name, case=False, na=False)]

if filtered.empty:
    st.info("No students match the selected filters.")
    st.stop()

# Overview
st.subheader("Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Students", f"{len(filtered):,}")
c2.metric("Average percentage", f"{filtered['Percentage'].mean():.2f}%")
c3.metric("Highest percentage", f"{filtered['Percentage'].max():.2f}%")
c4.metric("Average attendance", f"{filtered['Attendance'].mean():.2f}%")

overview_tab, records_tab, analysis_tab, cleaning_tab, downloads_tab = st.tabs(
    ["Overview", "Student Records", "Analysis & Charts", "Data Cleaning", "Downloads"]
)

with overview_tab:
    left, right = st.columns(2)
    with left:
        st.markdown("#### Average marks by subject")
        subject_avg = filtered[SUBJECT_COLUMNS].mean().rename("Average marks")
        st.bar_chart(subject_avg)
    with right:
        st.markdown("#### Grade distribution")
        grade_counts = filtered["Grade"].value_counts().reindex(
            ["A+", "A", "B", "C", "D", "Needs improvement"], fill_value=0
        )
        st.bar_chart(grade_counts)

    st.markdown("#### Top 5 students")
    top_five = filtered.nlargest(5, "Percentage")[
        ["Student_ID", "Name", "City", "Total", "Percentage", "Grade"]
    ]
    st.dataframe(top_five, use_container_width=True, hide_index=True)

with records_tab:
    st.markdown("#### Student records")
    display_cols = [
        "Student_ID", "Name", "Age", "Gender", "City",
        "Math", "Science", "English", "Attendance", "Total", "Percentage", "Grade"
    ]
    st.dataframe(
        filtered[display_cols].style.format({"Percentage": "{:.2f}%"}),
        use_container_width=True,
        hide_index=True,
    )

with analysis_tab:
    st.markdown("#### Subject-wise marks")
    st.bar_chart(filtered.set_index("Name")[SUBJECT_COLUMNS])

    st.markdown("#### Attendance vs percentage")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(filtered["Attendance"], filtered["Percentage"])
    ax.set_xlabel("Attendance (%)")
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Attendance vs Student Percentage")
    ax.grid(alpha=0.25)
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("#### Average percentage by city")
    city_avg = filtered.groupby("City")["Percentage"].mean().sort_values(ascending=False)
    st.bar_chart(city_avg)

    st.markdown("#### Correlation matrix")
    corr = filtered[["Math", "Science", "English", "Attendance", "Percentage"]].corr()
    st.dataframe(corr.round(2), use_container_width=True)

with cleaning_tab:
    st.markdown("#### Data quality summary")
    q1, q2, q3 = st.columns(3)
    q1.metric("Rows in uploaded/source data", len(raw_df))
    q2.metric("Missing cells in source", int(raw_df.isna().sum().sum()))
    q3.metric("Duplicate student IDs in source", int(raw_df["Student_ID"].duplicated().sum()))

    st.markdown("#### Missing values by column (before cleaning)")
    missing = raw_df.isna().sum().rename("Missing values")
    st.dataframe(missing.to_frame(), use_container_width=True)

    st.markdown("#### Cleaned data preview")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(
        "Cleaning follows the original project rules: trim text, convert numeric columns, "
        "validate age and 0–100 scores, fill missing subject marks with the subject mean, "
        "remove rows missing essential fields, and keep one row per Student_ID."
    )

with downloads_tab:
    st.markdown("#### Download cleaned data")
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    json_bytes = df.to_json(orient="records", indent=4).encode("utf-8")
    st.download_button(
        "Download cleaned CSV",
        data=csv_bytes,
        file_name="cleaned_students.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download student results JSON",
        data=json_bytes,
        file_name="students_result.json",
        mime="application/json",
    )

st.divider()
st.caption("Student Performance Analytics • Built with Python, Pandas, Matplotlib and Streamlit")
