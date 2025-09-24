#!/usr/bin/env python3
"""
LTM HD 지갑 생성 및 공개키 확인 도구
BIP32 P2WPKH (bc1 주소) 지갑 생성
"""

import sys
import os
sys.path.insert(0, '/home/junny/electrum')

from electrum import constants
from electrum.keystore import BIP32_KeyStore
from electrum.mnemonic import Mnemonic
from electrum.bitcoin import pubkey_to_address, hash_160
from electrum.segwit_addr import encode_segwit_address
import hashlib

def create_ltm_hd_wallet():
    """LTM HD 지갑 생성"""
    
    # LTM 네트워크로 설정
    constants.LTMMainnet.set_as_network()
    
    print("🔑 LTM HD 지갑 생성 (BIP32 P2WPKH)")
    print("=" * 50)
    
    # 1. 새로운 니모닉 생성
    mnemonic = Mnemonic('en')
    seed_words = mnemonic.make_seed(seed_type='segwit', num_bits=132)  # 12단어
    
    print(f"📝 니모닉 (12단어):")
    print(f"   {seed_words}")
    print()
    
    # 2. 시드에서 마스터 키 생성
    seed = mnemonic.mnemonic_to_seed(seed_words, passphrase="")
    
    print(f"🌱 시드 (hex):")
    print(f"   {seed.hex()[:64]}...")
    print()
    
    # 3. 시드에서 BIP32 KeyStore 생성
    from electrum.keystore import from_seed
    keystore = from_seed(seed_words, passphrase="", for_multisig=False)
    
    # 4. 마스터 공개키 정보
    master_xpub = keystore.get_master_public_key()
    print(f"🔐 마스터 확장 공개키 (xpub):")
    print(f"   {master_xpub}")
    print()
    
    # 5. BIP44 경로로 주소 생성 (m/84'/0'/0'/0/n)
    # LTM은 Bitcoin 호환이므로 coin type 0 사용
    
    addresses = []
    public_keys = []
    
    print(f"📋 HD 지갑 주소 및 공개키 (처음 20개)")
    print(f"   경로: m/84'/0'/0'/0/n (BIP84 P2WPKH)")
    print("-" * 80)
    
    for i in range(20):
        # BIP84 경로: m/84'/0'/0'/0/i
        derivation_path = f"m/84'/0'/0'/0/{i}"
        
        # 개별 공개키 생성
        pubkey = keystore.derive_pubkey(0, i)  # 0 = receiving addresses
        
        # bc1 주소 생성 (P2WPKH)
        address = pubkey_to_p2wpkh_address(pubkey)
        
        addresses.append(address)
        public_keys.append(pubkey)
        
        print(f"{i+1:2d}. {address}")
        print(f"    공개키: {pubkey}")
        print(f"    경로:   {derivation_path}")
        print()
    
    return {
        'mnemonic': seed_words,
        'seed': seed.hex(),
        'master_xpub': master_xpub,
        'addresses': addresses,
        'public_keys': public_keys
    }

def pubkey_to_p2wpkh_address(pubkey_hex):
    """공개키를 P2WPKH (bc1) 주소로 변환"""
    try:
        # 공개키를 바이트로 변환
        if isinstance(pubkey_hex, str):
            pubkey_bytes = bytes.fromhex(pubkey_hex)
        else:
            pubkey_bytes = pubkey_hex
            
        # 공개키 해시 생성 (HASH160)
        pubkey_hash = hash_160(pubkey_bytes)
        
        # bc1 주소 생성 (Bech32) - LTM은 Bitcoin 호환
        address = encode_segwit_address('bc', 0, pubkey_hash)
        return address
        
    except Exception as e:
        print(f"주소 변환 오류: {e}")
        return None

def verify_wallet_info(wallet_info):
    """생성된 지갑 정보 검증"""
    
    print("\n🔍 지갑 정보 검증")
    print("=" * 30)
    
    # 니모닉 검증 (간단한 단어 수 확인)
    words = wallet_info['mnemonic'].split()
    is_valid = len(words) == 12 and all(len(word) > 0 for word in words)
    print(f"✅ 니모닉 유효성: {'통과 (12단어)' if is_valid else '실패'}")
    
    # 주소 개수 확인
    print(f"✅ 생성된 주소 개수: {len(wallet_info['addresses'])}개")
    
    # 첫 번째 주소 형식 확인
    first_addr = wallet_info['addresses'][0]
    is_bc1 = first_addr.startswith('bc1q')
    print(f"✅ 주소 형식: {'bc1 (P2WPKH)' if is_bc1 else '다른 형식'}")
    
    # 공개키 길이 확인
    first_pubkey = wallet_info['public_keys'][0]
    pubkey_len = len(first_pubkey)
    print(f"✅ 공개키 길이: {pubkey_len} 문자 ({'압축된 공개키' if pubkey_len == 66 else '비압축 또는 다른 형식'})")

def save_wallet_info(wallet_info):
    """지갑 정보를 파일로 저장"""
    
    filename = "ltm_hd_wallet_info.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("LTM HD 지갑 정보\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"니모닉: {wallet_info['mnemonic']}\n")
        f.write(f"시드: {wallet_info['seed']}\n")
        f.write(f"마스터 xpub: {wallet_info['master_xpub']}\n\n")
        
        f.write("주소 및 공개키 목록:\n")
        f.write("-" * 80 + "\n")
        
        for i, (addr, pubkey) in enumerate(zip(wallet_info['addresses'], wallet_info['public_keys'])):
            f.write(f"{i+1:2d}. {addr}\n")
            f.write(f"    공개키: {pubkey}\n")
            f.write(f"    경로: m/84'/0'/0'/0/{i}\n\n")
    
    print(f"\n💾 지갑 정보가 '{filename}'에 저장되었습니다.")

def main():
    try:
        # HD 지갑 생성
        wallet_info = create_ltm_hd_wallet()
        
        # 검증
        verify_wallet_info(wallet_info)
        
        # 파일 저장
        save_wallet_info(wallet_info)
        
        print("\n🎉 LTM HD 지갑 생성 완료!")
        print("\n⚠️  중요 사항:")
        print("   - 니모닉 문구를 안전한 곳에 보관하세요")
        print("   - 이 정보가 있으면 지갑을 복구할 수 있습니다")
        print("   - 다른 사람과 공유하지 마세요")
        
        # 첫 번째 주소 잔액 확인 제안
        first_address = wallet_info['addresses'][0]
        print(f"\n💡 첫 번째 주소 잔액 확인:")
        print(f"   python3 ltm_balance_proper.py {first_address}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()