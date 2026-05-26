from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import InquirySerializer
from .emails import send_notification


class ContactView(APIView):
    """
    POST /api/contact/
    Public endpoint — no authentication required.
    Accepts a contact form submission, saves it, and fires an email notification.
    """
    authentication_classes = []   # disable session/CSRF enforcement
    permission_classes     = [AllowAny]

    def post(self, request):
        serializer = InquirySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        inquiry = serializer.save(
            ip_address=self._get_ip(request)
        )

        try:
            send_notification(inquiry)
        except Exception:
            # Don't fail the request if email delivery fails
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
