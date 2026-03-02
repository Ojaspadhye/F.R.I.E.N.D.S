from rest_framework.exceptions import APIException
from rest_framework import status


class OTPExpiredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "OTP Expired or Invalid"
    default_code = "OTP-Expired"


class OTPInvalidException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid or expired verification code."
    default_code = "OTP-Invalid"


class AccountAlreadyActiveException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "This account verified."
    default_code = "account-active"

