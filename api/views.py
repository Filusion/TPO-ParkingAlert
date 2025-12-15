from django.shortcuts import render
from rest_framework.request import Request

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.models import User


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
