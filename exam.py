from datetime import datetime
class TabObserver:
    def __init__(self, session):
        self.session = session
    def update(self, event):
        if event.lower() == "tab_hidden":
            self.session.add_violation("tab_hidden")
class ProctorSubject:
    def __init__(self):
        self.observers = []
    def attach(self, observer):
        self.observers.append(observer)
    def notify(self, event):
        for observer in self.observers:
            observer.update(event)
class FaceObserver:
    def __init__(self, session):
        self.session = session
    def update(self, event):
        if event.lower() == "two_faces":
            self.session.add_violation("two_faces")
        elif event.lower() == "no_face":
            self.session.add_violation("no_face")
class GazeObserver:
    def __init__(self, session):
        self.session = session
    def update(self, event):
        if event.lower() == "gaze_away":
            self.session.add_violation("gaze_away")

class Violation:
    def __init__(self, violation_type):
        self.violation_type = violation_type
        self.time = datetime.now()
class Submission:
    def __init__(self, question_id, code, percent):
        self.question_id = question_id
        self.code = code
        self.percent = percent
        self.time = datetime.now()
class ExamSession:
    def __init__(self, max_warnings):
        self.violations = []
        self.max_warnings = max_warnings
        self.score = 0
        self.warnings = 0
        self.status = "active"
        self.submissions = []
    def add_submission(self, question_id, code, percent):
        self.submissions.append(Submission(question_id, code, percent))
    def get_best_submission_percent(self, question_id):
        question_submission = [s.percent for s in self.submissions if s.question_id == question_id]
        return max(question_submission) if question_submission else 0
    def add_warning(self):
        self.warnings += 1
        if self.warnings >= self.max_warnings:
            self.status = "blocked"
    def add_score(self, points):
        self.score += points
    def add_violation(self, violation_type):
        self.violations.append(Violation(violation_type))
        self.add_warning()

session = ExamSession(3)
session.add_submission(1, "print(1)", 100)
session.add_submission(1, "print(2)", 70)
session.add_submission(2, "x = 1", 100)
print(len(session.submissions))
print(session.get_best_submission_percent(1))