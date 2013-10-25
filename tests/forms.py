from django import forms


class PageForm(forms.Form):
    """Form that handles pages within a test"""

    def __init__(self, *args, **kwargs):
        page = kwargs.pop('page', None)

        super(PageForm, self).__init__(*args, **kwargs)

        # Fetch page related questions
        questions = page.questions.all()

        for question in questions:
            # Returns related answers as list of 2-tuples
            # e.g.: [(1, 'answer1'), (2, 'answers'), ...]
            answers = question.answers.values_list('id', 'name')

            # Add radio fields representing each question's answers
            self.fields['question_{index}'.format(index=question.id)] = \
                forms.MultipleChoiceField(label=question.name,
                                          required=True,
                                          choices=answers,
                                          widget=forms.CheckboxSelectMultiple)
