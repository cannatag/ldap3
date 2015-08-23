"""
"""

# Created on 2015.08.19
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

from pyasn1.codec.ber.encoder import tagMap, BooleanEncoder
from pyasn1.type.univ import Boolean
from pyasn1.compat.octets import ints2octs

CLASSES = {(False, False): 'UNIVERSAL',
           (False, True): 'APPLICATION',
           (True, False): 'CONTEXT',
           (True, True): 'PRIVATE'}


# Monkeypatching of pyasn1 for encoding Boolean with the value 0xFF for TRUE
class BooleanCEREncoder(BooleanEncoder):
    _true = ints2octs((255,))

tagMap[Boolean.tagSet] = BooleanCEREncoder()

from pyasn1.codec.ber import encoder, decoder

def compare_ldap_responses(r1, r2):
    if r1 == r2:
        print('OK')
    else:
        print('NO')


def compute_ber_size(data):
    """
    Compute size according to BER definite length rules
    """

    if isinstance(data, str):  # fix for Python 2, data is string not bytes
        data = bytearray(data)  # Python 2 bytearray is equivalent to Python 3 bytes

    if data[1] <= 127:  # BER definite length - short form. Highest bit of byte 1 is 0, message length is in the last 7 bits - Value can be up to 127 bytes long
        return data[1], 2
    else:  # BER definite length - long form. Highest bit of byte 1 is 1, last 7 bits counts the number of following octets containing the value length
        bytes_length = data[1] - 128
        value_length = 0
        cont = bytes_length
        for byte in data[2: 2 + bytes_length]:
            cont -= 1
            value_length += byte * (256 ** cont)
        ret_value = value_length + 2 + bytes_length

        return ret_value, bytes_length + 2


def get_ber_tag(octet):
    # print(bin(octet))
    # print(bin(octet & 0b10000000))
    # print(bin(octet & 0b01000000))
    # print(bin(octet & 0b00100000))
    # print(bin(octet & 0b00011111))

    ber_class = CLASSES[(bool(octet & 0b10000000), bool(octet & 0b01000000))]

    if ber_class == 'UNIVERSAL':
        ber_type = UNIVERSAL_TYPES[octet & 0b00011111]
    elif ber_class == 'APPLICATION':
        ber_type = APPLICATION_TYPES[octet & 0b00011111]
    else:
        ber_type = octet & 0b00011111

    return ber_class, bool(octet & 0b00100000), ber_type


def decode_message(message):
    print('*** MESSAGE DECODER ***')
    decode_tlv(message, 0, len(message))


def decode_tlv(message, start, stop):
    while start < stop:
        ber_class, ber_constructed, ber_type = get_ber_tag(message[start])
        ber_len, ber_value_offset = compute_ber_size(message[start:])
        start += ber_value_offset
        print(ber_class[0], ber_constructed, ber_type[0], ber_len, ber_value_offset)
        if not ber_constructed:
            if ber_type[1]:
                value = ber_type[1](message, start, start + ber_len)
            else:
                value = message[start: start + ber_len]
            print(value)
        else:
            if ber_type[1]:
                ber_type[1](message, start, start + ber_len)  # call decode function
            else:
                print('need decoder for', ber_class, ber_constructed, ber_type[0], 'start:', ber_value_offset, '-', ber_len)
        start += ber_len


def decode_integer(message, start, stop):
    # adapted from pyasn1
    first = message[start]
    if first & 0x80:
        value = -1
    else:
        value = 0
    for octet in message[start: stop]:
        value = value << 8 | octet

    return value


def decode_octet_string(message, start, stop):
    value = message[start: stop]
    return value


def decode_boolean(message, start, stop):
    raise NotImplementedError


def decode_sequence(message, start, stop):
    print('*** SEQUENCE DECODER ***')
    decode_tlv(message, start, stop)


def decode_bind_response(message, start, stop):
    print('*** BIND RESPONSE DECODER ***')
    decode_tlv(message, start, stop)

UNIVERSAL_TYPES = {1: ('BOOLEAN', decode_boolean),
                   2: ('INTEGER', decode_integer),
                   4: ('OCTET STRING', decode_octet_string),
                   10: ('ENUMERATED', decode_integer),
                   16: ('SEQUENCE', decode_sequence),
                   17: ('SET', decode_sequence)}


APPLICATION_TYPES = {1: ('BIND RESPONSE', decode_bind_response)}
