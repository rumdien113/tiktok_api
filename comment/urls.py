from django.urls import path
from .views import CommentListCreateView, CommentRetrieveUpdateDestroyView, CommentReplyListView, CommentListViewByPost

urlpatterns = [
    path('', CommentListCreateView.as_view(), name='comment-list-create'),
    path('<uuid:pk>/', CommentRetrieveUpdateDestroyView.as_view(), name='comment-retrieve-update-destroy'),
    path('<uuid:parent_comment_id>/replies/', CommentReplyListView.as_view(), name='comment-replies-list'),
    path('posts/<uuid:post_id>/comments/', CommentListViewByPost.as_view(), name='comment-list-by-post'), # New URL
]
