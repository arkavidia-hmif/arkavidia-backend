from django.contrib import admin
from arkav.arkalogica.models import Session, Question
from arkav.arkalogica.models import Choice, ChoiceImage
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
