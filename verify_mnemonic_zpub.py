#!/usr/bin/env python3
"""
니모닉과 zpub 일치성 검증 스크립트
"""

import hashlib
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip84, Bip84Coins, Bip44Changes

def verify_mnemonic_zpub_pair():
    """니모닉과 zpub이 실제로 일치하는지 확인"""
    
    # 제공된 데이터
    mnemonic_phrase = "purchase banner canyon mother harbor toss sad section bomb icon trim obey"
    provided_zpub = "zpub6nNaJZM6KvEghtNGBjFMrd6Aex3pPN4WhhuH6JqUy93zZJQFhL7KPNPYcQLwJxSBaYtnCYafSXi4wpZQ74Kafs8ABwx8fQkow2cTw7KT5di"
    
    print("🔍 니모닉과 zpub 일치성 검증")
    print("=" * 50)
    print(f"📝 니모닉: {mnemonic_phrase}")
    print(f"🔑 제공된 zpub: {provided_zpub}")
    print()
    
    # 1. 니모닉 유효성 체크
    print("1️⃣ 니모닉 유효성 검사...")
    mnemo = Mnemonic("english")
    
    # 체크섬 검증 (일반적인 방법)
    try:
        is_valid = mnemo.check(mnemonic_phrase)
        print(f"   표준 체크섬 검증: {'✅ 유효' if is_valid else '❌ 무효'}")
    except:
        print("   표준 체크섬 검증: ❌ 오류")
        is_valid = False
    
    # 체크섬 무시하고 시드 생성해보기
    try:
        seed_bytes = mnemo.to_seed(mnemonic_phrase, passphrase="")
        print(f"   시드 생성: ✅ 성공 (64바이트)")
        print(f"   시드 (hex): {seed_bytes.hex()[:32]}...")
    except Exception as e:
        print(f"   시드 생성: ❌ 실패 - {e}")
        return False
    
    # 2. 니모닉에서 zpub 유도
    print("\n2️⃣ 니모닉에서 zpub 유도...")
    try:
        # BIP84 마스터 키 생성
        bip84_mst_ctx = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
        bip84_acc_ctx = bip84_mst_ctx.Purpose().Coin().Account(0)  # 계정 0
        
        # zpub 추출
        derived_zpub = bip84_acc_ctx.PublicKey().Extended()
        
        print(f"   계산된 zpub: {derived_zpub}")
        print(f"   제공된 zpub: {provided_zpub}")
        
        # 일치성 확인
        if derived_zpub == provided_zpub:
            print("   ✅ 완벽하게 일치합니다!")
            return True
        else:
            print("   ❌ 일치하지 않습니다!")
            
            # 부분 일치 확인
            if derived_zpub[:10] == provided_zpub[:10]:
                print("   ⚠️ 앞부분은 일치하지만 완전히 다름")
            else:
                print("   ⚠️ 완전히 다른 zpub입니다")
            
            return False
            
    except Exception as e:
        print(f"   ❌ zpub 유도 실패: {e}")
        return False

def generate_correct_zpub_from_mnemonic():
    """니모닉에서 올바른 zpub 생성"""
    mnemonic_phrase = "purchase banner canyon mother harbor toss sad section bomb icon trim obey"
    
    print("\n3️⃣ 니모닉에서 올바른 zpub 생성...")
    
    try:
        # 체크섬 무시하고 시드 생성
        mnemo = Mnemonic("english")
        seed_bytes = mnemo.to_seed(mnemonic_phrase, passphrase="")
        
        # BIP84 경로로 zpub 생성 (m/84'/0'/0')
        bip84_mst_ctx = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
        bip84_acc_ctx = bip84_mst_ctx.Purpose().Coin().Account(0)
        
        # 올바른 zpub
        correct_zpub = bip84_acc_ctx.PublicKey().Extended()
        
        print(f"   올바른 zpub: {correct_zpub}")
        
        # 첫 몇 개 주소도 생성해보기
        print("\n   생성되는 첫 5개 주소:")
        bip84_chg_ctx = bip84_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
        
        for i in range(5):
            bip84_addr_ctx = bip84_chg_ctx.AddressIndex(i)
            address = bip84_addr_ctx.PublicKey().ToAddress()
            print(f"   #{i}: {address}")
            
        return correct_zpub
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return None

