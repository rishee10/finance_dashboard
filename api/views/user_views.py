from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from ..models import User
from ..serializers import UserSerializer, UserUpdateSerializer
from ..permissions import IsAdminRole


class UserListView(ListAPIView):
    """Admin: list all users."""
    permission_classes = [IsAdminRole]
    serializer_class   = UserSerializer
    queryset           = User.objects.all().order_by('date_joined')


class UserDetailView(RetrieveUpdateAPIView):
    """Admin: view or update a specific user's role/status."""
    permission_classes = [IsAdminRole]
    queryset           = User.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        # Prevent admin from deactivating themselves
        instance = self.get_object()
        if instance == request.user and request.data.get('is_active') is False:
            return Response(
                {"error": "You cannot deactivate your own account."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)