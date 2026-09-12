#!/usr/bin/python

# Test RISCV jal/branch fixups against labels defined later in the block.
# adjustFixupValue() ran its range checks without braces, so the `return -1`
# guarded by them was unconditional: every forward reference assembled to
# 0xffffffff. The invalid-fixup error was also passed back by value and so
# never reached the caller.

# Author: borzacchiello

from keystone import *

import regress

class TestRISCV64ForwardBranch(regress.RegressTest):
    def runTest(self):
        ks = Ks(KS_ARCH_RISCV, KS_MODE_RISCV64)
        # "nop" assembles to the two byte c.nop, so L sits at offset 6 and the
        # branch displacement is +6: beq a0, a1, 6 == 0x00b50363
        encoding, _ = ks.asm(b"beq a0, a1, L; nop; L: nop")
        self.assertEqual(encoding[:4], [ 0x63, 0x03, 0xb5, 0x00 ])

class TestRISCV64ForwardJal(regress.RegressTest):
    def runTest(self):
        ks = Ks(KS_ARCH_RISCV, KS_MODE_RISCV64)
        # jal ra, 6 == 0x006000ef
        encoding, _ = ks.asm(b"jal L; nop; L: nop")
        self.assertEqual(encoding[:4], [ 0xef, 0x00, 0x60, 0x00 ])

class TestRISCV64BranchImmediate(regress.RegressTest):
    def runTest(self):
        # a displacement the parser folds needs no fixup, and kept working
        # throughout; keep it here so the two paths stay compared
        ks = Ks(KS_ARCH_RISCV, KS_MODE_RISCV64)
        encoding, _ = ks.asm(b"beq a0, a1, 8")
        self.assertEqual(encoding, [ 0x63, 0x04, 0xb5, 0x00 ])
        encoding, _ = ks.asm(b"jal 8")
        self.assertEqual(encoding, [ 0xef, 0x00, 0x80, 0x00 ])

class TestRISCV64BranchOutOfRange(regress.RegressTest):
    def runTest(self):
        # a conditional branch reaches +-4KiB; past that the fixup is invalid
        # and keystone has to report it rather than return a bogus encoding
        ks = Ks(KS_ARCH_RISCV, KS_MODE_RISCV64)
        with self.assertRaises(KsError) as ctx:
            ks.asm(b"beq a0, a1, L; .space 5000; L: nop")
        self.assertEqual(ctx.exception.errno, KS_ERR_ASM_FIXUP_INVALID)

if __name__ == '__main__':
    regress.main()
