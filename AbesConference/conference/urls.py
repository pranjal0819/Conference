from django.contrib.auth.decorators import login_required
from django.urls import path

from .views.views1 import *
from .views.views2 import *
from .views.views4 import *
from .views.views3 import *
from .views.views5 import *

urlpatterns = [
    # views1
    path('create_conference', CreateConference.as_view(), name='create_conference'),
    path('<slug>/close_submission', login_required(CloseSubmission.as_view()), name='close_submission'),
    path('<slug>/close_review', login_required(CloseReview.as_view()), name='close_review'),
    path('<slug>/close_status', login_required(CloseStatus.as_view()), name='close_status'),
    path('<slug>/open_submission', login_required(OpenSubmission.as_view()), name='open_submission'),
    path('<slug>/open_review', login_required(OpenReview.as_view()), name='open_review'),
    path('<slug>/open_status', login_required(OpenStatus.as_view()), name='open_status'),
    # views2
    path('<slug>', login_required(Welcome.as_view()), name='slug_welcome'),
    path('<slug>/submit_paper', login_required(SubmitPaper.as_view()), name='submit_paper'),
    path('<slug>/view_all_paper', login_required(ViewAllPaper.as_view()), name='view_all_paper'),
    path('<slug>/view_paper/<int:pk>/detail', login_required(ViewDetail.as_view()), name='view_detail'),
    path('<slug>/download_paper/<int:pk>', login_required(DownloadPaper.as_view()), name='download_paper'),
    path('<slug>/add_author/<int:pk>', login_required(AddAuthor.as_view()), name='add_author'),
    path('<slug>/update_paper/<int:pk>', login_required(UpdatePaper.as_view()), name='update_paper'),
    path('<slug>/update_author/<int:pk>', login_required(UpdateAuthor.as_view()), name='update_author'),
    path('<slug>/view_paper/<int:pk>/delete', login_required(DeletePaper.as_view()), name='delete_paper'),
    # views3
    path('<slug>/accepted', login_required(AcceptToReview.as_view()), name='accept_to_review'),
    path('<slug>/demand_paper/<int:pk>', login_required(Demand.as_view()), name='demand_paper'),
    path('<slug>/review_paper_list', login_required(ReviewPaperList.as_view()), name='review_list'),
    path('<slug>/review_paper/<int:pk>', login_required(ReviewPaper.as_view()), name='review_paper'),
    path('<slug>/accept_paper/<int:pk>', login_required(AcceptPaper.as_view()), name='accept_paper'),
    path('<slug>/reject_paper/<int:pk>', login_required(RejectPaper.as_view()), name='reject_paper'),
    # views4
    path('<slug>/manage_pc_member', login_required(ManagePCMember.as_view()), name='manage_pc_member'),
    path('<slug>/add_pc_member', login_required(AddPcMember.as_view()), name='add_pc_member'),
    path('<slug>/confirm/<uidb64>/<token>/', confirm, name='confirm'),
    path('<slug>/<int:pk>/email', login_required(SendEmail.as_view()), name='send_email'),
    path('<slug>/delete/<email>', login_required(DeletePCMember.as_view()), name='delete_pc_member'),
    path('<slug>/<int:pk>/select-user', login_required(PcMembers.as_view()), name='select_user'),
    path('<slug>/<int:pk>/show_reviews', login_required(ShowReviews.as_view()), name='show_review'),
    path('<slug>/<int:paper_pk>/select/<int:user_pk>', login_required(SelectedUser.as_view()), name='selected_user'),
    # path('<slug>/<int:paper_pk>/deselect/<int:user_pk>', login_required(DeselectUser.as_view()), name='deselect_user'),
    # view5
    path('<slug>/email_to_author', login_required(EmailToAuthors.as_view()), name='email_to_author'),
]
