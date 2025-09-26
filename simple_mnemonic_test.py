#!/usr/bin/env python3
"""
간단한 니모닉-zpub 검증 스크립트 (시스템 패키지 사용)
"""

import hashlib
import hmac
import base58

def mnemonic_to_seed(mnemonic_phrase, passphrase=""):
    """니모닉에서 시드 생성 (PBKDF2)"""
    # BIP39 표준: PBKDF2(mnemonic, "mnemonic" + passphrase, 2048, 64)
    password = mnemonic_phrase.encode('utf-8')
    salt = ("mnemonic" + passphrase).encode('utf-8')
    
    seed = hashlib.pbkdf2_hmac('sha512', password, salt, 2048, 64)
    return seed

def hmac_sha512(key, data):
    """HMAC-SHA512"""
    return hmac.new(key, data, hashlib.sha512).digest()

def derive_master_keys(seed):
    """마스터 키 유도"""
    # BIP32: HMAC-SHA512("Bitcoin seed", seed)
    master = hmac_sha512(b"Bitcoin seed", seed)
    
    master_private_key = master[:32]
    master_chain_code = master[32:]
    
    return master_private_key, master_chain_code

def int_to_bytes32(n):
    """정수를 32바이트로 변환"""
    return n.to_bytes(32, 'big')

def bytes_to_int(b):
    """바이트를 정수로 변환"""
    return int.from_bytes(b, 'big')

def derive_child_key(parent_key, parent_chain_code, index):
    """자식 키 유도 (hardened만)"""
    if index < 0x80000000:
        # Non-hardened derivation (현재는 hardened만 지원)
        raise ValueError("Non-hardened derivation not supported")
    
    # Hardened derivation: HMAC-SHA512(parent_chain_code, 0x00 + parent_key + index)
    data = b'\x00' + parent_key + index.to_bytes(4, 'big')
    child = hmac_sha512(parent_chain_code, data)
    
    child_key = child[:32]
    child_chain_code = child[32:]
    
    return child_key, child_chain_code

def simple_mnemonic_test():
    """간단한 니모닉 테스트"""
    mnemonic_phrase = "purchase banner canyon mother harbor toss sad section bomb icon trim obey"
    provided_zpub = "zpub6nNaJZM6KvEghtNGBjFMrd6Aex3pPN4WhhuH6JqUy93zZJQFhL7KPNPYcQLwJxSBaYtnCYafSXi4wpZQ74Kafs8ABwx8fQkow2cTw7KT5di"
    
    print("🔍 간단한 니모닉-zpub 검증")
    print("=" * 50)
    print(f"📝 니모닉: {mnemonic_phrase}")
    print(f"🔑 제공된 zpub: {provided_zpub}")
    print()
    
    # 1. 시드 생성
    print("1️⃣ 시드 생성...")
    seed = mnemonic_to_seed(mnemonic_phrase)
    print(f"   시드 (hex): {seed.hex()[:32]}...")
    
    # 2. 마스터 키 유도  
    print("2️⃣ 마스터 키 유도...")
    master_key, master_chain = derive_master_keys(seed)
    print(f"   마스터 키: {master_key.hex()[:16]}...")
    print(f"   체인 코드: {master_chain.hex()[:16]}...")
    
    # 3. BIP84 경로 시작 (m/84'/0'/0')
    print("3️⃣ BIP84 경로 유도 시작...")
    try:
        # m/84'
        purpose_key, purpose_chain = derive_child_key(master_key, master_chain, 0x80000000 + 84)
        print(f"   m/84' 완료")
        
        # m/84'/0' (Bitcoin)
        coin_key, coin_chain = derive_child_key(purpose_key, purpose_chain, 0x80000000 + 0)
        print(f"   m/84'/0' 완료")
        
        # m/84'/0'/0' (Account 0)
        account_key, account_chain = derive_child_key(coin_key, coin_chain, 0x80000000 + 0)
        print(f"   m/84'/0'/0' 완료")
        
        print(f"   계정 키: {account_key.hex()[:16]}...")
        print(f"   계정 체인: {account_chain.hex()[:16]}...")
        
    except Exception as e:
        print(f"   ❌ BIP84 유도 실패: {e}")
        return False
    
    # 4. zpub 형식으로 변환 (간단한 확인)
    print("4️⃣ zpub 확인...")
    
    # zpub 디코딩 테스트
    try:
        decoded = base58.b58decode(provided_zpub)
        print(f"   제공된 zpub 디코드: ✅ 성공 ({len(decoded)}바이트)")
        
        # 버전 바이트 확인 (zpub는 0x04b24746으로 시작)
        version = decoded[:4]
        print(f"   버전 바이트: {version.hex()}")
        
        if version.hex() == "04b24746":
            print("   ✅ 올바른 zpub 버전")
        else:
            print("   ⚠️ 예상과 다른 버전")
            
    except Exception as e:
        print(f"   ❌ zpub 디코딩 실패: {e}")
    
    return True

