
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
import logging

from .models import (
    Course,
    Enrollment,
    Question,
    Choice,
    Submission,
)

logger = logging.getLogger(__name__)


# User registration
def registration_request(request):
    context = {}

    if request.method == 'GET':
        return render(
            request,
            'onlinecourse/user_registration_bootstrap.html',
            context
        )

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        if User.objects.filter(username=username).exists():
            context['message'] = "User already exists."
            return render(
                request,
                'onlinecourse/user_registration_bootstrap.html',
                context
            )

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        login(request, user)
        return redirect("onlinecourse:index")

    return redirect("onlinecourse:index")


# User login
def login_request(request):
    context = {}

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')

        context['message'] = "Invalid username or password."
        return render(
            request,
            'onlinecourse/user_login_bootstrap.html',
            context
        )

    return render(
        request,
        'onlinecourse/user_login_bootstrap.html',
        context
    )


# User logout
def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


# Check enrollment
def check_if_enrolled(user, course):
    if user.is_authenticated:
        return Enrollment.objects.filter(
            user=user,
            course=course
        ).exists()

    return False


# Course list
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]

        for course in courses:
            course.is_enrolled = check_if_enrolled(user, course)

        return courses


# Course details
class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


# Enroll in a course
@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)

    if not is_enrolled:
        Enrollment.objects.create(
            user=user,
            course=course,
            mode='honor'
        )
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(
        reverse(
            viewname='onlinecourse:course_details',
            args=(course.id,)
        )
    )


# Collect selected answers from the exam form
def extract_answers(request):
    submitted_answers = []

    for key in request.POST:
        if key.startswith('choice'):
            try:
                choice_id = int(request.POST[key])
                submitted_answers.append(choice_id)
            except (TypeError, ValueError):
                continue

    return submitted_answers


# Submit exam answers
@login_required
@transaction.atomic
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method != 'POST':
        return redirect(
            'onlinecourse:course_details',
            course_id=course.id
        )

    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=course
    )

    submission = Submission.objects.create(
        enrollment=enrollment
    )

    answer_ids = extract_answers(request)

    # Only accept choices belonging to questions in this course.
    valid_choices = Choice.objects.filter(
        id__in=answer_ids,
        question__course=course
    ).distinct()

    submission.choices.add(*valid_choices)

    return redirect(
        'onlinecourse:show_exam_result',
        course_id=course.id,
        submission_id=submission.id
    )


# Display exam results
@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)

    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        enrollment__user=request.user,
        enrollment__course=course
    )

    selected_choices = submission.choices.all()

    # Map each question to the selected choice, if any.
    selected_by_question = {
        choice.question_id: choice
        for choice in selected_choices
    }

    questions = Question.objects.filter(
        course=course
    ).prefetch_related('choices')

    results = []
    score = 0
    total_score = 0

    for question in questions:
        choices = list(question.choices.all())
        selected_choice = selected_by_question.get(question.id)

        correct_choices = [
            choice for choice in choices if choice.is_correct
        ]

        is_correct = (
            selected_choice is not None
            and selected_choice.is_correct
        )

        if is_correct:
            score += question.grade

        total_score += question.grade

        results.append({
            'question': question,
            'choices': choices,
            'selected_choice': selected_choice,
            'correct_choices': correct_choices,
            'is_correct': is_correct,
        })

    passed = total_score > 0 and score >= total_score * 0.5

    context = {
        'course': course,
        'submission': submission,
        'results': results,
        'score': score,
        'total_score': total_score,
        'passed': passed,
    }

    return render(
        request,
        'onlinecourse/exam_result_bootstrap.html',
        context
    )
