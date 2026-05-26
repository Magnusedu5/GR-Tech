from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Inquiry
from .serializers import InquirySerializer, InquiryAdminSerializer
from .emails import send_notification


# ── Public: contact form ──────────────────────────────────────────────────────

class ContactView(APIView):
    """POST /api/contact/ — public, no auth required."""
    authentication_classes = []
    permission_classes     = [AllowAny]

    def post(self, request):
        serializer = InquirySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        inquiry = serializer.save(ip_address=self._get_ip(request))

        try:
            send_notification(inquiry)
        except Exception:
            pass

        return Response(
            {'message': 'Inquiry received. We will be in touch within 24 hours.'},
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def _get_ip(request):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


# ── Admin: login ──────────────────────────────────────────────────────────────

class LoginView(APIView):
    """POST /api/auth/login/ — returns auth token for valid credentials."""
    authentication_classes = []
    permission_classes     = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return Response({'error': 'Username and password required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_staff:
            return Response({'error': 'Admin access only.'}, status=status.HTTP_403_FORBIDDEN)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'first_name': user.first_name,
        })


# ── Admin: inquiries ──────────────────────────────────────────────────────────

class InquiryListView(APIView):
    """GET /api/inquiries/ — list all inquiries, newest first."""
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    def get(self, request):
        qs = Inquiry.objects.all()

        # Optional ?status= filter
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        serializer = InquiryAdminSerializer(qs, many=True)
        return Response({
            'count': qs.count(),
            'results': serializer.data,
            'summary': {
                'new':        Inquiry.objects.filter(status='new').count(),
                'in_review':  Inquiry.objects.filter(status='in_review').count(),
                'contacted':  Inquiry.objects.filter(status='contacted').count(),
                'closed':     Inquiry.objects.filter(status='closed').count(),
                'total':      Inquiry.objects.count(),
            }
        })


class InquiryDetailView(APIView):
    """GET /api/inquiries/{id}/ — single inquiry. PATCH to update status."""
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    def _get_object(self, pk):
        try:
            return Inquiry.objects.get(pk=pk)
        except Inquiry.DoesNotExist:
            return None

    def get(self, request, pk):
        inquiry = self._get_object(pk)
        if not inquiry:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(InquiryAdminSerializer(inquiry).data)

    def patch(self, request, pk):
        inquiry = self._get_object(pk)
        if not inquiry:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InquiryAdminSerializer(inquiry, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)
