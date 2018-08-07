from django.urls import path
from django.contrib.auth.decorators import login_required
from .views.views1 import *
from .views.views2 import *

urlpatterns = [
    path('welcome', Welcome.as_view(), name='welcome'),
    path('submit_paper', login_required(SubmitPaper.as_view()), name='submit_paper'),
    path('view-all-paper', login_required(ViewAllPaper.as_view()), name='view_all_paper'),
    path('view-paper/<int:pk>/detail', login_required(ViewDetail.as_view()), name='view_detail'),
    path('view-paper/<int:pk>/delete', login_required(DeletePaper.as_view()), name='delete_paper'),
    path('view-paper/<int:pk>/select-user', login_required(SelectUser.as_view()), name='select_user'),
    path('view-paper/<int:paper_pk>/select/<int:user_pk>', login_required(SelectedUser.as_view()),
         name='selected_user'),
    path('review-list', login_required(ReviewList.as_view()), name='review_list'),
    path('review_paper/<int:pk>', login_required(ReviewPaper.as_view()), name='review_paper'),
    #path('view_paper/<int:paper_pk>/deselect/<int:user_pk>', login_required(deselect_user.as_view()), name='deselect_user'),
]
