class Student:
    def __init__(self, roll_no, name, class_name, email=""):
        self.roll_no = roll_no
        self.name = name
        self.class_name = class_name
        self.email = email
        self.status = "Registered"

class ClassRoom:
    def __init__(self, class_id, name, total_students):
        self.class_id = class_id
        self.name = name
        self.total_students = total_students
        self.students = []

class Hall:
    def __init__(self, hall_id, name, rows, cols):
        self.hall_id = hall_id
        self.name = name
        self.rows = rows
        self.cols = cols
        self.total_seats = rows * cols

class Seat:
    def __init__(self, seat_id, hall_id, row, col):
        self.seat_id = seat_id
        self.hall_id = hall_id
        self.row = row
        self.col = col
        self.is_occupied = False
        self.student_roll = None

class Exam:
    def __init__(self, exam_id, subject, date, session):
        self.exam_id = exam_id
        self.subject = subject
        self.date = date
        self.session = session

class SeatingArrangement:
    def __init__(self, arrangement_id, exam_id, hall_id):
        self.arrangement_id = arrangement_id
        self.exam_id = exam_id
        self.hall_id = hall_id
        self.assignments = {}
        self.status = "Draft"

class ConstraintRule:
    def __init__(self, rule_id, rule_type, description):
        self.rule_id = rule_id
        self.rule_type = rule_type
        self.description = description
    def validate(self, s1, s2):
        return s1.class_name!= s2.class_name

class SeatingOptimizer:
    def __init__(self, students, seats, rules):
        self.students = students
        self.seats = seats
        self.rules = rules
    def optimize(self):
        sorted_students = sorted(self.students, key=lambda x: x.class_name)
        arrangement = {}
        for i, student in enumerate(sorted_students):
            if i < len(self.seats):
                arrangement[self.seats[i].seat_id] = student.roll_no
                self.seats[i].is_occupied = True
                self.seats[i].student_roll = student.roll_no
        return arrangement
