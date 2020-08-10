def send_password_reset_email(user):
    token = user.get_reset_password_token() # pylint: disable=unused-variable
