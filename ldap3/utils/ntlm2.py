"""
"""

# Created on 2015.03.28
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


# PyAuthenNTLM2: A mod-python module for Apache that carries out NTLM authentication
#
# ntlm_client.py
#
# Copyright 2011 Legrandin <helderijs@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import hmac
import hashlib
import time
from math import floor
from platform import system, version
from struct import pack, unpack


# def tuc(s):
#     return s.encode('utf-16-le')

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

    return major_release, minor_release, build


class NTLMParseException(Exception):
    pass


def get_nt_timestamp():
    return (floor(time.time()) + 11644473600) * 10000000


class NTLM2Client:
    """This class implements an NTLMv2 client"""

    NTLMSSP_NEGOTIATE_UNICODE = 0x00000001
    NTLM_NEGOTIATE_OEM = 0x00000002
    NTLMSSP_REQUEST_TARGET = 0x00000004
    NTLMSSP_NEGOTIATE_LM_KEY = 0x00000080
    NTLMSSP_NEGOTIATE_NTLM = 0x00000200
    NTLMSSP_NEGOTIATE_OEM_DOMAIN_SUPPLIED = 0x00001000
    NTLMSSP_NEGOTIATE_OEM_WORKSTATION_SUPPLIED = 0x00002000
    NTLMSSP_NEGOTIATE_ALWAYS_SIGN = 0x00008000
    NTLMSSP_TARGET_TYPE_DOMAIN = 0x00010000
    NTLMSSP_TARGET_TYPE_SERVER = 0x00020000
    NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY = 0x00080000
    NTLMSSP_NEGOTIATE_TARGET_INFO = 0x00800000
    NTLMSSP_NEGOTIATE_VERSION = 0x02000000
    NTLMSSP_NEGOTIATE_128 = 0x20000000
    NTLMSSP_NEGOTIATE_KEY_EXCH = 0x40000000
    NTLMSSP_NEGOTIATE_56 = 0x80000000

    avids = {
        1: ("Server's NETBIOS name", True),
        2: ("Server's NETBIOS domain", True),
        3: ("Server's DNS name", True),
        4: ("FQDN of the domain", True),
        5: ("FQDN of the forest", True),
        6: ("Flag value", False),
        7: ("Timestamp", False),
        8: ("Restriction", False),
        9: ("SPN of the server", True),
        10: ("Channel bindings", False),
    }

    def __init__(self, username, domain, password, workstation=b'python'):
        self.username = username.upper().encode('utf-16-le')
        self.domain = domain.upper().encode('utf-16-le')
        self.password = password.encode('utf-16-le')
        self.workstation = workstation

    def create_av_pairs(self, list_avs):
        avs = ''
        for av in list_avs:
            if self.avids[av[0]][1]:
                avvalue = av[1].encode('utf_16_le')
            else:
                avvalue = av[1]
            avs += pack('<HH', av[0], len(avvalue)) + avvalue
        avs += b'\x00' * 4
        return avs

    def ntowfv2(self):
        hashed = hashlib.new('md4', self.password).digest()

        # return hmac.new(MD4.new(tuc(self.password)).digest(), tuc(self.username.upper() + self.domain)).digest()
        return hmac.new(hashed, self.username + self.domain).digest()

    def lmowfv2(self):
        return self.ntowfv2()

    def lm_nt_challenge_response(self):
        response_key_nt = self.ntowfv2()
        response_key_lm = self.lmowfv2()
        # LMv2
        lm_challenge_response = hmac.new(response_key_lm, self.server_challenge + self.client_challenge).digest() + self.client_challenge
        # NTv2
        timestamp = get_nt_timestamp()
        temp = b'\x01\x01' + b'\x00' * 6 + pack('<Q', timestamp) + self.client_challenge + b'\x00' * 4 + self.target_info + b'\x00' * 4
        ntproofstr = hmac.new(response_key_nt, self.server_challenge + temp).digest()
        ntchallengeresp = ntproofstr + temp
        # sessionKey = HMAC.new(response_key_nt, ntproofstr).digest()
        return lm_challenge_response, ntchallengeresp

    def make_ntlm_negotiate(self):
        msg = b'NTLMSSP\x00'  # Signature
        msg += pack('<I', 1)  # Message Type 1

        # Flags
        self.flags = (
            self.NTLMSSP_NEGOTIATE_UNICODE |
            self.NTLM_NEGOTIATE_OEM |
            self.NTLMSSP_REQUEST_TARGET |
            self.NTLMSSP_NEGOTIATE_LM_KEY |
            self.NTLMSSP_NEGOTIATE_NTLM |
            self.NTLMSSP_NEGOTIATE_ALWAYS_SIGN |
            self.NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY |
            self.NTLMSSP_NEGOTIATE_VERSION
        )
        msg += pack('<I', self.flags)

        # DomainNameFields
        msg += pack('<HHI', 0, 0, 0)
        # WorkstationNameFields
        msg += pack('<HHI', 0, 0, 0)
        # Version (to be removed)
        if self.flags & self.NTLMSSP_NEGOTIATE_VERSION:
            major, minor, build = windows_version()
            msg += pack('<B', major)  # Product Major: Win XP SP2
            msg += pack('<B', minor)  # Product Minor: Win XP SP2
            msg += pack('<H', build)  # ProductBuild
            msg += b'\x00\x00\x00'  # Reserved
            msg += b'\x0F'  # NTLMRevisionCurrent

        return msg

    def parse_ntlm_challenge(self, msg):
        # Signature
        idx = 0
        if msg[idx:idx + 8] != b'NTLMSSP\x00':
            raise NTLMParseException("NTLM SSP signature not found.")
        # Type
        idx += 8
        typex = unpack('<I', msg[idx:idx + 4])[0]
        if typex != 2:
            raise NTLMParseException("Not a Type 2 NTLM message (%d)." % typex)
        # TargetNameFields
        idx += 4
        target_name_len = unpack('<H', msg[idx:idx + 2])[0]
        target_name_offset = unpack('<I', msg[idx + 4:idx + 8])[0]
        # Flags
        idx += 8
        self.flags = unpack('<I', msg[idx:idx + 4])[0]
        # TargetNameFields (again)
        if self.flags and self.NTLMSSP_REQUEST_TARGET and target_name_len > 0:
            self.target_name = msg[target_name_offset:target_name_offset + target_name_len]
        # TODO: verify Unicode, since this affects DomainName in Type3
        # Server challenge
        idx += 4
        self.server_challenge = msg[idx:idx + 8]
        # TargetInfoFields
        idx += 16
        self.target_info = b''
        target_info_len = unpack('<H', msg[idx:idx + 2])[0]
        target_info_offset = unpack('<I', msg[idx + 4:idx + 8])[0]
        if self.flags and self.NTLMSSP_NEGOTIATE_TARGET_INFO and target_info_len > 0:
            self.target_info = msg[target_info_offset:target_info_offset + target_info_len]

    def make_ntlm_authenticate(self):
        self.client_challenge = os.urandom(8)

        # Pre-compute LmChallengeResponse and NtChallengeResponse
        # see 3.3.2 in MS-NLMP
        lm_challenge_response, nt_challenge_response = self.lm_nt_challenge_response()

        msg = b'NTLMSSP\x00'  # Signature
        msg += pack('<I', 3)  # Message Type 3

        fixup = []

        for f in lm_challenge_response, nt_challenge_response, self.domain, self.username, self.workstation:
            msg += pack('<H', len(f))
            msg += pack('<H', len(f))
            fixup.append((len(msg), f))
            msg += b' ' * 4  # Fake offset

        # EncryptedRandomSessionKeyFields
        assert not (self.flags & self.NTLMSSP_NEGOTIATE_KEY_EXCH)
        msg += pack('<HHI', 0, 0, 0)

        # NegotiateFlags
        self.flags &= ~(
            self.NTLMSSP_TARGET_TYPE_SERVER |
            self.NTLMSSP_TARGET_TYPE_DOMAIN |
            self.NTLMSSP_NEGOTIATE_VERSION |
            self.NTLM_NEGOTIATE_OEM
        )
        msg += pack('<I', self.flags)

        # Version
        if self.flags & self.NTLMSSP_NEGOTIATE_VERSION:
            major, minor, build = windows_version()
            msg += pack('<B', major)  # Product Major: Win XP SP2
            msg += pack('<B', minor) # Product Minor: Win XP SP2
            msg += pack('<H', build)  # ProductBuild
            msg += b'\x00\x00\x00'  # Reserved
            msg += b'\x0F'  # NTLMRevisionCurrent

        # MIC
        msg += pack('<IIII', 0, 0, 0, 0)

        # Fix up offsets
        msg = bytearray(msg)
        payload = b''
        for offset, entry in fixup:
            msg[offset:offset + 4] = pack('<I', len(msg) + len(payload))
            payload += entry
        msg = bytes(msg) + payload
        return msg

