from django.conf import settings
from kavenegar import KavenegarAPI, APIException, HTTPException


def send_sms(phone, message):
    api = KavenegarAPI(settings.KAVENEGAR_API_KEY)

    params = {
        "sender": settings.KAVENEGAR_SENDER,
        "receptor": phone,
        "message": message,
    }

    try:
        response = api.sms_send(params)
        return response
    except (APIException, HTTPException) as e:
        raise e