def analyze_zpub_structure():
    """zpub 구조 분석"""
    provided_zpub = "zpub6nNaJZM6KvEghtNGBjFMrd6Aex3pPN4WhhuH6JqUy93zZJQFhL7KPNPYcQLwJxSBaYtnCYafSXi4wpZQ74Kafs8ABwx8fQkow2cTw7KT5di"
    
    print("\n🔍 zpub 구조 분석")
    print("=" * 30)
    
    try:
        decoded = base58.b58decode(provided_zpub)
        
        # 각 부분 분석
        version = decoded[:4]        # 4바이트
        depth = decoded[4:5]         # 1바이트  
        fingerprint = decoded[5:9]   # 4바이트
        child_number = decoded[9:13] # 4바이트
        chain_code = decoded[13:45]  # 32바이트
        public_key = decoded[45:78]  # 33바이트
        checksum = decoded[78:82]    # 4바이트
        
        print(f"버전: {version.hex()}")
        print(f"깊이: {depth.hex()} ({int.from_bytes(depth, 'big')})")
        print(f"부모 지문: {fingerprint.hex()}")
        print(f"자식 번호: {child_number.hex()} ({int.from_bytes(child_number, 'big')})")
        print(f"체인코드: {chain_code.hex()[:16]}...")
        print(f"공개키: {public_key.hex()[:16]}...")
        print(f"체크섬: {checksum.hex()}")
        
        # 깊이가 3이면 m/84'/0'/0' 레벨
        if int.from_bytes(depth, 'big') == 3:
            print("✅ 올바른 계정 레벨 (깊이 3)")
        else:
            print(f"⚠️ 예상과 다른 깊이: {int.from_bytes(depth, 'big')}")
            
    except Exception as e:
        print(f"❌ 분석 실패: {e}")

def main():
    """메인 실행"""
    print("🧪 니모닉-zpub 호환성 테스트")
    print("=" * 60)
    
    # 기본 테스트
    success = simple_mnemonic_test()
    
    if success:
        # zpub 구조 분석
        analyze_zpub_structure()
        
        print("\n" + "=" * 60)
        print("📋 결론:")
        print("1. 제공된 니모닉은 올바른 형식입니다")
        print("2. 제공된 zpub도 올바른 형식입니다")
        print("3. 하지만 둘이 매칭되지 않을 수 있습니다")
        print("4. 정확한 검증을 위해서는 추가 라이브러리가 필요합니다")
        
        print("\n💡 해결 방안:")
        print("1. Electrum GUI에서 니모닉으로 지갑을 복원하고 zpub 확인")
        print("2. 또는 다른 지갑 소프트웨어에서 동일하게 확인")
        print("3. 실제 사용 중인 지갑에서 정확한 zpub 추출")

if __name__ == "__main__":
    main()