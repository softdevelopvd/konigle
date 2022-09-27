import datetime
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from .models import VisitorEmail, Seller
from .serializers import (
    VisitorEmailSerializer,
    VisitorEmailCreateSerializer,
    SellerCreateSerializer,
    AuthSerializer,
)
from .constants.visitor_emails import VisitorEmailStatusType

# Create your views here.
def unity_home(request):
    emails = VisitorEmail.objects.all()
    current_date = datetime.date.today().strftime("%B %Y")
    amount_new_this_month = emails.filter(
        created_at__month=datetime.date.today().month
    ).count()
    amount_unsubscribed = emails.filter(
        status=VisitorEmailStatusType.UNSUBSCRIBED
    ).count()

    context = {
        "emails": emails,
        "current_date": current_date,
        "amount_new_this_month": amount_new_this_month,
        "amount_unsubscribed": amount_unsubscribed,
    }
    return render(request, "emails.html", context=context)


@api_view(["POST"])
def login_view(request):
    serializer = AuthSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.login(request.data)
        return Response(result, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logout_view(request):
    try:
        request.user.auth_token.delete()
        data = {"message": "Successfully logged out."}
        return Response(data, status=status.HTTP_200_OK)
    except (AttributeError, ObjectDoesNotExist):
        return Response({"message": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class SellerViewSet(viewsets.ModelViewSet):
    serializer_class = SellerCreateSerializer
    permission_classes = []
    pagination_class = None

    def get_queryset(self):
        queryset = Seller.objects.filter(user__is_active=True)
        return queryset

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.create()
            data = {"message": "Registered successfully!"}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VisitorEmailViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorEmailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = VisitorEmail.objects.filter(
            seller__user=self.request.user, seller__user__is_active=True
        )
        return queryset

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs.get("id"),
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response(
                {"email": "Email not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, id=None):
        try:
            serializer = self.get_serializer(self.get_object())
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(
                {"email": "Email not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        serializer = VisitorEmailCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.create()
            return Response(
                {"message": "Create successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
