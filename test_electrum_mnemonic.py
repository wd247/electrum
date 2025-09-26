#!/usr/bin/env python3
"""
Electrum을 사용한 니모닉-zpub 검증
"""

import sys
import os

# Electrum 모듈 경로 추가
sys.path.insert(0, '/home/junny/electrum')

def test_mnemonic_with_electrum():
    """Electrum 라이브러리로 니모닉 검증"""
    
    mnemonic_phrase = "purchase banner canyon mother harbor toss sad section bomb icon trim obey"
    provided_zpub = "zpub6nNaJZM6KvEghtNGBjFMrd6Aex3pPN4WhhuH6JqUy93zZJQFhL7KPNPYcQLwJxSBaYtnCYafSXi4wpZQ74Kafs8ABwx8fQkow2cTw7KT5di"
    
    print("🔍 Electrum으로 니모닉-zpub 검증")
    print("=" * 50)
    print(f"📝 니모닉: {mnemonic_phrase}")
    print(f"🔑 제공된 zpub: {provided_zpub}")
    print()
    
    try:
        # Electrum 모듈 import
        from electrum.mnemonic import Mnemonic
        from electrum.keystore import from_bip39_seed
        from electrum.bip32 import BIP32Node
        
        print("1️⃣ Electrum 니모닉 검증...")
        
        # 니모닉 유효성 확인
        m = Mnemonic('en')
        
        # 체크섬 확인
        try:
            is_valid = m.check(mnemonic_phrase)
            print(f"   체크섬 검증: {'✅ 유효' if is_valid else '❌ 무효'}")
        except:
            print("   체크섬 검증: ❌ 실패 (단어 사전에 없음)")
            is_valid = False
        
        # 시드 생성 (체크섬 무시)
        print("2️⃣ 시드 생성...")
        seed = m.mnemonic_to_seed(mnemonic_phrase, passphrase="")
        print(f"   시드: {seed.hex()[:32]}...")
        
        # BIP32 마스터 노드 생성
        print("3️⃣ BIP32 마스터 키 생성...")
        master = BIP32Node.from_rootseed(seed, xtype='standard')
        print(f"   마스터 키 생성: ✅ 성공")
        
        # BIP84 경로로 계정 키 유도 (m/84'/0'/0')
        print("4️⃣ BIP84 계정 키 유도...")
        
        # Native SegWit (zpub) 경로
        account_path = "m/84'/0'/0'"
        account_node = master.subkey_at_path(account_path)
        
        # zpub 생성
        derived_zpub = account_node.to_xpub()
        print(f"   유도된 zpub: {derived_zpub}")
        
        # 비교
        print("5️⃣ zpub 비교...")
        if derived_zpub == provided_zpub:
            print("   ✅ 완벽하게 일치합니다!")
            return True
        else:
            print("   ❌ 일치하지 않습니다!")
            print(f"   제공된:  {provided_zpub}")
            print(f"   계산된:  {derived_zpub}")
            
            # 차이점 분석
            if len(derived_zpub) == len(provided_zpub):
                diff_count = sum(1 for a, b in zip(derived_zpub, provided_zpub) if a != b)
                print(f"   차이나는 문자: {diff_count}개")
            
            return False
            
    except ImportError as e:
        print(f"❌ Electrum 모듈 import 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 검증 중 오류: {e}")
        return False

def test_first_few_addresses():
    """첫 몇 개 주소 생성 테스트"""
    mnemonic_phrase = "purchase banner canyon mother harbor toss sad section bomb icon trim obey"
    
    print("\n6️⃣ 첫 5개 주소 생성 테스트...")
    
    try:
        from electrum.mnemonic import Mnemonic
        from electrum.bip32 import BIP32Node
        from electrum.bitcoin import pubkey_to_address
        
        # 시드 생성
        m = Mnemonic('en')
        seed = m.mnemonic_to_seed(mnemonic_phrase, passphrase="")
        
        # BIP32 마스터 노드
        master = BIP32Node.from_rootseed(seed, xtype='standard')
        
        # BIP84 계정 노드 (m/84'/0'/0')
        account_node = master.subkey_at_path("m/84'/0'/0'")
        
        # 외부 체인 (m/84'/0'/0'/0)
        external_chain = account_node.subkey_at_path("0")
        
        print("   니모닉에서 생성된 주소들:")
        for i in range(5):
            # 각 주소 노드 (m/84'/0'/0'/0/i)
            addr_node = external_chain.subkey_at_path(str(i))
            
            # 공개키에서 주소 생성 (P2WPKH)
            pubkey = addr_node.eckey.get_public_key_bytes(compressed=True)
            address = pubkey_to_address('p2wpkh', pubkey)
            
            print(f"   #{i}: {address}")
            
    except Exception as e:
        print(f"   ❌ 주소 생성 실패: {e}")

def main():
    """메인 실행"""
    print("🧪 Electrum 기반 니모닉-zpub 검증")
    print("=" * 60)
    
    # 메인 검증
    is_matching = test_mnemonic_with_electrum()
    
    # 주소 생성 테스트
    test_first_few_addresses()
    
    print("\n" + "=" * 60)
    if is_matching:
        print("✅ 니모닉과 zpub이 일치합니다!")
        print("   코드에 오류는 없습니다.")
    else:
        print("❌ 니모닉과 zpub이 일치하지 않습니다!")
        print("   다음을 확인하세요:")
        print("   1. 실제 사용한 니모닉이 정확한지")
        print("   2. 지갑에서 추출한 zpub가 정확한지") 
        print("   3. BIP 유도 경로가 올바른지 (m/84'/0'/0')")

if __name__ == "__main__":
    main()