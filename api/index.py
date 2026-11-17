from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
from pathlib import Path

app = FastAPI(title="Student Performance Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "dataset.csv"


def load_data():
    df = pd.read_csv(DATA_FILE)

    required_columns = [
        "Student_ID", "Name", "Age", "Gender", "City",
        "Math", "Science", "English", "Attendance"
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for col in ["Math", "Science", "English", "Attendance"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Math", "Science", "English", "Attendance"])

    df["Average"] = df[["Math", "Science", "English"]].mean(axis=1)

    return df


@app.get("/api/health")
def health():
    return {"status": "working"}


@app.get("/api/dashboard")
def dashboard():

    df = load_data()

    excellent = int((df["Average"] >= 80).sum())
    average = int(((df["Average"] >= 50) & (df["Average"] < 80)).sum())
    weak = int((df["Average"] < 50).sum())

    return {
        "total_students": int(len(df)),
        "average_marks": round(float(df["Average"].mean()), 2),
        "average_attendance": round(float(df["Attendance"].mean()), 2),
        "excellent_students": excellent,
        "average_students": average,
        "weak_students": weak,
        "attendance_below_75": int((df["Attendance"] < 75).sum()),
        "subject_average": {
            "Math": round(float(df["Math"].mean()), 2),
            "Science": round(float(df["Science"].mean()), 2),
            "English": round(float(df["English"].mean()), 2)
        }
    }


@app.get("/api/students")
def students():

    df = load_data()

    return df.to_dict(orient="records")