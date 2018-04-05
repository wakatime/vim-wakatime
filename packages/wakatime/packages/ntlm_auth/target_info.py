"""
    Original Author: Ian Clegg
    Project: ntlmlib
    URL: https://github.com/ianclegg/ntlmlib
    License: Apache 2.0 License
    Notes: Most of this code has been copied from the messages.py in the ntlmlib repo.
    Some minor changes such as the name of the AV Pairs and extra comments have been added.
"""

import struct
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

class TargetInfo(object):
    MSV_AV_EOL                  = 0x00
    MSV_AV_NB_COMPUTER_NAME     = 0x01
    MSV_AV_NB_DOMAIN_NAME       = 0x02
    MSV_AV_DNS_COMPUTER_NAME    = 0x03
    MSV_AV_DNS_DOMAIN_NAME      = 0x04
    MSV_AV_DNS_TREE_NAME        = 0x05
    MSV_AV_FLAGS                = 0x06
    MSV_AV_TIMESTAMP            = 0x07
    MSV_AV_SINGLE_HOST          = 0x08
    MSV_AV_TARGET_NAME          = 0x09
    MSV_AV_CHANNEL_BINDINGS     = 0x0a

    def __init__(self, data=None):
        self.fields = OrderedDict()
        if data is not None:
            self.from_string(data)

    def __setitem__(self, key, value):
        self.fields[key] = (len(value), value)

    def __getitem__(self, key):
        if key in self.fields:
           return self.fields[key]
        return None

    def __delitem__(self, key):
        del self.fields[key]

    def from_string(self, data):
        attribute_type = 0xff
        while attribute_type is not TargetInfo.MSV_AV_EOL:
            # Parse the Attribute Value pair from the structure
            attribute_type = struct.unpack('<H', data[:struct.calcsize('<H')])[0]
            data = data[struct.calcsize('<H'):]
            length = struct.unpack('<H', data[:struct.calcsize('<H')])[0]
            data = data[struct.calcsize('<H'):]
            # Add a new field to the object for the parse attribute value
            self.fields[attribute_type] = (length, data[:length])
            data = data[length:]

    def get_data(self):
        if TargetInfo.MSV_AV_EOL in self.fields:
            del self.fields[TargetInfo.MSV_AV_EOL]

        data = b''
        for i in self.fields.keys():
            data += struct.pack('<HH', i, self[i][0])
            data += self[i][1]

        # end with a NTLMSSP_AV_EOL
        data += struct.pack('<HH', TargetInfo.MSV_AV_EOL, 0)
        return data