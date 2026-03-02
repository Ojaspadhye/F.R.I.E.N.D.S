import secrets
import logging
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from Profiles.models import UserProfile, OTPVerification
from Profiles.exceptions import OTPExpiredException, OTPInvalidException, AccountAlreadyActiveException


logger = logging.getLogger(__name__)


def _send_otp_email(email, otp):
    send_mail(
        subject="Your verification code",
        message=(
            f"Your verification code is: {otp}\n\n"
            f"It expires in {settings.OTP_EXPIRY_MINUTES} minutes.\n"
            "Never share this code with anyone.\n\n"
            "If you didn't request this, you can safely ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


def sign_up_procedure(validated_data):
    with transaction.atomic():
        user = UserProfile.objects.create_user(
            username   = validated_data["username"],
            email      = validated_data["email"],
            password   = validated_data["password"],
            first_name = validated_data.get("first_name") or None,
            last_name  = validated_data.get("last_name") or None,
            is_active  = False,
        )
        otp_record = OTPVerification.objects.create_otp(user)

    _send_otp_email(user.email, otp_record.otp)
    logger.info("Signup OTP dispatched | email=%s user_id=%s", user.email, user.pk)
    return user


def resend_otp(email):
    try:
        user = UserProfile.objects.get(email=email)
    except UserProfile.DoesNotExist:
        logger.warning("resend_otp: unknown email=%s", email)
        return

    if user.is_active:
        logger.info("resend_otp: account already active | email=%s", email)
        return

    otp_record = OTPVerification.objects.create_otp(user)
    _send_otp_email(user.email, otp_record.otp)
    logger.info("OTP resent | email=%s user_id=%s", email, user.pk)


def verify_otp_and_activate(email, otp_input):
    otp_record = OTPVerification.objects.get_valid(email)

    if otp_record is None:
        raise OTPExpiredException()
    
    if not secrets.compare_digest(otp_record.otp, otp_input):
        raise OTPInvalidException()

    with transaction.atomic():
        user = otp_record.user

        if user.is_active:
            raise AccountAlreadyActiveException()

        user.is_active = True
        user.save(update_fields=["is_active", "updated_at"])
        otp_record.delete()

    logger.info("Account activated | email=%s user_id=%s", email, user.pk)
    return user


def login_procedure(validated_data):
    user = validated_data.user

    refresh = RefreshToken.for_user(user=user)
    access = RefreshToken.access_token(refresh)

    return {
        "Access Token": str(access),
        "Refresh Token": str(refresh)
    }
