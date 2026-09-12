#!/usr/bin/python

# Test some issues with KS_OPT_SYM_RESOLVER

# Github issue: #244
# Author: Duncan (mrexodia)

from keystone import *

import regress

class TestX86(regress.RegressTest):
    def runTest(self):
        def sym_resolver(symbol, value):
            # is this the missing symbol we want to handle?
            # the callback is CFUNCTYPE(c_bool, c_char_p, POINTER(c_uint64)),
            # so the name arrives as bytes and the value is written through
            # the pointer rather than rebound
            if symbol == b"ZwQueryInformationProcess":
                # put value of this symbol in @value
                value[0] = 0x7FF98A050840
                # we handled this symbol, so return true
                return True

            # we did not handle this symbol, so return false
            return False

        # Initialize Keystone engine
        ks = Ks(KS_ARCH_X86, KS_MODE_64)
        ks.sym_resolver = sym_resolver

        encoding, _ = ks.asm(b"call 0x7FF98A050840", 0x7FF98A081A38)
        self.assertEqual(encoding, [ 0xE8, 0x03, 0xEE, 0xFC, 0xFF ])

        encoding, _ = ks.asm(b"call ZwQueryInformationProcess", 0x7FF98A081A38)
        self.assertEqual(encoding, [ 0xE8, 0x03, 0xEE, 0xFC, 0xFF ])


if __name__ == '__main__':
    regress.main()
