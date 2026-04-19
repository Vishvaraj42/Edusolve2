import random
from django.core.cache import cache   # <--- ADD THIS LINE!
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView    
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Student
from .serializers import (
    StudentRegistrationSerializer,
    StudentProfileSerializer,
    StudentSerializer,
    ChangePasswordSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = Student.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = StudentRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Feature 1: Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Store OTP in cache for 5 minutes (300 seconds), tied to the user's email
        cache.set(f"otp_{user.email}", otp, timeout=300)
        
        # Send Email OTP
        try:
            send_mail(
                subject="EduSolve - Your Verification Code",
                message=f"Hi {user.first_name},\n\nYour verification code is: {otp}\nThis code will expire in 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Email failed to send: {e}")

        # "Send" Mobile OTP (Mocked for now until you connect Twilio)
        print(f"--- MOCK SMS --- Sent OTP {otp} to {user.phone_number}")
        
        return Response({
            'message': 'Registration successful! Please verify your email.',
            'email': user.email, # Send email back to frontend so it knows what to verify
            'requires_otp': True
        }, status=status.HTTP_201_CREATED)
    
class VerifyOTPView(APIView):
    """New Endpoint to verify OTP and activate the account"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        provided_otp = request.data.get('otp')

        if not email or not provided_otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the real OTP from the cache
        cached_otp = cache.get(f"otp_{email}")

        if not cached_otp or cached_otp != str(provided_otp):
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Student.objects.get(email=email)
            user.is_active = True # Activate the user!
            user.save()
            
            # Clear the OTP from cache
            cache.delete(f"otp_{email}")

            # Feature 2: Send the Welcome Email now that they are verified!
            try:
                send_mail(
                    subject="Welcome to EduSolve! ✨",
                    message=f"Hi {user.first_name},\n\nYour account is verified! Welcome to your premium AI learning journey.\n\n- The EduSolve Team",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass # Fail silently if welcome email drops

            # Generate JWT tokens for instant login
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': StudentSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'message': 'Verification successful! Welcome to EduSolve.'
            }, status=status.HTTP_200_OK)

        except Student.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': StudentSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful!'
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful!'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token or token already blacklisted'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get('old_password')):
                return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'message': 'Password changed successfully!'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentListView(generics.ListAPIView):
    queryset = Student.objects.all().order_by('-points')
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['grade']
    search_fields = ['username', 'first_name', 'last_name']
    ordering_fields = ['points', 'created_at']