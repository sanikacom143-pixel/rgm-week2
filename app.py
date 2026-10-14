from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'rgm-week2-secret'

# ========== 8 OOP CLASSES ==========

class Student:
    def __init__(self, roll_no, name, class_name, branch=""):
        self.roll_no = roll_no
        self.name = name
        self.class_name = class_name
        self.branch = branch
        self.validate()
    def validate(self):
        if not self.roll_no or not self.name:
            raise ValueError("Roll and Name required")
        return True
    def to_dict(self):
        return {"roll_no": self.roll_no, "name": self.name, "class_name": self.class_name, "branch": self.branch}

class Class:
    def __init__(self, class_id, name, total_students=0):
        self.class_id = class_id
        self.name = name
        self.total_students = total_students
        self.students = []
    def add_student(self, student):
        self.students.append(student)
        self.total_students = len(self.students)
    def validate_roll_numbers(self):
        rolls = [s.roll_no for s in self.students]
        return len(rolls) == len(set(rolls))

class Seat:
    def __init__(self, seat_id, row, col):
        self.seat_id = seat_id
        self.row = row
        self.col = col
        self.status = "available"
        self.student = None
    def occupy(self, student):
        if self.status!= "available":
            raise ValueError("Seat not available")
        self.student = student
        self.status = "occupied"
    def vacate(self):
        self.student = None
        self.status = "available"

class Hall:
    def __init__(self, hall_id, name, rows, cols):
        self.hall_id = hall_id
        self.name = name
        self.rows = int(rows)
        self.cols = int(cols)
        self.seats = []
        self.create_layout()
    def create_layout(self):
        self.seats = []
        for r in range(1, self.rows+1):
            for c in range(1, self.cols+1):
                seat_id = f"{self.name}-R{r}S{c}"
                self.seats.append(Seat(seat_id, r, c))
    def get_available_seats(self):
        return [s for s in self.seats if s.status == "available"]
    def get_occupancy(self):
        total = len(self.seats)
        occupied = len([s for s in self.seats if s.status == "occupied"])
        return {"total": total, "occupied": occupied, "available": total-occupied}

class Exam:
    def __init__(self, exam_id, subject, date, session="FN"):
        self.exam_id = exam_id
        self.subject = subject
        self.date = date
        self.session = session
        self.status = "created"
    def to_dict(self):
        return {"exam_id": self.exam_id, "subject": self.subject, "date": self.date, "session": self.session, "status": self.status}

class ConstraintRule:
    def __init__(self, rule_type="branch_alternate"):
        self.rule_type = rule_type
    def is_valid(self, seat, student, neighbors):
        if self.rule_type == "branch_alternate":
            for n in neighbors:
                if n and n.branch == student.branch:
                    return False
        return True

class SeatingArrangement:
    def __init__(self, arrangement_id, exam, halls):
        self.arrangement_id = arrangement_id
        self.exam = exam
        self.halls = halls
        self.status = "pending"
        self.created_at = datetime.now().isoformat()
    def update_status(self, new_status):
        self.status = new_status

class SeatingOptimizer:
    def __init__(self, constraint_rule=None):
        self.constraint_rule = constraint_rule or ConstraintRule()
    def optimize(self, students, halls):
        sorted_students = sorted(students, key=lambda x: (x.branch, x.roll_no))
        all_seats = []
        for hall in halls:
            all_seats.extend(hall.seats)
        for seat in all_seats:
            seat.vacate()
        assigned = []
        for i, student in enumerate(sorted_students):
            if i >= len(all_seats):
                break
            for seat in all_seats[i:]:
                if seat.status == "available":
                    seat.occupy(student)
                    assigned.append((seat, student))
                    break
        return assigned

# ========== DATA STORAGE ==========
DATA_FILE = "data.json"
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"students": [], "halls": [], "exams": []}
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    data = load_data()
    return render_template("index.html", data=data)

@app.route("/add_student", methods=["POST"])
def add_student():
    try:
        roll_no = request.form.get("roll_no").strip()
        name = request.form.get("name").strip()
        class_name = request.form.get("class_name").strip()
        branch = request.form.get("branch").strip()
        s = Student(roll_no, name, class_name, branch)
        data = load_data()
        if any(st["roll_no"] == roll_no for st in data["students"]):
            flash(f"Roll {roll_no} already exists!", "error")
        else:
            data["students"].append(s.to_dict())
            save_data(data)
            flash(f"Student {name} added!", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("index"))

@app.route("/import_students", methods=["POST"])
def import_students():
    try:
        text = request.form.get("bulk_data", "")
        lines = text.strip().split("\n")
        data = load_data()
        count = 0
        for line in lines:
            if not line.strip(): continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                roll, name, cls = parts[0], parts[1], parts[2]
                branch = parts[3] if len(parts) > 3 else cls
                s = Student(roll, name, cls, branch)
                if not any(st["roll_no"] == roll for st in data["students"]):
                    data["students"].append(s.to_dict())
                    count += 1
        save_data(data)
        flash(f"Imported {count} students!", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("index"))

@app.route("/add_hall", methods=["POST"])
def add_hall():
    try:
        name = request.form.get("hall_name").strip()
        rows = int(request.form.get("rows"))
        cols = int(request.form.get("cols"))
        hall = Hall(f"HALL-{name}", name, rows, cols)
        data = load_data()
        data["halls"].append({"hall_id": hall.hall_id, "name": hall.name, "rows": hall.rows, "cols": hall.cols, "total_seats": len(hall.seats)})
        save_data(data)
        flash(f"Hall {name} created with {len(hall.seats)} seats!", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("index"))

@app.route("/add_exam", methods=["POST"])
def add_exam():
    try:
        subject = request.form.get("subject").strip()
        date = request.form.get("date")
        session_val = request.form.get("session")
        exam_id = f"EXAM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        exam = Exam(exam_id, subject, date, session_val)
        data = load_data()
        data["exams"].append(exam.to_dict())
        save_data(data)
        flash(f"Exam {subject} created!", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("index"))

@app.route("/generate", methods=["POST"])
def generate():
    data = load_data()
    if not data["students"] or not data["halls"] or not data["exams"]:
        flash("Add Students, Halls, Exams first!", "error")
        return redirect(url_for("index"))
    students = [Student(s["roll_no"], s["name"], s["class_name"], s["branch"]) for s in data["students"]]
    halls = [Hall(h["hall_id"], h["name"], h["rows"], h["cols"]) for h in data["halls"]]
    exam = Exam(data["exams"][-1]["exam_id"], data["exams"][-1]["subject"], data["exams"][-1]["date"], data["exams"][-1]["session"])
    optimizer = SeatingOptimizer(ConstraintRule("branch_alternate"))
    assigned = optimizer.optimize(students, halls)
    result = []
    for seat, student in assigned:
        result.append({"seat_id": seat.seat_id, "roll_no": student.roll_no, "name": student.name, "class_name": student.class_name, "branch": student.branch})
    arrangement = SeatingArrangement(f"ARR-{datetime.now().strftime('%H%M%S')}", exam, halls)
    arrangement.update_status("generated")
    session["last_arrangement"] = {"arrangement_id": arrangement.arrangement_id, "exam": exam.to_dict(), "result": result, "status": arrangement.status, "total": len(result)}
    return render_template("result.html", arrangement=session["last_arrangement"])

@app.route("/clear")
def clear():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    session.clear()
    flash("Cleared!", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
