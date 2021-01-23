from django.contrib import admin
from arkav.arkalogica.models import Session, Question
from arkav.arkalogica.models import Choice, ChoiceImage
from arkav.arkalogica.models import Answer, Submission
from arkav.arkalogica.models import QuestionImage


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'start_time', 'end_time']


class ChoiceInline(admin.TabularInline):
    model = Choice
    fields = ['tag', 'content', 'is_correct']
    extra = 1


class QuestionImageInline(admin.TabularInline):
    model = QuestionImage
    fields = ['question', 'url']
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'content']
    search_fields = ['title', 'content']
    inlines = [QuestionImageInline, ChoiceInline]


@admin.register(ChoiceImage)
class ChoiceImageAdmin(admin.ModelAdmin):
    model = ChoiceImage
    list_display = ['choice', 'url']
    list_filter = ['choice']


class AnswerInline(admin.StackedInline):
    model = Answer
    fields = ['info', 'iscorrect']
    readonly_fields = ['info', 'iscorrect']
    extra = 0

    def info(self, obj):
        return obj.tag + '. ' + obj.choice.content

    def iscorrect(self, obj):
        return obj.choice.is_correct
    iscorrect.short_description = 'Is Correct'
    iscorrect.boolean = True


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'start', 'end', 'correct_answer', 'wrong_answer', 'not_answered']
    search_fields = ['user']
    inlines = [AnswerInline]

    def correct_answer(self, obj):
        correct = 0
        for x in obj.answer.all():
            if x.choice.is_correct:
                correct += 1
        return correct
    correct_answer.short_description = 'Correct Answer'

    def wrong_answer(self, obj):
        wrong = 0
        for x in obj.answer.all():
            if not x.choice.is_correct:
                wrong += 1
        return wrong
    wrong_answer.short_description = 'Wrong Answer'

    def not_answered(self, obj):
        answered = obj.answer.count()
        total_questions = Question.objects.count()
        return total_questions-answered
    not_answered.short_description = 'Empty Answer'