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
    fields = ['choice', 'question', 'iscorrect']
    readonly_fields = ['choice', 'question', 'iscorrect']
    extra = 0

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
        return obj.answer.filter(choice__is_correct=True).count()
    correct_answer.short_description = 'Correct Answer'

    def wrong_answer(self, obj):
        return obj.answer.filter(choice__is_correct=False).count()
    wrong_answer.short_description = 'Wrong Answer'

    def not_answered(self, obj):
        answered = obj.answer.count()
        total_questions = obj.session.questions.count()
        return total_questions-answered
    not_answered.short_description = 'Empty Answer'
