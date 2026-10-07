from django.contrib.auth import (
    get_user_model,
    authenticate,
    login,
    logout,
)
from django.contrib import messages
from django.shortcuts import render, redirect

from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import RegisterSerializer, UserSerializer


User = get_user_model()


# =========================================================
# HTML LOGIN
# =========================================================

def html_login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(request, user)

            if user.is_superuser or user.role == "ADMIN":
                return redirect("admin-dashboard")

            elif user.role == "FACULTY":
                return redirect("faculty-dashboard")

            elif user.role == "PLACEMENT":
                return redirect("placement-dashboard")

            elif user.role == "STUDENT":
                return redirect("student-dashboard")

            messages.error(
                request,
                "User role is not configured correctly."
            )

            logout(request)

        else:
            messages.error(
                request,
                "Invalid username or password."
            )

    return render(request, "login.html")


# =========================================================
# HTML LOGOUT
# =========================================================

def html_logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")


# =========================================================
# API REGISTER
# =========================================================

class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()

    serializer_class = RegisterSerializer

    permission_classes = [
        permissions.AllowAny
    ]


# =========================================================
# JWT LOGIN
# =========================================================

class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        token["username"] = user.username
        token["role"] = user.role

        return token

    def validate(self, attrs):

        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "phone": self.user.phone,
            "role": self.user.role,
        }

        return data


class LoginView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer


# =========================================================
# API PROFILE
# =========================================================

class ProfileView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = UserSerializer

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):
        return self.request.user