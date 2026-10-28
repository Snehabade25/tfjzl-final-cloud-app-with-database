
from django.urls import path
from . import views

app_name = 'onlinecourse'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='index'),
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),

    path(
        'course/<int:pk>/',
        views.CourseDetailView.as_view(),
        name='course_details'
    ),

    path(
        'course/<int:course_id>/enroll/',
        views.enroll,
        name='enroll'
    ),

    path(
        'course/<int:course_id>/submit/',
        views.submit,
        name='submit'
    ),

    path(
        'course/<int:course_id>/exam_result/<int:submission_id>/',
        views.show_exam_result,
        name='show_exam_result'
    ),
]
