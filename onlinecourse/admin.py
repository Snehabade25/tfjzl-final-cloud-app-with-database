
from django.contrib import admin

from .models import (
    Course,
    Lesson,
    Instructor,
    Learner,
    Question,
    Choice,
    Submission,
)


# Inline for choices inside a question
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2


# Inline for questions inside a course
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2
    show_change_link = True


# Lesson inline
class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# Course administration
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline, QuestionInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


# Lesson administration
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']
    list_filter = ['course']
    search_fields = ['title']


# Question administration
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('question_text', 'course', 'grade')
    list_filter = ['course']
    search_fields = ['question_text']


# Choice administration
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'is_correct')
    list_filter = ['is_correct']
    search_fields = ['choice_text']


# Submission administration
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment', 'timestamp')
    list_filter = ['timestamp']


# Register models
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Submission, SubmissionAdmin)
