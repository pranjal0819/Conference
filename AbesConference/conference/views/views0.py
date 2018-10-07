from django.core.exceptions import ObjectDoesNotExist

from ..models import ConferenceRecord, PaperRecord, PcMemberRecord, ReviewPaperRecord, AuthorRecord


# noinspection PyBroadException
def get_conference(request, slug, error_code):
    try:
        conference = ConferenceRecord.objects.get(slug=slug)
        if conference.owner == request.user or request.user.is_staff or request.user.is_superuser:
            return conference, True
        return conference, False
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist("Conference Not Found. Error Code: " + error_code)


def get_paper(conference, pk, error_code):
    try:
        return PaperRecord.objects.get(conference=conference, pk=pk)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist("Paper Not Found. Error Code: " + error_code)


def get_all_paper(conference):
    return PaperRecord.objects.filter(conference=conference)


def get_all_paper_user(conference, user):
    return PaperRecord.objects.filter(conference=conference, user=user)


def get_pc_member(conference, email, error_code):
    try:
        return PcMemberRecord.objects.get(pcCon=conference, pcEmail=email)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist("PC Member Not Found. Error Code: " + error_code)


def get_all_pc_member(conference):
    return PcMemberRecord.objects.filter(pcCon=conference)


def get_all_accepted_pc_member(conference):
    return PcMemberRecord.objects.filter(pcCon=conference, accepted=5)


def get_all_pc_member_for_paper(conference, paper):
    return PcMemberRecord.objects.filter(pcCon=conference, demand=paper)


def get_review_paper(pc_user, paper, error_code):
    try:
        return ReviewPaperRecord.objects.get(reviewUser=pc_user, paper=paper)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist("Review Not Found. Error Code: " + error_code)


def get_all_review_paper(conference, pc_user):
    return ReviewPaperRecord.objects.filter(reviewCon=conference, reviewUser=pc_user)


def get_author(pk, error_code):
    try:
        return AuthorRecord.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist("Author Not Found. Error Code: " + error_code)
