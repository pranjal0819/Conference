from django.contrib.auth.decorators import login_required
from django.urls import path

from .views.views1 import *
from .views.views2 import *
from .views.views3 import *

urlpatterns = {
    # view1
    path('', Conference.as_view(), name='welcome'),
    path('<slug>/close-submission', login_required(CloseSubmission.as_view()), name='close_submission'),
    path('<slug>/close-review', login_required(CloseReview.as_view()), name='close_review'),
    path('<slug>/close-status', login_required(CloseStatus.as_view()), name='close_status'),
    # view2
    path('<slug>/welcome2', login_required(Welcome2.as_view()), name='slug_welcome'),
    path('<slug>/submit_paper', login_required(SubmitPaper.as_view()), name='submit_paper'),
    path('<slug>/view-all-paper', login_required(ViewAllPaper.as_view()), name='view_all_paper'),
    path('<slug>/view-paper/<int:pk>/detail', login_required(ViewDetail.as_view()), name='view_detail'),
    path('<slug>/view-paper/<int:pk>/delete', login_required(DeletePaper.as_view()), name='delete_paper'),
    # view3
    path('<slug>view-paper/<int:pk>/select-user', login_required(SelectUser.as_view()), name='select_user'),
    path('<slug>view-paper/<int:paper_pk>/select/<int:user_pk>', login_required(SelectedUser.as_view()),
         name='selected_user'),
    path('<slug>review-list', login_required(ReviewList.as_view()), name='review_list'),
    path('<slug>review_paper/<int:pk>', login_required(ReviewPaper.as_view()), name='review_paper'),
    # path('view_paper/<int:paper_pk>/deselect/<int:user_pk>', login_required(deselect_user.as_view()), name='deselect_user'),
}
