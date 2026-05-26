from django.urls import path
from .views import ContactView, LoginView, InquiryListView, InquiryDetailView

urlpatterns = [
    # Public
    path('contact/',              ContactView.as_view(),      name='contact'),
    # Admin auth
    path('auth/login/',           LoginView.as_view(),         name='login'),
    # Admin inquiries
    path('inquiries/',            InquiryListView.as_view(),   name='inquiries'),
    path('inquiries/<int:pk>/',   InquiryDetailView.as_view(), name='inquiry-detail'),
]
