from django.http import QueryDict
from knox.models import AuthToken
from ..models import User


def get_token(headers, *args, **kwargs):
    '''
    Function to retrieve valid token from request headers
    '''

    if "Authorization" not in headers:
        err_msg = {
            "Error": 'Token should be provided in header as follows: "Authorization: Token <digest>"'
        }
        return None, err_msg

    if not headers["Authorization"].startswith("Token "):
        err_msg = {
            "Error": 'Token should be provided in header as follows: "Authorization: Token <digest>"'
        }
        return None, err_msg

    token = headers["Authorization"].split(" ")[1]
    knox_object = AuthToken.objects.filter(
        token_key__startswith=token[:8]).first()

    if knox_object is None:
        err_msg = {
            "Error": "Invalid token"
        }
        return None, err_msg

    return knox_object, None


def get_user_from_token(headers, *args, **kwargs):
    token, err = get_token(headers, *args, **kwargs)
    if (err is not None):
        return None, err
    return token.user, None


def validate_contact(data, *args, **kwargs):
    '''
    Function to validate contact from data dict
    '''
    if (data is None):
        err_msg = {
            "Error": "contacts field is required"
        }
        return err_msg

    if (len(data.keys()) > 1):
        err_msg = {
            "Error": "only contacts field is allowed"
        }
        return err_msg

    if (list(data.keys())[0] != "contacts"):
        err_msg = {
            "Error": "only contacts field is allowed"
        }
        return err_msg

    try:
        data = data.getlist("contacts") if (
            isinstance(data, QueryDict)) else data["contacts"]

        for contact in data:
            User.objects.all().get(id=contact)
        return None
    except:
        err_msg = {
            "Error": "some users do not exist"
        }
        return err_msg


def request_exists(sent_from, received_from):
    try:
        User.objects.filter(sent_from=sent_from, received_from=received_from)
        return True
    except:
        return False
