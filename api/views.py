import random
from dataclasses import dataclass

from django.shortcuts import render
from rest_framework.request import Request

from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from api.models import User, Role, Image


# Create your views here.

class Test(APIView):

    def get(self, request):
        print('This is GET request.')
        print(f'Request data: {request.data}')
        print(f'Request query params: {request.query_params}')

        users = list(User.objects.values())
        return Response(users, status=status.HTTP_200_OK)

    def post(self, request):
        print(f'Request data: {request.data}')
        print(f'Request query params: {request.query_params}')

        return Response(
            {
                "status": "ok",
                "message": "POST request received",
                "data": request.data
            },
            status=status.HTTP_200_OK
        )


class Signup(APIView):

    def post(self, request):
        print('===== SIGNUP START =====')

        data = request.data
        print(f'[DEBUG] Post data: {data}')

        username = data.get("username")
        password = data.get("password")
        name = data.get("name")
        surname = data.get("surname")
        bio = data.get("bio", "")
        email = data.get("email")
        phone = data.get("phone", "")

        print("[DEBUG] Parsed fields:")
        print(f"  username={username}")
        print(f"  password_length={len(password) if password else 'None'}")
        print(f"  name={name}")
        print(f"  surname={surname}")
        print(f"  email={email}")
        print(f"  phone={phone}")

        # required fields check
        if not all([username, password, name, surname, email]):
            print("[ERROR] Missing required fields")
            return Response(
                {
                    "status": "error",
                    "message": "Missing required fields"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # pass length check (>=8)
        if len(password) < 8:
            print("[ERROR] Password too short")
            return Response(
                {
                    "status": "error",
                    "message": "Password must be at least 8 characters long"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            print(f"[ERROR] Username already exists: {username}")
            return Response(
                {
                    "status": "error",
                    "message": "Username already exists"
                },
                status=status.HTTP_409_CONFLICT
            )

        if User.objects.filter(email=email).exists():
            print(f"[ERROR] Email already exists: {email}")
            return Response(
                {
                    "status": "error",
                    "message": "Email already exists"
                },
                status=status.HTTP_409_CONFLICT
            )

        try:
            role = Role.objects.get(id=2)
            print(f"[DEBUG] Role found: id={role.id}, name={role}")
        except Role.DoesNotExist:
            print("[ERROR] Default role (id=2) not found")
            return Response(
                {
                    "status": "error",
                    "message": "Default role not found"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        random_image_id = random.randint(1, 10)
        image = Image.objects.filter(id=random_image_id).first()
        if image:
            print(f"[DEBUG] Image found: id={image.id}")
        else:
            print(f"[WARN] Image not found for id={random_image_id}")

        hashed_password = make_password(password)
        print("[DEBUG] Password hashed successfully")

        try:
            user = User.objects.create(
                username=username,
                password=hashed_password,
                name=name,
                surname=surname,
                bio=bio,
                location="",
                email=email,
                phone=phone,
                role=role,
                image=image
            )
            print(f"[SUCCESS] User created with id={user.id}")
        except Exception as e:
            print("[ERROR] Failed to create user")
            print(f"[ERROR DETAILS] {e}")
            return Response(
                {
                    "status": "error",
                    "message": "Failed to create user"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        print("=== SIGNUP END ===")

        return Response(
            {
                "status": "success",
                "message": "User created successfully",
                "user_id": user.id
            },
            status=status.HTTP_201_CREATED
        )


class Login(APIView):

    def post(self, request):
        print('===== LOGIN START =====')

        data = request.data
        print(f'[DEBUG] Post data: {data}')

        email = data.get("email")
        password = data.get("password")

        # required fields check
        if not email or not password:
            print("[ERROR] Email or password missing")
            return Response(
                {
                    "status": "error",
                    "message": "Email and password are required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # try to fetch user
        try:
            user = User.objects.get(email=email)
            print(f"[DEBUG] User found: id={user.id}, username={user.username}")
        except User.DoesNotExist:
            print("[ERROR] User not found for email:", email)
            return Response(
                {
                    "status": "error",
                    "message": "Invalid email or password"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # check password
        if not check_password(password, user.password):
            print("[ERROR] Invalid password")
            return Response(
                {
                    "status": "error",
                    "message": "Invalid email or password"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        print("[SUCCESS] Login successful")
        print("===== LOGIN END =====")

        return Response(
            {
                "status": "success",
                "message": "Login successful",
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            },
            status=status.HTTP_200_OK
        )


class DeleteUser(APIView):

    def delete(self, request):
        print("===== DELETE USER START =====")

        data = request.data
        print(f'[DEBUG] Requst data: {data}')

        requester_id = data.get("requester_id") # who is requesting to delete
        target_user_id = data.get("target_user_id")   # who should be deleted

        # requried params check
        if not requester_id or not target_user_id:
            print("[ERROR] requester_id or user_id missing")
            return Response(
                {
                    "status": "error",
                    "message": "requester_id and user_id are required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # try to fetch requester
        try:
            requester = User.objects.get(id=requester_id)
            print(f"[DEBUG] Requester found: id={requester.id}, role={requester.role.id}")
        except User.DoesNotExist:
            print("[ERROR] Requester not found")
            return Response(
                {
                    "status": "error",
                    "message": "Requester not found"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # try to fetch targer user
        try:
            target_user = User.objects.get(id=target_user_id)
            print(f"[DEBUG] Target user found: id={target_user.id}")
        except User.DoesNotExist:
            print("[ERROR] Target user not found")
            return Response(
                {
                    "status": "error",
                    "message": "User to delete not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # check authorization
        is_self = requester.id == target_user.id
        is_admin = requester.role.id == 1

        if not (is_self or is_admin):
            print("[ERROR] Unauthorized delete attempt")
            return Response(
                {
                    "status": "error",
                    "message": "You are not authorized to delete this user"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # delete user
        try:
            target_user.delete()
            print(f"[SUCCESS] User deleted: id={target_user_id}")
        except Exception as e:
            print("[ERROR] Failed to delete user")
            print(f"[ERROR DETAILS] {e}")
            return Response(
                {
                    "status": "error",
                    "message": "Failed to delete user"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        print("===== DELETE USER END =====")

        return Response(
            {
                "status": "success",
                "message": "User deleted successfully"
            },
            status=status.HTTP_200_OK
        )