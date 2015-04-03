from socket import gethostname

ntlm_support = True
if str == bytes:  # python 2
    try:
        from ntlm.ntlm import create_NTLM_NEGOTIATE_MESSAGE, parse_NTLM_CHALLENGE_MESSAGE, create_NTLM_AUTHENTICATE_MESSAGE
    except ImportError:
        ntlm_support = False
else:  # python 3
    try:
        from ntlm3.ntlm import create_NTLM_NEGOTIATE_MESSAGE, parse_NTLM_CHALLENGE_MESSAGE, create_NTLM_AUTHENTICATE_MESSAGE, \
            NTLM_NegotiateUnicode, NTLM_NegotiateOEM, NTLM_RequestTarget, NTLM_NegotiateNTLM, NTLM_NegotiateAlwaysSign, \
            NTLM_NegotiateExtendedSecurity, NTLM_NegotiateVersion, NTLM_Negotiate128, NTLM_Negotiate56, calc_resp, \
            create_NT_hashed_password_v1, ntlm2sr_calc_resp, create_LM_hashed_password_v1, NTLM_TYPE2_FLAGS

    except ImportError:
        ntlm_support = False

from base64 import b64decode
import struct
from platform import version, system
from random import getrandbits


def windows_version():
    if system().lower() == 'windows':
        try:
            major_release, minor_release, build = version().split('.')
            major_release = int(major_release)
            minor_release = int(minor_release)
            build = int(build)
        except Exception:
            major_release = 5
            minor_release = 1
            build = 2600
    else:
        major_release = 5
        minor_release = 1
        build = 2600

    print("VERSION:", major_release, minor_release, build)
    return major_release, minor_release, build


def ntlm_generate_negotiate(user):
    flags = (NTLM_NegotiateUnicode |
                NTLM_NegotiateOEM |
                NTLM_RequestTarget |
                NTLM_NegotiateNTLM |
                NTLM_NegotiateAlwaysSign |
                NTLM_NegotiateExtendedSecurity |
                NTLM_NegotiateVersion |
                NTLM_Negotiate128 |
                NTLM_Negotiate56)


    message = b'NTLMSSP\0'  # signature
    message += struct.pack('<I', 1)  # message type 1
    message += struct.pack('<I', flags)  # flags
    message += struct.pack('<I', 0)  # NULL workstation
    message += struct.pack('<I', 0)  # NULL workstation
    message += struct.pack('<I', 0)  # NULL domain
    message += struct.pack('<I', 0)  # NULL domain
    major_release, minor_release, build = windows_version()
    message += struct.pack('<B', major_release)  # major version
    message += struct.pack('<B', minor_release)  # minor version
    message += struct.pack('<H', build)  # build
    message += struct.pack('<B', 0)  # reserved
    message += struct.pack('<B', 0)  # reserved
    message += struct.pack('<B', 0)  # reserved
    message += struct.pack('<B', 15)  # revision

    return message

    # message_type_1 = b64decode(create_NTLM_NEGOTIATE_MESSAGE(user, ))
    # return message_type_1


def decode_ntlm_challenge(message):
    message_type_2 = parse_NTLM_CHALLENGE_MESSAGE(message)

    return message_type_2


def ntlm_generate_response(user, password, flags, challenge):
    domain, username = user.split('\\', 1)

    is_unicode = struct.unpack('<I', flags)[0] & NTLM_NegotiateUnicode
    is_negotiate_extended_security = struct.unpack('<I', flags)[0] & NTLM_NegotiateExtendedSecurity
    if is_unicode:
        print('UNICODE')
        workstation = gethostname().upper().encode('utf-16-le')
        domain = domain.upper().encode('utf-16-le')
        username = username.upper().encode('utf-16-le')
        encrypted_random_session_key = ''.encode('utf-16-le')
    else:
        workstation = gethostname().upper().encode('ascii')
        domain = domain.upper().encode('ascii')
        username = username.encode('ascii')
        encrypted_random_session_key = b''

    if is_negotiate_extended_security:
        print('EXTENDED SECURITY')
        pwhash = create_NT_hashed_password_v1(password, username, domain)
        client_challenge = b''
        for i in range(8):
            client_challenge += bytes((getrandbits(8),)) if str != bytes else chr(getrandbits(0))  # python 2 and 3
        nt_challenge_response, lm_challenge_response = ntlm2sr_calc_resp(pwhash, challenge, client_challenge)
    else:
        nt_challenge_response = calc_resp(create_NT_hashed_password_v1(password), challenge)
        lm_challenge_response = calc_resp(create_LM_hashed_password_v1(password), challenge)

    payload_start = 72

    domain_len = struct.pack('<H', len(domain))
    domain_offset = struct.pack('<I', payload_start)
    payload_start += len(domain)

    username_len = struct.pack('<H', len(username))
    username_offset = struct.pack('<I', payload_start)
    payload_start += len(username)

    workstation_len = struct.pack('<H', len(workstation))
    workstation_offset = struct.pack('<I', payload_start)
    payload_start += len(workstation)

    lm_challenge_response_len = struct.pack('<H', len(lm_challenge_response))
    lm_challenge_response_offset = struct.pack('<I', payload_start)
    payload_start += len(lm_challenge_response)

    nt_challenge_response_len = struct.pack('<H', len(nt_challenge_response))
    nt_challenge_response_offset = struct.pack('<I', payload_start)
    payload_start += len(nt_challenge_response)

    encrypted_random_session_key_len = struct.pack('<H', len(encrypted_random_session_key))
    encrypted_random_session_key_offset = struct.pack('<I', payload_start)
    payload_start += len(encrypted_random_session_key)

    MIC = struct.pack('<IIII', 0, 0, 0, 0)  # noqa

    message = b'NTLMSSP\0'  # signature
    message += struct.pack('<I', 3)  # message type 3
    message += lm_challenge_response_len + lm_challenge_response_len + lm_challenge_response_offset
    message += nt_challenge_response_len + nt_challenge_response_len + nt_challenge_response_offset
    message += domain_len + domain_len + domain_offset
    message += username_len + username_len + username_offset
    message += workstation_len + workstation_len + workstation_offset
    message += encrypted_random_session_key_len + encrypted_random_session_key_len + encrypted_random_session_key_offset
    message += struct.pack('<I', NTLM_TYPE2_FLAGS)
    major_release, minor_release, build = windows_version()
    message += struct.pack('<B', major_release)  # major version
    message += struct.pack('<B', minor_release)  # minor version
    message += struct.pack('<H', build)  # build
    message += struct.pack('<B', 0)  # reserved
    message += struct.pack('<B', 0)  # reserved
    message += struct.pack('<B', 0)  # reserved
    message += struct.pack('<B', 15)  # revision
    message += domain
    message += username
    message += workstation
    message += lm_challenge_response
    message += nt_challenge_response
    message += encrypted_random_session_key

    return message

    # message_type_3 = b64decode(create_NTLM_AUTHENTICATE_MESSAGE(challenge, username, domain, password, flags))
    # return message_type_3
