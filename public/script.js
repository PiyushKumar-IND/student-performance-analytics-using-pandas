// ======================================
// STUDENT PERFORMANCE ANALYTICS
// ======================================

// Local development uses FastAPI on port 8000.
// On Vercel, frontend and API use the same domain.

const API_BASE =
    (location.protocol === "file:" ||
    (["localhost", "127.0.0.1"].includes(location.hostname)
    && location.port !== "8000"))
    ? "http://127.0.0.1:8000"
    : "";

let performanceChart = null;
let subjectChart = null;
let attendanceChart = null;

let allStudents = [];


// ======================================
// FETCH API DATA
// ======================================

async function fetchData(endpoint) {

    const response = await fetch(`${API_BASE}/api/${endpoint}`);

    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }

    return await response.json();
}


// ======================================
// LOAD DASHBOARD
// ======================================

async function loadDashboard() {

    try {

        const [dashboard, students] = await Promise.all([
            fetchData("dashboard"),
            fetchData("students")
        ]);

        allStudents = students;

        updateStatistics(dashboard);

        createPerformanceChart(dashboard);

        createSubjectChart(dashboard);

        createAttendanceChart(dashboard);

        updateStudentTable(allStudents);

    }

    catch (error) {

        console.error("Dashboard Error:", error);

        document.getElementById("totalStudents").textContent = "Error";

        alert(
            "Unable to load dashboard data. " +
            "Check whether your FastAPI server is running."
        );

    }

}


// ======================================
// UPDATE STATISTICS
// ======================================

function updateStatistics(data) {

    document.getElementById("totalStudents").textContent =
        data.total_students;

    document.getElementById("averageMarks").textContent =
        data.average_marks + "%";

    document.getElementById("averageAttendance").textContent =
        data.average_attendance + "%";

    document.getElementById("excellentStudents").textContent =
        data.excellent_students;

    document.getElementById("excellentCount").textContent =
        data.excellent_students;

    document.getElementById("averageCount").textContent =
        data.average_students;

    document.getElementById("weakCount").textContent =
        data.weak_students;

    document.getElementById("lowAttendance").textContent =
        data.attendance_below_75;

}


// ======================================
// PERFORMANCE CHART
// ======================================

function createPerformanceChart(data) {

    const ctx = document
        .getElementById("performanceChart")
        .getContext("2d");

    if (performanceChart) {
        performanceChart.destroy();
    }

    performanceChart = new Chart(ctx, {

        type: "doughnut",

        data: {

            labels: [
                "Excellent",
                "Average",
                "Needs Improvement"
            ],

            datasets: [{

                data: [
                    data.excellent_students,
                    data.average_students,
                    data.weak_students
                ],

                backgroundColor: [
                    "#16a34a",
                    "#f59e0b",
                    "#ef4444"
                ],

                borderWidth: 2

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });

}


// ======================================
// SUBJECT PERFORMANCE CHART
// ======================================

function createSubjectChart(data) {

    const ctx = document
        .getElementById("subjectChart")
        .getContext("2d");

    if (subjectChart) {
        subjectChart.destroy();
    }

    subjectChart = new Chart(ctx, {

        type: "bar",

        data: {

            labels: ["Math", "Science", "English"],

            datasets: [{

                label: "Average Marks",

                data: [
                    data.subject_average.Math,
                    data.subject_average.Science,
                    data.subject_average.English
                ],

                backgroundColor: [
                    "#2563eb",
                    "#9333ea",
                    "#0891b2"
                ],

                borderRadius: 7

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            scales: {

                y: {

                    beginAtZero: true,

                    max: 100

                }

            }

        }

    });

}


// ======================================
// ATTENDANCE CHART
// ======================================

function createAttendanceChart(data) {

    const ctx = document
        .getElementById("attendanceChart")
        .getContext("2d");

    if (attendanceChart) {
        attendanceChart.destroy();
    }

    const lowAttendance = data.attendance_below_75;

    const goodAttendance =
        data.total_students - lowAttendance;

    attendanceChart = new Chart(ctx, {

        type: "pie",

        data: {

            labels: [
                "Good Attendance",
                "Low Attendance"
            ],

            datasets: [{

                data: [
                    goodAttendance,
                    lowAttendance
                ],

                backgroundColor: [
                    "#16a34a",
                    "#ef4444"
                ]

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false

        }

    });

}


// ======================================
// STUDENT TABLE
// ======================================

function updateStudentTable(students) {

    const table = document.getElementById("studentTable");

    table.innerHTML = "";

    students.forEach(student => {

        const row = document.createElement("tr");

        const values = [
            student.Student_ID,
            student.Name,
            student.City,
            student.Math,
            student.Science,
            student.English,
            student.Attendance + "%",
            Number(student.Average).toFixed(2)
        ];

        values.forEach(value => {

            const cell = document.createElement("td");

            cell.textContent = value ?? "";

            row.appendChild(cell);

        });

        table.appendChild(row);

    });

}


// ======================================
// SEARCH STUDENTS
// ======================================

document
    .getElementById("searchInput")
    .addEventListener("input", function () {

        const searchValue = this.value.toLowerCase();

        const filteredStudents = allStudents.filter(student => {

            return String(student.Name)
                .toLowerCase()
                .includes(searchValue);

        });

        updateStudentTable(filteredStudents);

    });


// ======================================
// START DASHBOARD
// ======================================

loadDashboard();