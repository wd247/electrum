# -*- coding: utf-8 -*-
#
# LTM Blockchain - Adaptive difficulty for laptop mining
# Extended from Electrum blockchain module
# Genesis: "David project begins" - 20a1cb14930e9cc8f0b7e6872b0630a86c135a6903aec70b6c4e63457c7948a8
#

import time
from . import constants
from .blockchain import Blockchain, InvalidHeader
from .util import bfh
from .bitcoin import hash_header

class LTMBlockchain(Blockchain):
    """
    LTM Blockchain with adaptive difficulty adjustment
    Block time: 60 seconds (1 minute)
    """
    
    @classmethod  
    def verify_header(cls, header: dict, prev_hash: str, target: int, expected_header_hash: str=None) -> None:
        """LTM header verification with adaptive difficulty support"""
        
        _hash = hash_header(header)
        if expected_header_hash and expected_header_hash != _hash:
            raise InvalidHeader("hash mismatches with expected: {} vs {}".format(expected_header_hash, _hash))
        if prev_hash != header.get('prev_block_hash'):
            raise InvalidHeader("prev hash mismatch: %s vs %s" % (prev_hash, header.get('prev_block_hash')))
            
        # LTM specific: Skip difficulty check for testnet adaptive mechanism
        if constants.net.NET_NAME in ('ltm-testnet',):
            # Allow rapid difficulty adjustment for low-spec mining
            # Testnet uses adaptive difficulty that can change drastically
            return
            
        # Standard difficulty verification for mainnet
        bits = cls.target_to_bits(target)
        if bits != header.get('bits'):
            raise InvalidHeader("bits mismatch: %s vs %s" % (bits, header.get('bits')))
            
        # Proof of work verification
        _pow_hash = hash_header(header)  # LTM uses standard SHA256d
        pow_hash_as_num = int.from_bytes(bfh(_pow_hash), byteorder='big')
        if pow_hash_as_num > target:
            raise InvalidHeader(f"insufficient proof of work: {pow_hash_as_num} vs target {target}")
    
    @classmethod
    def ltm_adaptive_difficulty(cls, current_bits: int, time_delta: int) -> int:
        """
        LTM adaptive difficulty calculation
        If block time exceeds target (60s), reduce difficulty for laptop mining
        """
        TARGET_BLOCK_TIME = 60  # 1 minute
        
        if time_delta > TARGET_BLOCK_TIME * 2:  # If taking too long
            # Reduce difficulty by making nBits larger (easier target)
            # Example: 0x912b0209 -> 0xffff0021 (much easier)
            return 0xffff0021  # Emergency low difficulty for laptop mining
        elif time_delta < TARGET_BLOCK_TIME // 2:  # If too fast
            # Increase difficulty slightly
            return max(0x1d00ffff, current_bits - 0x00010000)
        else:
            return current_bits  # Keep current difficulty
            
    def get_ltm_target(self, height: int) -> int:
        """Get target for LTM adaptive difficulty"""
        if height <= 0:
            return 0x1d00ffff  # Genesis block difficulty
            
        # For adaptive difficulty, check recent block times
        prev_header = self.read_header(height - 1)
        if not prev_header:
            return 0x1d00ffff
            
        # Calculate time since previous block
        current_time = int(time.time())
        prev_time = prev_header.get('timestamp', current_time - 60)
        time_delta = current_time - prev_time
        
        # Apply LTM adaptive difficulty
        current_bits = prev_header.get('bits', 0x1d00ffff)
        new_bits = self.ltm_adaptive_difficulty(current_bits, time_delta)
        
        return self.bits_to_target(new_bits)