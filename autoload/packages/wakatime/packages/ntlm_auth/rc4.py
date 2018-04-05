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

class ARC4(object):
    state = None
    i = 0
    j = 0

    def __init__(self, key):
        # Split up the key into a list
        if isinstance(key, str):
            key = [ord(c) for c in key]
        else:
            key = [c for c in key]

        #Key-scheduling algorithm (KSA)
        self.state = [n for n in range(256)]
        j = 0
        for i in range(256):
            j = (j + self.state[i] + key[i % len(key)]) % 256
            self.state[i], self.state[j] = self.state[j], self.state[i]

    def update(self, value):
        chars = []
        random_gen = self._random_generator()
        for char in value:
            if isinstance(value, str):
                byte = ord(char)
            else:
                byte = char
            updated_byte = byte ^ next(random_gen)
            chars.append(updated_byte)
        return bytes(bytearray(chars))

    def _random_generator(self):
        #Pseudo-Random Generation Algorithm (PRGA)
        while True:
            self.i = (self.i + 1) % 256
            self.j = (self.j + self.state[self.i]) % 256
            self.state[self.i], self.state[self.j] = self.state[self.j], self.state[self.i]
            yield self.state[(self.state[self.i] + self.state[self.j]) % 256]
