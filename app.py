from flask import Flask, render_template, request, redirect
from models import Student, ClassRoom, Hall, Seat, Exam, SeatingArrangement, ConstraintRule, SeatingOptimizer
import os

app = Flask(__name__)

students_db = []
halls_db = []
exams_db = []
arrangements_db = []

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_student':
            s = Student(request.form['roll_no'], request.form['name'], request.form['class_name'])
            students_db.append(s)
        elif action == 'add_hall':
            h = Hall(len(halls_db)+1, request.form['hall_name'], int(request.form['rows']), int(request.form['cols']))
            halls_db.append(h)
        elif action == 'add_exam':
            e = Exam(len(exams_db)+1, request.form['subject'], request.form['date'], request.form['session'])
            exams_db.append(e)
        elif action == 'generate':
            if students_db and halls_db:
                seats = []
                hall = halls_db[0]
                sid=1
                for r in range(hall.rows):
                    for c in range(hall.cols):
                        seats.append(Seat(sid, hall.hall_id, r, c))
                        sid+=1
                rule = ConstraintRule(1, "NoSameClassAdjacent", "Same class not adjacent")
                optimizer = SeatingOptimizer(students_db, seats, [rule])
                mapping = optimizer.optimize()
                arr = SeatingArrangement(len(arrangements_db)+1, 1, hall.hall_id)
                arr.assignments = mapping
                arr.status = "Generated"
                arrangements_db.append(arr)
        return redirect('/')
    return render_template('index.html', students=students_db, halls=halls_db, exams=exams_db, arrangements=arrangements_db)

@app.route('/upload', methods=['POST'])
def upload():
    return home()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
