# from rest_framework import generics, permissions
# from .models import Tag
# from .serializers import TagSerializer, TagCreateSerializer
# from post_tag.models import PostTag
# from post_tag.serializers import PostTagSerializer, PostTagCreateSerializer
#
# class TagListView(generics.ListCreateAPIView):
#     queryset = Tag.objects.all()
#     serializer_class = TagSerializer
#     permission_classes = [permissions.IsAdminUser] # Chỉ admin mới có thể tạo và xem danh sách tag
#
#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return TagCreateSerializer
#         return TagSerializer
#
# class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Tag.objects.all()
#     serializer_class = TagSerializer
#     permission_classes = [permissions.IsAdminUser] # Chỉ admin mới có thể xem, cập nhật và xóa tag
#
# class PostTagListView(generics.ListAPIView):
#     queryset = PostTag.objects.all()
#     serializer_class = PostTagSerializer
#     permission_classes = [permissions.IsAdminUser] # Chỉ admin mới có thể xem danh sách post-tag
#
# class PostTagCreateView(generics.CreateAPIView):
#     queryset = PostTag.objects.all()
#     serializer_class = PostTagCreateSerializer
#     permission_classes = [permissions.IsAuthenticated] # Bất kỳ người dùng đã xác thực nào cũng có thể thêm tag vào post (tùy thuộc logic ứng dụng)
#
# class PostTagDetailView(generics.RetrieveDestroyAPIView):
#     queryset = PostTag.objects.all()
#     serializer_class = PostTagSerializer
#     permission_classes = [permissions.IsAdminUser] # Chỉ admin mới có thể xem và xóa liên kết post-tag
