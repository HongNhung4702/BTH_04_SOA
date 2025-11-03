import jwt
import datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import LoginSerializer


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['userName']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(UserName=username)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.Password != password:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        payload = {
            'user_id': user.IdUser,
            'username': user.UserName,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=4)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        user.Token = token
        user.save(update_fields=['Token'])
        return Response({'token': token})


class VerifyView(APIView):
    def post(self, request):
        token = (request.data or {}).get('token')
        if not token:
            return Response({'error': 'token required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return Response({'valid': True, 'user_id': decoded.get('user_id')})
        except Exception as e:
            return Response({'valid': False, 'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

