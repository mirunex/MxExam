class User:
    def __init__(self, name, role):
        self.name = name
        self.role = role
    def info(self):
        return f"Name: {self.name}, Role: {self.role}"
    def is_teacher(self):
        return self.role.lower() == "teacher"
class Student(User):
    def __init__(self, name):
        super().__init__(name, "student")
        self.exam_history = []
class Teacher(User):
    def __init__(self, name):
        super().__init__(name, "teacher")
    def can_create_exam(self):
        return True
a = Student("Alice")
b = Teacher("Araz")
print(a.info())
print(a.exam_history)
print(a.is_teacher())
print(b.info())
print(b.can_create_exam())
