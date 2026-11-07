from core.models.question import Question


class QuestionFactory:
    @staticmethod
    def create_question(question_type, text, points=1.0, created_by = None, **kwargs):
        """
        Gələn sual növünə görə (test, written, code) müvafiq sual obyekti yaradır və bazaya saxlayır.
        """
        if question_type not in dict(Question.QUESTION_TYPES):
            raise ValueError(f"Yanlış sual növü: {question_type}")

        question = Question(
            text=text,
            points=points,
            question_type=question_type,
            option_a=kwargs.get('option_a'),
            option_b=kwargs.get('option_b'),
            option_c=kwargs.get('option_c'),
            option_d=kwargs.get('option_d'),
            correct_option=kwargs.get('correct_option'),
            created_by=created_by
        )
        question.full_clean()
        question.save()
        return question