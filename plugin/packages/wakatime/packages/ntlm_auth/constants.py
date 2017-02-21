# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library.  If not, see <http://www.gnu.org/licenses/> or <http://www.gnu.org/licenses/lgpl.txt>.

"""
    [MS-NLMP] v28.0 2016-07-14

    2.2 Message Syntax
    The signature field used in NTLM messages
"""
NTLM_SIGNATURE = b'NTLMSSP\0'

"""
    [MS-NLMP] v28.0 2016-07-14

    2.2 Message Syntax
    The 3 message type options you can have in a message.
"""
class MessageTypes(object):
    NTLM_NEGOTIATE      = 0x1
    NTLM_CHALLENGE      = 0x2
    NTLM_AUTHENTICATE   = 0x3

"""
    [MS-NLMP] v28.0 2016-07-14

    2.2.2.1 AV_PAIR (MsvAvFlags)
    A 32-bit value indicated server or client configuration
"""
class AvFlags(object):
    AUTHENTICATION_CONSTRAINED  = 0x1
    MIC_PROVIDED                = 0x2
    UNTRUSTED_SPN_SOURCE        = 0x4

"""
    [MS-NLMP] v28.0 2016-07-14

    2.2.2.5 NEGOTIATE
    During NTLM authentication, each of the following flags is a possible value of the
    NegotiateFlags field of the NEGOTIATE_MESSAGE, CHALLENGE_MESSAGE and AUTHENTICATE_MESSAGE,
    unless otherwise noted. These flags define client or server NTLM capabilities
    supported by the sender.
"""
class NegotiateFlags(object):
    NTLMSSP_NEGOTIATE_56                            = 0x80000000
    NTLMSSP_NEGOTIATE_KEY_EXCH                      = 0x40000000
    NTLMSSP_NEGOTIATE_128                           = 0x20000000
    NTLMSSP_RESERVED_R1                             = 0x10000000
    NTLMSSP_RESERVED_R2                             = 0x08000000
    NTLMSSP_RESERVED_R3                             = 0x04000000
    NTLMSSP_NEGOTIATE_VERSION                       = 0x02000000
    NTLMSSP_RESERVED_R4                             = 0x01000000
    NTLMSSP_NEGOTIATE_TARGET_INFO                   = 0x00800000
    NTLMSSP_REQUEST_NON_NT_SESSION_KEY              = 0x00400000
    NTLMSSP_RESERVED_R5                             = 0x00200000
    NTLMSSP_NEGOTIATE_IDENTITY                      = 0x00100000
    NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY      = 0x00080000
    NTLMSSP_RESERVED_R6                             = 0x00040000
    NTLMSSP_TARGET_TYPE_SERVER                      = 0x00020000
    NTLMSSP_TARGET_TYPE_DOMAIN                      = 0x00010000
    NTLMSSP_NEGOTIATE_ALWAYS_SIGN                   = 0x00008000
    NTLMSSP_RESERVED_R7                             = 0x00004000
    NTLMSSP_NEGOTIATE_OEM_WORKSTATION_SUPPLIED      = 0x00002000
    NTLMSSP_NEGOTIATE_OEM_DOMAIN_SUPPLIED           = 0x00001000
    NTLMSSP_ANOYNMOUS                               = 0x00000800
    NTLMSSP_RESERVED_R8                             = 0x00000400
    NTLMSSP_NEGOTIATE_NTLM                          = 0x00000200
    NTLMSSP_RESERVED_R9                             = 0x00000100
    NTLMSSP_NEGOTIATE_LM_KEY                        = 0x00000080
    NTLMSSP_NEGOTIATE_DATAGRAM                      = 0x00000040
    NTLMSSP_NEGOTIATE_SEAL                          = 0x00000020
    NTLMSSP_NEGOTIATE_SIGN                          = 0x00000010
    NTLMSSP_RESERVED_R10                            = 0x00000008
    NTLMSSP_REQUEST_TARGET                          = 0x00000004
    NTLMSSP_NEGOTIATE_OEM                           = 0x00000002
    NTLMSSP_NEGOTIATE_UNICODE                       = 0x00000001

class SignSealConstants(object):
    # Magic Contants used to get the signing and sealing key for Extended Session Security
    CLIENT_SIGNING = b"session key to client-to-server signing key magic constant\0"
    SERVER_SIGNING = b"session key to server-to-client signing key magic constant\0"
    CLIENT_SEALING = b"session key to client-to-server sealing key magic constant\0"
    SERVER_SEALING = b"session key to server-to-client sealing key magic constant\0"
