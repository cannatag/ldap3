"""
"""

# Created on 2015.04.02
#
# Author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

# NTLMv2 authentication as per [MS-NLMP] (https://msdn.microsoft.com/en-us/library/cc236621.aspx)

from struct import pack, unpack
from platform import system, version
import binascii

NTLM_SIGNATURE = b'NTLMSSP\x00'
NTLM_MESSAGE_TYPE_NTLM_NEGOTIATE = 1
NTLM_MESSAGE_TYPE_NTLM_CHALLENGE = 2
NTLM_MESSAGE_TYPE_NTLM_AUTHENTICATE = 3

FLAG_NEGOTIATE_56 = 31  # W
FLAG_NEGOTIATE_KEY_EXCH = 30  # V
FLAG_NEGOTIATE_128 = 29  # U
FLAG_NEGOTIATE_VERSION = 25  # T
FLAG_NEGOTIATE_TARGET_INFO = 23  # S
FLAG_REQUEST_NOT_NT_SESSION_KEY = 22  # R
FLAG_NEGOTIATE_IDENTIFY = 20  # Q
FLAG_NEGOTIATE_EXTENDED_SESSIONSECURITY = 19  # P
FLAG_TARGET_TYPE_SERVER = 17  # O
FLAG_TARGET_TYPE_DOMAIN = 16  # N
FLAG_NEGOTIATE_ALWAYS_SIGN = 15  # M
FLAG_NEGOTIATE_OEM_WORKSTATION_SUPPLIED = 13  # L
FLAG_NEGOTIATE_OEM_DOMAIN_SUPPLIED = 12  # K
FLAG_NEGOTIATE_ANONYMOUS = 11  # J
FLAG_NEGOTIATE_NTLM = 9  # H
FLAG_NEGOTIATE_LM_KEY = 7  # G
FLAG_NEGOTIATE_DATAGRAM = 6  # F
FLAG_NEGOTIATE_SEAL = 5  # E
FLAG_NEGOTIATE_SIGN = 4  # D
FLAG_REQUEST_TARGET = 2  # C
FLAG_NEGOTIATE_OEM = 1  # B
FLAG_NEGOTIATE_UNICODE = 0

FLAGS = [FLAG_NEGOTIATE_56,
         FLAG_NEGOTIATE_KEY_EXCH,
         FLAG_NEGOTIATE_128,
         FLAG_NEGOTIATE_VERSION,
         FLAG_NEGOTIATE_TARGET_INFO,
         FLAG_REQUEST_NOT_NT_SESSION_KEY,
         FLAG_NEGOTIATE_IDENTIFY,
         FLAG_NEGOTIATE_EXTENDED_SESSIONSECURITY,
         FLAG_TARGET_TYPE_SERVER,
         FLAG_TARGET_TYPE_DOMAIN,
         FLAG_NEGOTIATE_ALWAYS_SIGN,
         FLAG_NEGOTIATE_OEM_WORKSTATION_SUPPLIED,
         FLAG_NEGOTIATE_OEM_DOMAIN_SUPPLIED,
         FLAG_NEGOTIATE_ANONYMOUS,
         FLAG_NEGOTIATE_NTLM,
         FLAG_NEGOTIATE_LM_KEY,
         FLAG_NEGOTIATE_DATAGRAM,
         FLAG_NEGOTIATE_SEAL,
         FLAG_NEGOTIATE_SIGN,
         FLAG_REQUEST_TARGET,
         FLAG_NEGOTIATE_OEM,
         FLAG_NEGOTIATE_UNICODE]


def pack_windows_version():
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

    return pack('<B', major_release) + pack('<B', minor_release) + pack('<H', build)


def unpack_version(version_message):
    print("version", binascii.hexlify(version_message))
    if len(version_message) != 8:
        raise ValueError('version field must be 8 bytes long')

    unpack('<B', version_message[0])[0]
    unpack('<B', version_message[1])[0]
    unpack('<H', version_message[2:4])[0]
    unpack('<B', version_message[7])[0]
    return unpack('<B', version_message[0])[0], unpack('<B', version_message[1])[0], unpack('<H', version_message[2:4])[0], unpack('<B', version_message[7])[0]


