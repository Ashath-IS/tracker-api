from django.urls import path
from .views import create_question, create_user, test_api, fetch_user_by_email, get_questions_by_topic, submit_answer, get_user_progress

urlpatterns = [
    path('test/', test_api),
    path('users/', fetch_user_by_email),
    path('create/', create_user),
    path('questions/create/', create_question),
    path('questions/', get_questions_by_topic),
    path('answer/submit/',submit_answer),
    path('progress/', get_user_progress)
]
