import random
from dataclasses import dataclass

from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request

from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, serializers
from api.models import User, Role, Image, SlovenskaMesta, ParkirnaMesta, SlovenskeUlice


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


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    name = serializers.CharField()
    surname = serializers.CharField()
    bio = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True)


class Signup(APIView):

    @extend_schema(request=SignupSerializer)
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


class EditUser(APIView):

    def get(self, request):
        print('===== EDIT USER GET START =====')

        user_id = request.query_params.get('user_id')
        print(f"[DEBUG] user_id param: {user_id}")

        # no user_id in url
        if not user_id:
            return Response(
                {
                    "status": "error",
                    "message": "user_id is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # get data from user through user_id
        try:
            user = User.objects.get(id=user_id)
            print(f"[DEBUG] User found: id={user.id}")
        except User.DoesNotExist:
            print("[ERROR] User not found")
            return Response(
                {
                    "status": "error",
                    "message": "User not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # return data in JSON format
        response_data = {
            "username": user.username,
            "name": user.name,
            "surname": user.surname,
            "bio": user.bio,
            "location": user.location,
            "email": user.email,
            "phone": user.phone,
        }

        print("[SUCCESS] User data returned")
        print("===== EDIT USER GET END =====")

        return Response(
            {
                "status": "success",
                "data": response_data
            },
            status=status.HTTP_200_OK
        )

    def put(self, request):
        print("===== EDIT USER PUT START =====")

        data = request.data
        print(f"[DEBUG] Request data: {data}")

        requester_id = request.query_params.get('user_id')

        # check requester_id
        if not requester_id:
            return Response(
                {"message": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # fetch user
        try:
            user = User.objects.get(id=requester_id)
            print(f"[DEBUG] User found: id={user.id}")
        except User.DoesNotExist:
            return Response(
                {"message": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # fields allowed to be updated
        updatable_fields = [
            "username", "name", "surname",
            "bio", "location", "email", "phone"
        ]

        # update fields
        for field in updatable_fields:
            if field in data:
                old = getattr(user, field)
                new = data.get(field)
                setattr(user, field, new)
                print(f"[DEBUG] Updated {field}: {old} -> {new}")

        # save the changes
        try:
            user.save()
            print("[SUCCESS] User updated")
        except Exception as e:
            print("[ERROR] Update failed")
            print(e)
            return Response(
                {"message": "Failed to update user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        print("===== EDIT USER PUT END =====")

        return Response(
            {"message": "Profile updated successfully"},
            status=status.HTTP_200_OK
        )


class SlovenskaMestaAPI(APIView):

    def get(self, request):
        print("===== SLOVENSKA MESTA GET =====")

        data = request.data
        print(f"[DEBUG] data={data}")

        city_id = data.get("id")

        # --- get one ---
        if city_id:
            try:
                city = SlovenskaMesta.objects.get(id=city_id)
                return Response(
                    {
                        "id": city.id,
                        "ime": city.name
                    },
                    status=status.HTTP_200_OK
                )
            except SlovenskaMesta.DoesNotExist:
                return Response(
                    {"message": "City not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        # --- get all ---
        cities = SlovenskaMesta.objects.all()
        result = [{"id": c.id, "ime": c.name} for c in cities]

        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        print("===== SLOVENSKA MESTA POST =====")

        ime = request.data.get("ime")
        print(f"[DEBUG] ime={ime}")

        if not ime:
            return Response(
                {"message": "ime is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        city = SlovenskaMesta.objects.create(name=ime)

        return Response(
            {
                "message": "City created",
                "id": city.id
            },
            status=status.HTTP_201_CREATED
        )

    def put(self, request):
        print("===== SLOVENSKA MESTA PUT =====")

        data = request.data
        print(f"[DEBUG] data={data}")

        city_id = data.get("id")
        ime = data.get("ime")

        if not city_id or not ime:
            return Response(
                {"message": "id and ime are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            city = SlovenskaMesta.objects.get(id=city_id)
        except SlovenskaMesta.DoesNotExist:
            return Response(
                {"message": "City not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        city.name = ime
        city.save()

        return Response(
            {"message": "City updated"},
            status=status.HTTP_200_OK
        )

    def delete(self, request):
        print("===== SLOVENSKA MESTA DELETE =====")

        city_id = request.data.get("id")
        print(f"[DEBUG] id={city_id}")

        if not city_id:
            return Response(
                {"message": "id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            city = SlovenskaMesta.objects.get(id=city_id)
        except SlovenskaMesta.DoesNotExist:
            return Response(
                {"message": "City not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        city.delete()

        return Response(
            {"message": "City deleted"},
            status=status.HTTP_200_OK
        )


class ParkirnaMestaAPI(APIView):

    def get(self, request):
        print("===== PARKIRNA MESTA GET =====")

        data = request.data
        print(f"[DEBUG] data={data}")

        park_id = data.get("id")

        if park_id:
            try:
                park = ParkirnaMesta.objects.get(id=park_id)
                return Response(
                    {
                        "id": park.id,
                        "ime": park.name,
                        "latitude": park.latitude,
                        "longitude": park.longitude
                    },
                    status=status.HTTP_200_OK
                )
            except ParkirnaMesta.DoesNotExist:
                return Response(
                    {"message": "Parking spot not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        parks = ParkirnaMesta.objects.all()
        result = [
            {
                "id": p.id,
                "ime": p.name,
                "latitude": p.latitude,
                "longitude": p.longitude
            }
            for p in parks
        ]

        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        print("===== PARKIRNA MESTA POST =====")

        name = request.data.get("ime")
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if not all([name, latitude, longitude]):
            return Response(
                {"message": "ime, latitude and longitude are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        park = ParkirnaMesta.objects.create(
            name=name,
            latitude=latitude,
            longitude=longitude
        )

        return Response(
            {
                "message": "Parking spot created",
                "id": park.id
            },
            status=status.HTTP_201_CREATED
        )

    def put(self, request):
        print("===== PARKIRNA MESTA PUT =====")

        park_id = request.data.get("id")
        name = request.data.get("ime")
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if not all([park_id, name, latitude, longitude]):
            return Response(
                {"message": "id, ime, latitude, longitude are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            park = ParkirnaMesta.objects.get(id=park_id)
        except ParkirnaMesta.DoesNotExist:
            return Response(
                {"message": "Parking spot not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if name is not None:
            park.name = name
        if latitude is not None:
            park.latitude = latitude
        if longitude is not None:
            park.longitude = longitude

        park.save()

        return Response(
            {"message": "Parking spot updated"},
            status=status.HTTP_200_OK
        )

    def delete(self, request):
        print("===== PARKIRNA MESTA DELETE =====")

        park_id = request.data.get("id")

        if not park_id:
            return Response(
                {"message": "id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            park = ParkirnaMesta.objects.get(id=park_id)
        except ParkirnaMesta.DoesNotExist:
            return Response(
                {"message": "Parking spot not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        park.delete()

        return Response(
            {"message": "Parking spot deleted"},
            status=status.HTTP_200_OK
        )


class SlovenskeUliceAPI(APIView):

    def get(self, request):
        print("===== SLOVENSKE ULICE GET =====")

        data = request.data
        print(f"[DEBUG] data={data}")

        street_id = data.get("id")

        if street_id:
            try:
                street = SlovenskeUlice.objects.get(id=street_id)
                return Response(
                    {
                        "id": street.id,
                        "ime": street.name
                    },
                    status=status.HTTP_200_OK
                )
            except SlovenskeUlice.DoesNotExist:
                return Response(
                    {"message": "Street not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        streets = SlovenskeUlice.objects.all()
        result = [{"id": s.id, "ime": s.name} for s in streets]

        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        print("===== SLOVENSKE ULICE POST =====")

        ime = request.data.get("ime")
        print(f"[DEBUG] ime={ime}")

        if not ime:
            return Response(
                {"message": "ime is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        street = SlovenskeUlice.objects.create(name=ime)

        return Response(
            {
                "message": "Street created",
                "id": street.id
            },
            status=status.HTTP_201_CREATED
        )

    def put(self, request):
        print("===== SLOVENSKE ULICE PUT =====")

        street_id = request.data.get("id")
        ime = request.data.get("ime")

        if not street_id or not ime:
            return Response(
                {"message": "id and ime are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            street = SlovenskeUlice.objects.get(id=street_id)
        except SlovenskeUlice.DoesNotExist:
            return Response(
                {"message": "Street not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        street.name = ime
        street.save()

        return Response(
            {"message": "Street updated"},
            status=status.HTTP_200_OK
        )

    def delete(self, request):
        print("===== SLOVENSKE ULICE DELETE =====")

        street_id = request.data.get("id")

        if not street_id:
            return Response(
                {"message": "id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            street = SlovenskeUlice.objects.get(id=street_id)
        except SlovenskeUlice.DoesNotExist:
            return Response(
                {"message": "Street not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        street.delete()

        return Response(
            {"message": "Street deleted"},
            status=status.HTTP_200_OK
        )