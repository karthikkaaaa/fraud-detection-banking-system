
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .forms import RegisterForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import Transaction, CustomerProfile
from .serializers import TransactionSerializer
from .ml_model import predict_risk
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Transaction, Complaint

from .models import Complaint

def home(request):
    return redirect("login")



def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
                email=form.cleaned_data["email"]
            )

            profile = form.save(commit=False)
            profile.user = user
            profile.save()

            messages.success(request, "Account Created Successfully")
            return redirect("login")

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("user_dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")




@login_required
def make_transaction(request):
    phone = request.session.get("pay_phone")

    if not phone:
        return redirect("pay_phone")
    
    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        location = request.POST.get("location")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(confirm_password):
            messages.error(request, "Incorrect transaction password")
            return redirect("make_transaction")

        profile = CustomerProfile.objects.get(user=request.user)

        risk = 0
        if amount > 20000:
            risk += 0.6
        if location != profile.home_location:
            risk += 0.4

        if risk >= 0.7:
            status_result = "Flagged"
            send_fraud_email = True
        elif amount > profile.balance:
            messages.error(request, "Insufficient Balance")
            return redirect("make_transaction")
        else:
            status_result = "Approved"
            send_fraud_email = False
            profile.balance -= amount
            profile.save()

        transaction = Transaction.objects.create(
            user=request.user,
            amount=amount,
            location=location,
            risk_score=risk,
            status=status_result
        )

        if send_fraud_email:
            confirm_url = request.build_absolute_uri(
                reverse('confirm_transaction', args=[transaction.id])
            )

            fraud_url = request.build_absolute_uri(
                reverse('report_fraud', args=[transaction.id])
            )

            send_mail(
                subject="Fraud Alert - Transaction Flagged",
                message=f"""
⚠️ Suspicious Transaction Detected

User: {request.user.username}
Amount: ₹{amount}
Risk Score: {risk}
Location: {location}
Transaction ID: {transaction.id}

YES → {confirm_url}
NO → {fraud_url}
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=["karthikakunnummal123@gmail.com"],
                fail_silently=False,
            )

        return render(request, "transaction_result.html", {
            "status": status_result,
            "risk": risk
        })

    return render(request, "make_transaction.html")


@login_required
def report_fraud(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id, user=request.user)
    transaction.status = "Fraud Reported"
    transaction.save()

    return render(request, "fraud_reported.html")

@login_required
def confirm_transaction(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id, user=request.user)
    transaction.status = "Pending Bank Approval"
    transaction.save()

    return render(request, "confirmation_sent.html")


def is_bank(user):
    return user.is_staff


def bank_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect("bank_dashboard")

    return render(request, "bank_login.html")


@user_passes_test(is_bank)
def bank_dashboard(request):

    search_query = request.GET.get("search")

    transactions = Transaction.objects.all().order_by('-created_at')
    complaints = Complaint.objects.filter(status="New").order_by('-created_at')

    if search_query:
        transactions = transactions.filter(user__username__icontains=search_query)

    return render(request, "bank_dashboard.html", {
        "transactions": transactions,
        "complaints": complaints
    })

@user_passes_test(is_bank)
def update_status(request, transaction_id, new_status):
    transaction = Transaction.objects.get(id=transaction_id)
    profile = CustomerProfile.objects.get(user=transaction.user)

    # if new_status == "Approved":
    #     if profile.balance >= transaction.amount:
    #         profile.balance -= transaction.amount
    #         profile.save()
    #         transaction.status = "Approved"

    #         send_mail(
    #             "Transaction Approved",
    #             f"Dear {transaction.user.username}, you can now transact safely.",
    #             settings.EMAIL_HOST_USER,
    #             [transaction.user.email],
    #             fail_silently=True,
    #         )
    #     else:
    #         transaction.status = "Declined"
    # else:
    #     transaction.status = "Declined"

    # transaction.save()
    # return redirect("bank_dashboard")
    if new_status == "Approved":
        profile.balance -= transaction.amount
        profile.save()
        transaction.status = "Approved"

        send_mail(
            subject="Transaction Approved",
            message=f"Dear {transaction.user.username}, your transaction of ₹{transaction.amount} has been approved by the bank.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["karthikakunnummal123@gmail.com"],
            fail_silently=False,
    )

    elif new_status == "Declined":
        transaction.status = "Declined"

    transaction.save()
    return redirect("bank_dashboard")


@user_passes_test(is_bank)
def customer_detail(request, user_id):
    user_obj = User.objects.get(id=user_id)
    profile = CustomerProfile.objects.get(user=user_obj)
    transactions = Transaction.objects.filter(user=user_obj)

    return render(request, "customer_detail.html", {
        "customer": user_obj,
        "profile": profile,
        "transactions": transactions,
        "total_transactions": transactions.count()
    })

@user_passes_test(is_bank)
def customer_dashboard(request):
    customers = CustomerProfile.objects.all()
    return render(request, "customer_dashboard.html", {"customers": customers})


class TransactionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = float(request.data.get("amount"))
        location = request.data.get("location")

        profile = CustomerProfile.objects.get(user=request.user)

        risk = 0
        if amount > 5000:
            risk += 0.4
        if location != profile.home_location:
            risk += 0.4

        status_result = "Declined" if risk >= 0.7 else "Approved"

        transaction = Transaction.objects.create(
            user=request.user,
            amount=amount,
            location=location,
            risk_score=risk,
            status=status_result
        )

        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HighRiskTransactions(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(risk_score__gte=0.7)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
class UserTransactionHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
@user_passes_test(is_bank)
def staff_list(request):
    staff = User.objects.filter(is_staff=True)
    return render(request, "staff_list.html", {"staff": staff})
@user_passes_test(is_bank)
def add_staff(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.save()

        return redirect("staff_list")

    return render(request, "add_staff.html")
@user_passes_test(is_bank)
def bank_history(request):
    transactions = Transaction.objects.all().order_by('-created_at')
    return render(request, "bank_history.html", {"transactions": transactions})



@login_required
def user_dashboard(request):
    profile = CustomerProfile.objects.get(user=request.user)
    return render(request, "dashboard.html", {"profile": profile})



@login_required
def check_balance(request):
    profile = CustomerProfile.objects.get(user=request.user)

    if request.method == "POST":
        password = request.POST.get("password")

        if request.user.check_password(password):
            return render(request, "balance.html", {"balance": profile.balance})
        else:
            messages.error(request, "Incorrect Password")

    return render(request, "check_balance.html")


@login_required
def user_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "history.html", {"transactions": transactions})


@login_required
def user_profile(request):
    profile = CustomerProfile.objects.get(user=request.user)
    return render(request, "profile.html", {"profile": profile})


@login_required
def pay_phone(request):
    if request.method == "POST":
        phone = request.POST.get("phone")

        if len(phone) != 10 or not phone.isdigit():
            messages.error(request, "Enter valid 10 digit phone number")
            return redirect("pay_phone")

        request.session["pay_phone"] = phone

        return redirect("make_transaction")

    return render(request, "pay_phone.html")





@login_required
def help_request(request):

    if request.method == "POST":
        phone = request.POST.get("phone")
        problem = request.POST.get("problem")
        confirm_password = request.POST.get("confirm_password")
        is_you = request.POST.get("is_you")

        if not request.user.check_password(confirm_password):
            messages.error(request, "Incorrect Password")
            return redirect("help_request")

        Complaint.objects.create(
            user=request.user,
            phone=phone,
            is_you=is_you,
            problem=problem
        )

        send_mail(
            subject="Customer Complaint - TrustShield Bank",
            message=f"""
New Customer Complaint

Customer Username: {request.user.username}
Phone: {phone}
Is Transaction Yours?: {is_you}

Problem:
{problem}
            """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.BANK_EMAIL],
            fail_silently=False,
        )

        return render(request, "help_submitted.html")

    return render(request, "help_form.html")


@user_passes_test(is_bank)
def bank_complaints(request):
    complaints = Complaint.objects.all().order_by("-created_at")
    return render(request, "bank_complaints.html", {"complaints": complaints})



@user_passes_test(is_bank)
def complaint_detail(request, complaint_id):
    complaint = Complaint.objects.get(id=complaint_id)
    return render(request, "complaint_detail.html", {"complaint": complaint})