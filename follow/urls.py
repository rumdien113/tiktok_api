from django.urls import path
from .views import FollowView, UnfollowView, FollowerListView, FollowingListView, CheckFollowStatusView

urlpatterns = [
    path('', FollowView.as_view(), name='follow-create'),
    path('unfollow/', UnfollowView.as_view(), name='follow-delete'),
    path('followers/', FollowerListView.as_view(), name='follower-list'),
    path('following/', FollowingListView.as_view(), name='following-list'),
    path('check-follow/<uuid:user_id>/', CheckFollowStatusView.as_view(), name='check-follow-status'),
]
