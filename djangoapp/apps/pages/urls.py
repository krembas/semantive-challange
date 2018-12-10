from django.urls import path

from djangoapp.apps.pages.views import TaskView, PageContentView, PageImagesView, TaskStatusView

urlpatterns = [
    path('', TaskView.as_view()),
    path('<int:task_id>/status/', TaskStatusView.as_view()),
    path('<int:task_id>/text/', PageContentView.as_view()),
    path('<int:task_id>/images/', PageImagesView.as_view()),
]
