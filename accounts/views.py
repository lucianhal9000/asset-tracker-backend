from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializer


class RegisterView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        User = get_user_model()
        email_field = getattr(User, 'EMAIL_FIELD', 'email')
        email_value = getattr(user, email_field, None) or getattr(user, 'email', None)

        return Response({'email': email_value}, status=status.HTTP_201_CREATED)
