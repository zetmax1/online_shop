from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (AccountsViewSet, CustomTokenObtainPairView,
                            ResetPasswordView, SendPasswordResetCodeView)

router = DefaultRouter()
router.register('accounts', AccountsViewSet, basename='accounts')

urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('send-reset-code/', SendPasswordResetCodeView.as_view(), name='send-reset-code'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]