from django.urls import path
from .views import PostListView, PostDetailView, UserPostListView, RandomPostView, PostSearchView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list-create'),
    path('random/', RandomPostView.as_view(), name='random-post'),
    path('user/<str:user_id>/', UserPostListView.as_view(), name='user-posts'),
    path('search/', PostSearchView.as_view(), name='post-search'),
    path('<str:post_id>/', PostDetailView.as_view(), name='post-detail'),
]
