from django.contrib.auth.decorators import login_required
from django.urls import path

from .views.views1 import *
from .views.views2 import *
from .views.views3 import *
from .views.views4 import *

urlpatterns = [
    # views1
    path('', Conference.as_view(), name='welcome'),
    path('<slug>/close-submission', login_required(CloseSubmission.as_view()), name='close_submission'),
    path('<slug>/close-review', login_required(CloseReview.as_view()), name='close_review'),
    path('<slug>/close-status', login_required(CloseStatus.as_view()), name='close_status'),
    # views2
    path('<slug>', login_required(Welcome2.as_view()), name='slug_welcome'),
    path('<slug>/submit_paper', login_required(SubmitPaper.as_view()), name='submit_paper'),
    path('<slug>/view-all-paper', login_required(ViewAllPaper.as_view()), name='view_all_paper'),
    path('<slug>/view-paper/<int:pk>/detail', login_required(ViewDetail.as_view()), name='view_detail'),
    path('<slug>/add-author/<int:pk>', login_required(AddAuthor.as_view()), name='add_author'),
    path('<slug>/update-paper/<int:pk>', login_required(UpdatePaper.as_view()), name='update_paper'),
    path('<slug>/update-author/<int:pk>', login_required(UpdateAuthor.as_view()), name='update_author'),
    path('<slug>/view-paper/<int:pk>/delete', login_required(DeletePaper.as_view()), name='delete_paper'),
    # views3
    path('<slug>/view-paper/<int:pk>/select-user', login_required(SelectUser.as_view()), name='select_user'),
    path('<slug>/view-paper/<int:paper_pk>/select/<int:user_pk>', login_required(SelectedUser.as_view()),
         name='selected_user'),
    # path('view_paper/<int:paper_pk>/deselect/<int:user_pk>', login_required(deselect_user.as_view()),
    #    name='deselect_user'),
    # views4
    path('<slug>/review-list', login_required(ReviewerList.as_view()), name='review_list'),
    path('<slug>/review_paper/<int:pk>', login_required(ReviewPaper.as_view()), name='review_paper'),
]
