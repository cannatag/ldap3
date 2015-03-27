ntlm_support = True
if str == bytes:  # python 2
    try:
        from ntlm.ntlm import create_NTLM_NEGOTIATE_MESSAGE, parse_NTLM_CHALLENGE_MESSAGE, create_NTLM_AUTHENTICATE_MESSAGE
    except ImportError:
        ntlm_support = False
else:  # python 3
    try:
        from ntlm3.ntlm import create_NTLM_NEGOTIATE_MESSAGE, parse_NTLM_CHALLENGE_MESSAGE, create_NTLM_AUTHENTICATE_MESSAGE
    except ImportError:
        ntlm_support = False

from base64 import b64decode


def ntlm_generate_negotiate(user):
    message_type_1 = b64decode(create_NTLM_NEGOTIATE_MESSAGE(user))

    return message_type_1


def decode_ntlm_challenge(message):
    message_type_2 = parse_NTLM_CHALLENGE_MESSAGE(message)

    return message_type_2


def ntlm_generate_response(user, password, flags, challenge):
    domain, username = user.split('\\', 1)
    print('CHALLENGE', challenge)
    print('USER', username)
    print('DOMAIN', domain)
    print('PASSWORD', password)
    print('FLAGS', flags)
    message_type_3 = b64decode(create_NTLM_AUTHENTICATE_MESSAGE(challenge, username, domain, password, flags))
    return message_type_3
