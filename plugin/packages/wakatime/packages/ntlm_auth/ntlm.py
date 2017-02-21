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

import base64
import socket
import struct
from ntlm_auth.constants import NegotiateFlags
from ntlm_auth.messages import NegotiateMessage, ChallengeMessage, AuthenticateMessage
from ntlm_auth.session_security import SessionSecurity


"""
utility functions for Microsoft NTLM authentication

References:
[MS-NLMP]: NT LAN Manager (NTLM) Authentication Protocol Specification
http://download.microsoft.com/download/a/e/6/ae6e4142-aa58-45c6-8dcf-a657e5900cd3/%5BMS-NLMP%5D.pdf

[MS-NTHT]: NTLM Over HTTP Protocol Specification
http://download.microsoft.com/download/a/e/6/ae6e4142-aa58-45c6-8dcf-a657e5900cd3/%5BMS-NTHT%5D.pdf

Cntlm Authentication Proxy
http://cntlm.awk.cz/

NTLM Authorization Proxy Server
http://sourceforge.net/projects/ntlmaps/

Optimized Attack for NTLM2 Session Response
http://www.blackhat.com/presentations/bh-asia-04/bh-jp-04-pdfs/bh-jp-04-seki.pdf
"""

class Ntlm(object):
    """
    Initialises the NTLM context to use when sending and receiving messages to and from the server. You should be
    using this object as it supports NTLMv2 authenticate and it easier to use than before. It also brings in the
    ability to use signing and sealing with session_security and generate a MIC structure.

    :param ntlm_compatibility: The Lan Manager Compatibility Level to use withe the auth message - Default 3
                                This is set by an Administrator in the registry key
                                'HKLM\SYSTEM\CurrentControlSet\Control\Lsa\LmCompatibilityLevel'
                                The values correspond to the following;
                                    0 : LM and NTLMv1
                                    1 : LM, NTLMv1 and NTLMv1 with Extended Session Security
                                    2 : NTLMv1 and NTLMv1 with Extended Session Security
                                    3-5 : NTLMv2 Only
                                Note: Values 3 to 5 are no different as the client supports the same types

    Attributes:
        negotiate_flags: A NEGOTIATE structure that contains a set of bit flags. These flags are the options the client supports and are sent in the negotiate_message
        ntlm_compatibility: The Lan Manager Compatibility Level, same as the input if supplied
        negotiate_message: A NegotiateMessage object that is sent to the server
        challenge_message: A ChallengeMessage object that has been created from the server response
        authenticate_message: An AuthenticateMessage object that is sent to the server based on the ChallengeMessage
        session_security: A SessionSecurity structure that can be used to sign and seal messages sent after the authentication challenge
    """
    def __init__(self, ntlm_compatibility=3):
        self.ntlm_compatibility = ntlm_compatibility

        # Setting up our flags so the challenge message returns the target info block if supported
        self.negotiate_flags = NegotiateFlags.NTLMSSP_NEGOTIATE_TARGET_INFO | \
                               NegotiateFlags.NTLMSSP_NEGOTIATE_128 | \
                               NegotiateFlags.NTLMSSP_NEGOTIATE_56 | \
                               NegotiateFlags.NTLMSSP_NEGOTIATE_UNICODE | \
                               NegotiateFlags.NTLMSSP_NEGOTIATE_VERSION | \
                               NegotiateFlags.NTLMSSP_NEGOTIATE_KEY_EXCH | \
                               NegotiateFlags.NTLMSSP_NEGOTIATE_ALWAYS_SIGN | \
                               NegotiateFlags.NTLMSSP_NEGOTIATE_SIGN | \
                               NegotiateFlags.NTLMSSP_NEGOTIATE_SEAL

        # Setting the message types based on the ntlm_compatibility level
        self._set_ntlm_compatibility_flags(self.ntlm_compatibility)

        self.negotiate_message = None
        self.challenge_message = None
        self.authenticate_message = None
        self.session_security = None


    def create_negotiate_message(self, domain_name=None, workstation=None):
        """
        Create an NTLM NEGOTIATE_MESSAGE

        :param domain_name: The domain name of the user account we are authenticating with, default is None
        :param worksation: The workstation we are using to authenticate with, default is None
        :return: A base64 encoded string of the NEGOTIATE_MESSAGE
        """
        self.negotiate_message = NegotiateMessage(self.negotiate_flags, domain_name, workstation)

        return base64.b64encode(self.negotiate_message.get_data())

    def parse_challenge_message(self, msg2):
        """
        Parse the NTLM CHALLENGE_MESSAGE from the server and add it to the Ntlm context fields

        :param msg2: A base64 encoded string of the CHALLENGE_MESSAGE
        """
        msg2 = base64.b64decode(msg2)
        self.challenge_message = ChallengeMessage(msg2)

    def create_authenticate_message(self, user_name, password, domain_name=None, workstation=None, server_certificate_hash=None):
        """
        Create an NTLM AUTHENTICATE_MESSAGE based on the Ntlm context and the previous messages sent and received

        :param user_name: The user name of the user we are trying to authenticate with
        :param password: The password of the user we are trying to authenticate with
        :param domain_name: The domain name of the user account we are authenticated with, default is None
        :param workstation: The workstation we are using to authenticate with, default is None
        :param server_certificate_hash: The SHA256 hash string of the server certificate (DER encoded) NTLM is authenticating to. Used for Channel
                                        Binding Tokens. If nothing is supplied then the CBT hash will not be sent. See messages.py AuthenticateMessage
                                        for more details
        :return: A base64 encoded string of the AUTHENTICATE_MESSAGE
        """
        self.authenticate_message = AuthenticateMessage(user_name, password, domain_name, workstation,
                                                        self.challenge_message, self.ntlm_compatibility,
                                                        server_certificate_hash)
        self.authenticate_message.add_mic(self.negotiate_message, self.challenge_message)

        # Setups up the session_security context used to sign and seal messages if wanted
        if self.negotiate_flags & NegotiateFlags.NTLMSSP_NEGOTIATE_SEAL or self.negotiate_flags & NegotiateFlags.NTLMSSP_NEGOTIATE_SIGN:
            self.session_security = SessionSecurity(struct.unpack("<I", self.authenticate_message.negotiate_flags)[0],
                                                    self.authenticate_message.exported_session_key)

        return base64.b64encode(self.authenticate_message.get_data())

    def _set_ntlm_compatibility_flags(self, ntlm_compatibility):
        if (ntlm_compatibility >= 0) and (ntlm_compatibility <= 5):
            if ntlm_compatibility == 0:
                self.negotiate_flags |= NegotiateFlags.NTLMSSP_NEGOTIATE_NTLM | \
                                        NegotiateFlags.NTLMSSP_NEGOTIATE_LM_KEY
            elif ntlm_compatibility == 1:
                self.negotiate_flags |= NegotiateFlags.NTLMSSP_NEGOTIATE_NTLM | \
                                        NegotiateFlags.NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY
            else:
                self.negotiate_flags |= NegotiateFlags.NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY
        else:
            raise Exception("Unknown ntlm_compatibility level - expecting value between 0 and 5")