def test_provided_zpub_addresses():
    """제공된 zpub에서 주소 생성 테스트"""
    provided_zpub = "zpub6nNaJZM6KvEghtNGBjFMrd6Aex3pPN4WhhuH6JqUy93zZJQFhL7KPNPYcQLwJxSBaYtnCYafSXi4wpZQ74Kafs8ABwx8fQkow2cTw7KT5di"
    
    print("\n4️⃣ 제공된 zpub에서 주소 생성 테스트...")
    
    try:
        # bitcoinlib 사용
        from bitcoinlib.keys import HDKey
        
        key = HDKey(provided_zpub, network='bitcoin')
        change_key = key.child_public(0)  # 외부 체인
        
        print("   제공된 zpub의 첫 5개 주소:")
        for i in range(5):
            child_key = change_key.child_public(i)
            address = child_key.address()
            print(f"   #{i}: {address}")
            
    except Exception as e:
        print(f"   ❌ 제공된 zpub 주소 생성 실패: {e}")

def compare_different_derivation_paths():
    """다른 유도 경로들 테스트"""
    mnemonic_phrase = "purchase banner canyon mother harbor toss sad section bomb icon trim obey"
    
    print("\n5️⃣ 다른 BIP 경로들 테스트...")
    
    try:
        mnemo = Mnemonic("english")
        seed_bytes = mnemo.to_seed(mnemonic_phrase, passphrase="")
        
        # BIP44 (Legacy) - m/44'/0'/0'
        print("   BIP44 (Legacy) 경로:")
        from bip_utils import Bip44, Bip44Coins
        bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
        bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
        xpub_44 = bip44_acc_ctx.PublicKey().Extended()
        print(f"   xpub: {xpub_44}")
        
        # BIP49 (SegWit Wrapped) - m/49'/0'/0'
        print("   BIP49 (P2SH-SegWit) 경로:")
        from bip_utils import Bip49, Bip49Coins
        bip49_mst_ctx = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN)
        bip49_acc_ctx = bip49_mst_ctx.Purpose().Coin().Account(0)
        ypub_49 = bip49_acc_ctx.PublicKey().Extended()
        print(f"   ypub: {ypub_49}")
        
        # BIP84 (Native SegWit) - m/84'/0'/0'
        print("   BIP84 (Native SegWit) 경로:")
        bip84_mst_ctx = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
        bip84_acc_ctx = bip84_mst_ctx.Purpose().Coin().Account(0)
        zpub_84 = bip84_acc_ctx.PublicKey().Extended()
        print(f"   zpub: {zpub_84}")
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")

def main():
    print("🔍 니모닉-zpub 쌍 검증 도구")
    print("=" * 60)
    
    # 메인 검증
    is_matching = verify_mnemonic_zpub_pair()
    
    if not is_matching:
        # 올바른 zpub 생성
        correct_zpub = generate_correct_zpub_from_mnemonic()
        
        # 제공된 zpub 테스트
        test_provided_zpub_addresses()
        
        # 다른 경로들 테스트
        compare_different_derivation_paths()
        
        print("\n" + "=" * 60)
        print("📋 분석 결과:")
        print("1. 제공된 니모닉과 zpub가 일치하지 않습니다")
        print("2. 코드에서 올바른 zpub를 사용하거나")
        print("3. 실제 사용한 니모닉을 확인해야 합니다")
        
        if correct_zpub:
            print(f"\n✅ 올바른 zpub: {correct_zpub}")
            print("   이 zpub를 WALLET_ZPUB 변수에 사용하세요")
            
    else:
        print("\n✅ 니모닉과 zpub이 완벽하게 일치합니다!")

if __name__ == "__main__":
    main()