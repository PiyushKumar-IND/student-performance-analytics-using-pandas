import os
import pandas as pd
import matplotlib.pyplot as plt

# Keep dataset.csv in the same folder as this file.
df = pd.read_csv("dataset.csv")

print("\n=== STUDENT PERFORMANCE ANALYSIS ===")

# 1. Explore the data
print("\nFirst five rows:")
print(df.head())
print("\nShape (rows, columns):", df.shape)
print("\nColumn names:", list(df.columns))
print("\nData types:")
print(df.dtypes)
print("\nSummary:")
print(df.describe())

# 2. Clean data (these steps are safe even if the original file is already clean)
df["Name"] = df["Name"].astype("string").str.strip()
df["City"] = df["City"].astype("string").str.strip()

numeric_cols = ["Age", "Math", "Science", "English", "Attendance"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Example validation rules for this practice dataset
df.loc[~df["Age"].between(15, 30), "Age"] = pd.NA
for col in ["Math", "Science", "English", "Attendance"]:
    df.loc[~df[col].between(0, 100), col] = pd.NA

# Fill missing subject marks with that subject's average
for col in ["Math", "Science", "English"]:
    df[col] = df[col].fillna(df[col].mean())

# Drop rows still missing essential information
df = df.dropna(subset=["Student_ID", "Name", "Age"])
df = df.drop_duplicates(subset=["Student_ID"])
df = df.reset_index(drop=True)

# 3. Create calculated columns
df["Total"] = df[["Math", "Science", "English"]].sum(axis=1)
df["Percentage"] = df["Total"] / 3

def grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    return "Needs improvement"

df["Grade"] = df["Percentage"].apply(grade)

# 4. Analyze
print("\nStudent results:")
print(df[["Name", "Total", "Percentage", "Grade"]].to_string(index=False))

print("\nAverage marks by subject:")
print(df[["Math", "Science", "English"]].mean())

print("\nStudents by city:")
print(df["City"].value_counts())

print("\nAverage percentage by city:")
print(df.groupby("City")["Percentage"].mean().round(2))

print("\nTop five students:")
print(df.nlargest(5, "Percentage")[["Name", "Percentage", "Grade"]])

print("\nCorrelation matrix:")
print(df[["Math", "Science", "English", "Attendance", "Percentage"]].corr().round(2))

# 5. Save cleaned files
df.to_csv("cleaned_students.csv", index=False)
df.to_json("students_result.json", orient="records", indent=4)

# 6. Plot charts
os.makedirs("charts", exist_ok=True)

df.plot(x="Name", y="Percentage", kind="bar", legend=False, figsize=(10, 5))
plt.title("Student Percentage")
plt.xlabel("Student")
plt.ylabel("Percentage")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("charts/student_percentage.png")
plt.show()

df.plot(x="Attendance", y="Percentage", kind="scatter", figsize=(7, 5))
plt.title("Attendance vs Percentage")
plt.xlabel("Attendance (%)")
plt.ylabel("Percentage")
plt.tight_layout()
plt.savefig("charts/attendance_vs_percentage.png")
plt.show()

print("\nProject complete. Check the generated CSV, JSON and charts.")