class NtlmClient(object):
    def __init__(self, domain, username, password):
        self.client_config_flags = 0
        self.exported_session_key = None
        self.negotiated_flags = None
        self.user = username
        self.user_domain = domain
        self.no_lm_response_ntlm_v1 = None
        self.client_blocked = False
        self.client_block_exceptions = []
        self.client_require_128_bit_encryption = None
        self.max_life_time = None
        self.client_signing_key = None
        self.client_sealing_key = None
        self.sequence_number = None
        self.server_sealing_key = None
        self.server_signing_key = None
        self.integrity = False
        self.replay_detect = False
        self.sequence_detect = False
        self.confidentiality = False
        self.datagram = False
        self.identity = False
        self.client_supplied_target_name = None
        self.client_channel_binding_unhashed = None
        self.unverified_target_name = None
        self._password = password
        self.from_server_challenge = None
        self.from_server_target_name = None
        self.from_server_target_info = None
        self.from_server_version = None

    def get_flag(self, flag):
        if flag in FLAGS:
            return True if self.client_config_flags & (1 << flag) else False

        raise ValueError('invalid flag')

    def set_flag(self, flags):
        if type(flags) == int:
            flags = [flags]
        for flag in flags:
            if flag in FLAGS:
                self.client_config_flags |= (1 << flag)
            else:
                raise ValueError('invalid flag')

    def reset_flags(self):
        self.client_config_flags = 0

    def unset_flag(self, flags):
        if type(flags) == int:
            flags = [flags]
        for flag in flags:
            if flag in FLAGS:
                self.client_config_flags &= ~(1 << flag)
            else:
                raise ValueError('invalid flag')

    def create_negotiate_message(self):
        self.reset_flags()
        self.set_flag([FLAG_REQUEST_TARGET,
                       FLAG_NEGOTIATE_NTLM,
                       FLAG_NEGOTIATE_ALWAYS_SIGN,
                       FLAG_NEGOTIATE_UNICODE,
                       FLAG_NEGOTIATE_EXTENDED_SESSIONSECURITY])

        message = NTLM_SIGNATURE  # 8 bytes
        message += pack('<I', NTLM_MESSAGE_TYPE_NTLM_NEGOTIATE)  # 4 bytes
        message += pack('<I', self.client_config_flags)  # 4 bytes
        message += self.pack_field('', 40)  # domain name field  # 8 bytes
        message += self.pack_field('', 40)  # workstation field  # 8 bytes
        if self.get_flag(FLAG_NEGOTIATE_VERSION):  # version 8 bytes - used for debug in ntlm
            message += pack_windows_version()
        else:
            message += pack('<I', 0)  # no version

        message += pack('<B', 15)  # revision

        return message

    def parse_challenge_message(self, message):
        print(len(message))
        if len(message) < 56:  # minimum size of challenge message
            return False

        if message[0:8] != NTLM_SIGNATURE:  # NTLM signature - 8 bytes
            print('SIGNATURE ERROR')
            return False

        if int(unpack('<I', message[8:12])[0]) != NTLM_MESSAGE_TYPE_NTLM_CHALLENGE:  # type of message - 4 bytes
            print('MESSAGE TYPE ERROR', message[8:12])
            return False

        target_name_len, _, target_name_offset = self.unpack_field(message[12:20])  # targetNameFields - 8 bytes
        self.negotiated_flags = unpack('<I', message[20:24])[0]  # negotiated flags - 4 bytes
        self.from_server_challenge = message[24:32]  # server challenge - 8 bytes
        target_info_len, _, target_info_offset = self.unpack_field(message[40:48])  # targetInfoFields - 8 bytes
        self.from_server_version = unpack_version(message[40:48])
        if target_name_len:
            self.from_server_target_name = message[target_name_offset: target_name_offset + target_name_len]
        if target_info_len:
            self.from_server_target_info = message[target_info_offset: target_info_offset + target_info_len]

        print(self.negotiated_flags)
        print(self.from_server_challenge)
        print(self.from_server_version)
        print(self.from_server_target_name)
        print(self.from_server_target_info)

    @staticmethod
    def pack_field(value, offset):
        return pack('<HHI', len(value), len(value), offset)

    @staticmethod
    def unpack_field(field_message):
        if len(field_message) != 8:
            raise ValueError('ntlm field must be 8 bytes long')
        print('field', binascii.hexlify(field_message))
        return unpack('<H', field_message[0:2])[0], unpack('<H', field_message[2:4])[0], unpack('<I', field_message[4:8])[0]

