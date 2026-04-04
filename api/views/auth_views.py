# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import AllowAny
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth import authenticate
# from ..serializers import RegisterSerializer, UserSerializer

# # from django.views.decorators.csrf import csrf_exempt



# class RegisterView(APIView):
#     permission_classes = [AllowAny]


#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 "message": "Account created successfully.",
#                 "user": UserSerializer(user).data,
#                 "tokens": {
#                     "refresh": str(refresh),
#                     "access":  str(refresh.access_token),
#                 }
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class LoginView(APIView):
#     permission_classes = [AllowAny]

    
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         if not username or not password:
#             return Response(
#                 {"error": "Both username and password are required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         user = authenticate(username=username, password=password)
#         if not user:
#             return Response(
#                 {"error": "Invalid credentials."},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )
#         if not user.is_active:
#             return Response(
#                 {"error": "This account is deactivated."},
#                 status=status.HTTP_403_FORBIDDEN
#             )

#         refresh = RefreshToken.for_user(user)
#         return Response({
#             "user": UserSerializer(user).data,
#             "tokens": {
#                 "refresh": str(refresh),
#                 "access":  str(refresh.access_token),
#             }
#         })


# class MeView(APIView):
#     # @csrf_exempt
#     def get(self, request):
#         return Response(UserSerializer(request.user).data)


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from ..serializers import RegisterSerializer, UserSerializer


@method_decorator(csrf_exempt, name='dispatch')   # ← ADD THIS
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Account created successfully.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access":  str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')   # ← ADD THIS
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "Both username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not user.is_active:
            return Response(
                {"error": "This account is deactivated."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access":  str(refresh.access_token),
            }
        })


@method_decorator(csrf_exempt, name='dispatch')   # ← ADD THIS
class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)