# def print_help():
# print
#     print "Performs an NTLM authentication for user\\DOMAIN against the server at the given address:"
#     print "ntlm_client {-u|--user} usr {-p|--password} pwd {-d|--domain} DOMAIN {-a|--address} address [{-g|--group} name[,name]* [{-m/--member member}]]"
#     print
#     print "    When '-a/--address' starts with 'ldap://', it is an URI of an Active Directory server."
#     print "    The URI has format ldap://serveraddres/dn"
#     print "        - serveraddress is the IP or the hostname of the AD server."
#     print "        - dn is the base Distinguished name to use for the LDAP search."
#     print "          Special characters must be escaped (space=%20, comma=%2C, equals=%3D)"
#     print "    Otherwise, the address is the IP or the hostname of a Domain Controller."
#     print
#     print "    When '-g/--group' is present, it is a comma-separated list of group accounts the user's membership is"
#     print "    checked for. It is only applicable if 'address' is an Active Directory server."
#     print
#     print "    When '-m/--member' is present, it is the name of the user to check membership for, if it's different"
#     print "    than the one specified with '-u/--user'. '-g/--group' must be present as well."
#     sys.exit(-1)
#
# if __name__ == '__main__':
#     config = dict()
#
#     if len(sys.argv)<2:
#         print_help()
#
#     try:
#         options, remain = getopt.getopt(sys.argv[1:],'hu:p:d:a:g:m:v',['help', 'user=', 'password=', 'domain=', 'address=', 'group=','member=','verbose'])
#     except getopt.GetoptError, err:
#         print err.msg
#         print_help()
#     if remain:
#         print "Unknown option", ''.join(remain)
#         print_help()
#
#     config['verbose'] = False
#     for o, v in options:
#         if o in ['-h', '--help']:
#             print_help()
#         elif o in ['-u', '--user']:
#             config['user'] = v
#         elif o in ['-p', '--password']:
#             config['password'] = v
#         elif o in ['-d', '--domain']:
#             config['domain'] = v
#         elif o in ['-a', '--address']:
#             config['address'] = v
#         elif o in ['-g', '--group']:
#             config['group'] = v.split(',')
#         elif o in ['-m', '--member']:
#             config['member'] = v
#         elif o in ['-v', '--verbose']:
#             print "Verbose mode"
#             config['verbose'] = True
#
#     if len(config)<4:
#         print "Too few options specified."
#         print_help()
#
#     if 'member' in config and not 'group' in config:
#         print "Option '-m/--memeber can only be specified together with -g/--group'."
#         print_help()
#
#     if config['address'].startswith('ldap:'):
#         print "Using Active Directory (LDAP) to verify credentials."
#         url = urlparse(config['address'])
#         proxy = NTLM_AD_Proxy(url.netloc, config['domain'], base=urllib.unquote(url.path)[1:], verbose=config['verbose'])
#     else:
#         print "Using Domain Controller to verify credentials."
#         proxy = NTLM_DC_Proxy(config['address'], config['domain'], verbose=config['verbose'])
#
#     client = NTLM_Client(config['user'],config['domain'],config['password'])
#
#     type1 = client.make_ntlm_negotiate()
#     challenge = proxy.negotiate(type1)
#     if not challenge:
#         print "Did not get the challenge!"
#         sys.exit(-2)
#
#     client.parse_ntlm_challenge(challenge)
#     authenticate = client.make_ntlm_authenticate()
#     if proxy.authenticate(authenticate):
#         print "User %s\\%s was authenticated." % (config['user'], config['domain'])
#
#         # Group membership check
#         member = config.get('member', config['user'])
#         if config['address'].startswith('ldap:') and config.has_key('group'):
#             res = proxy.check_membership(member, config['group'])
#             if res:
#                 print "User %s belongs to at least one group." % member
#             else:
#                 print "User %s does NOT belong to any group." % member
#
#     else:
#         print "User %s\\%s was NOT authenticated." % (config['user'], config['domain'])
#     proxy.close()
