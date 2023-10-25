from django.urls import path

from actions.views import (
    # AcceptInvitation,
    # CancelInvitation,
    CreateInvitation,
    # CreateRequest,
    # LeaveFromCompany,
    # MemberList,
    # MyInvites,
    # MyRequests,
    # RemoveUser,
)

urlpatterns = [
    path("invite/create", CreateInvitation.as_view()),
    # path("invite/cancel", CancelInvitation.as_view()),
    # path("invite/accept", AcceptInvitation.as_view()),
    # path("request", CreateRequest.as_view()),
    # path("remove", RemoveUser.as_view()),
    # path("leave", LeaveFromCompany.as_view()),
    # path("member-list", MemberList.as_view()),
    # path("my/invites", MyInvites.as_view()),
    # path("my/requests", MyRequests.as_view())
]
