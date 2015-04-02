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

from struct import pack


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


class NtlmClient(object):
    def __init__(self, domain, user, password):
        self.client_config_flags = 0
        self.exported_session_key = None
        self.negotiated_flags = None
        self.user = user
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

    @property
    def negotiate_flags(self):
        return pack('<I', self.client_config_flags)

    def create_negotiate_message(self):
        self.reset_flags()
        self.set_flag([FLAG_REQUEST_TARGET,
                       FLAG_NEGOTIATE_NTLM,
                       FLAG_NEGOTIATE_ALWAYS_SIGN,
                       FLAG_NEGOTIATE_UNICODE,
                       FLAG_NEGOTIATE_EXTENDED_SESSIONSECURITY])

        message = NTLM_SIGNATURE
        message += pack('<I', NTLM_MESSAGE_TYPE_NTLM_NEGOTIATE)
        message += pack('<I', self.client_config_flags)

    def buildField(self, value, offset):
        return pack('<HHI', len(value), len(value), offset)
