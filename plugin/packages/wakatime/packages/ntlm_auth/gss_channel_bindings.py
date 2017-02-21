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

import struct

"""
    This is not the easiest structure to understand, ultimately this is a set structure
    as defined by Microsoft. Channel Binding Tokens set the SHA256 hash of the server
    certificate to the application_data field and then ultimately creates the MD5 hash
    to include in the NTLM auth from there. This class is just designed to create the
    bindings structure which is then used by compute_response.py to do the rest of the
    work.

    For more infor on how this works and how it is derived, this is a great link;
    https://blogs.msdn.microsoft.com/openspecification/2013/03/26/ntlm-and-channel-binding-hash-aka-extended-protection-for-authentication/
"""
class GssChannelBindingsStruct(object):
    INITIATOR_ADDTYPE = 'initiator_addtype'
    INITIATOR_ADDRESS_LENGTH = 'initiator_address_length'
    ACCEPTOR_ADDRTYPE = 'acceptor_addrtype'
    ACCEPTOR_ADDRESS_LENGTH = 'acceptor_address_length'
    APPLICATION_DATA_LENGTH = 'application_data_length'
    INITIATOR_ADDRESS = 'initiator_address'
    ACCEPTOR_ADDRESS = 'acceptor_address'
    APPLICATION_DATA = 'application_data'

    def __init__(self):
        self.fields = {}
        self.fields[self.INITIATOR_ADDTYPE] = 0
        self.fields[self.INITIATOR_ADDRESS_LENGTH] = 0
        self.fields[self.ACCEPTOR_ADDRTYPE] = 0
        self.fields[self.ACCEPTOR_ADDRESS_LENGTH] = 0
        self.fields[self.APPLICATION_DATA_LENGTH] = 0
        self.fields[self.INITIATOR_ADDRESS] = b''
        self.fields[self.ACCEPTOR_ADDRESS] = b''
        self.fields[self.APPLICATION_DATA] = b''

    def __setitem__(self, key, value):
        self.fields[key] = value

    def get_data(self):
        # Set the lengths of each len field in case they have changed
        self.fields[self.INITIATOR_ADDRESS_LENGTH] = len(self.fields[self.INITIATOR_ADDRESS])
        self.fields[self.ACCEPTOR_ADDRESS_LENGTH] = len(self.fields[self.ACCEPTOR_ADDRESS])
        self.fields[self.APPLICATION_DATA_LENGTH] = len(self.fields[self.APPLICATION_DATA])

        # Add all the values together to create the gss_channel_bindings_struct
        data = struct.pack('<L', self.fields[self.INITIATOR_ADDTYPE]) + \
               struct.pack('<L', self.fields[self.INITIATOR_ADDRESS_LENGTH]) + \
               self.fields[self.INITIATOR_ADDRESS] + \
               struct.pack('<L', self.fields[self.ACCEPTOR_ADDRTYPE]) + \
               struct.pack('<L', self.fields[self.ACCEPTOR_ADDRESS_LENGTH]) + \
               self.fields[self.ACCEPTOR_ADDRESS] + \
               struct.pack('<L', self.fields[self.APPLICATION_DATA_LENGTH]) + \
               self.fields[self.APPLICATION_DATA]

        return data