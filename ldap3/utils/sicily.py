if str == bytes:
    try:
        from ntlm3 import create_NTLM_NEGOTIATE_MESSAGE, parse_NTLM_CHALLENGE_MESSAGE, create_NTLM_AUTHENTICATE_MESSAGE
    except ImportError:
        pass
else:
    try:
        from ntlm import create_NTLM_NEGOTIATE_MESSAGE, parse_NTLM_CHALLENGE_MESSAGE, create_NTLM_AUTHENTICATE_MESSAGE
    except ImportError:
        pass


def ntlm_generate_negotiate(user):
    message_type_1 = create_NTLM_NEGOTIATE_MESSAGE(user)

    return message_type_1


def ntlm_generate_response(user, password, flags, challenge):
    domain, username = user.split('\\', 1)

    message_type_3 = create_NTLM_AUTHENTICATE_MESSAGE(challenge, user, domain, password, flags)
    return message_type_3
