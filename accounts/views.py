from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import CustomUser, PasswordResetCode
from accounts.serializers import (AccountsSerializer,
                                  AccountsTokenObtainPairSerializer,
                                  ResetPasswordSerializer,
                                  SendResetCodeSerializer)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = AccountsTokenObtainPairSerializer


class AccountsViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = AccountsSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "data": serializer.data,
            "status": status.HTTP_201_CREATED,
            "headers": headers,
            "message": "User created successfully"
        },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "data": serializer.data,
            status: status.HTTP_200_OK,
            "message": "User updated successfully"

        },
        status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        self.update(request, *args, **kwargs)
        return Response({
            "status": status.HTTP_200_OK,
            "message": "User updated successfully"
        },
        status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": status.HTTP_204_NO_CONTENT,
            "message": "User deleted successfully"
        },
        status=status.HTTP_204_NO_CONTENT)


class SendPasswordResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendResetCodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Code has been sent to your email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password has been successfully changed"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
