from abc import ABC, abstractmethod
class Question(ABC):
    def __init__(self, text):
        self.text = text

    @abstractmethod
    def score(self, answer):
        pass

class TestQuestion(Question):
    def __init__(self, text, options, correct_index):
        super().__init__(text)
        self.options = options
        self.correct_index = correct_index
    def score(self, answer):
        return 1 if answer == self.correct_index else 0
class WrittenQuestion(Question):
    def score(self, answer):
        return None
q = TestQuestion("Python nədir?", ["ilan", "proqramlaşdırma dili", "meyvə"], 1)
q2 = WrittenQuestion("Mueyyen inteqralin hell yolllari haqqinda danisin")

questions = [q, q2]
answers = [1, "Müəyyən inteqralın həll yolları bunlardır..."]
for i in range(len(questions)):
    if questions[i].score(answers[i]) is not None:
        print(questions[i].score(answers[i]))
    else:
        print("Muellim ozu yoxlayacaq")
