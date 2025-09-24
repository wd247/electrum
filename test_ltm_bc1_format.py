#!/usr/bin/env python3
"""
LTM 코인 bc1 주소 형식 검증 테스트
비트코인과 동일한 주소 형식 사용 확인
"""

import os
import sys
import subprocess

# Electrum 경로 추가
sys.path.insert(0, '/home/junny/electrum')

def test_ltm_bc1_addresses():
    """LTM 네트워크의 bc1 주소 형식 테스트"""
    
    print("=" * 60)
    print("🏠 LTM 코인 bc1 주소 형식 검증")
    print("=" * 60)
    
    # 1. 네트워크 설정 확인
    print("\n1️⃣ LTM 네트워크 설정 확인")
    try:
        from electrum import constants
        
        ltm_mainnet = constants.LTMMainnet()
        ltm_testnet = constants.LTMTestnet()
        
        print(f"✅ LTM 메인넷 SEGWIT_HRP: {ltm_mainnet.SEGWIT_HRP}")
        print(f"✅ LTM 테스트넷 SEGWIT_HRP: {ltm_testnet.SEGWIT_HRP}")
        
        # 비트코인과 동일한지 확인
        bitcoin_mainnet = constants.BitcoinMainnet()
        bitcoin_testnet = constants.BitcoinTestnet()
        
        if ltm_mainnet.SEGWIT_HRP == bitcoin_mainnet.SEGWIT_HRP:
            print("✅ LTM 메인넷이 비트코인과 동일한 bc1 형식 사용")
        else:
            print(f"❌ LTM: {ltm_mainnet.SEGWIT_HRP} vs 비트코인: {bitcoin_mainnet.SEGWIT_HRP}")
            
        if ltm_testnet.SEGWIT_HRP == bitcoin_testnet.SEGWIT_HRP:
            print("✅ LTM 테스트넷이 비트코인 테스트넷과 동일한 tb1 형식 사용")
        else:
            print(f"❌ LTM 테스트넷: {ltm_testnet.SEGWIT_HRP} vs 비트코인 테스트넷: {bitcoin_testnet.SEGWIT_HRP}")
            
    except Exception as e:
        print(f"❌ 네트워크 설정 확인 실패: {e}")
        return False
    
    # 2. 실제 주소 생성 테스트
    print("\n2️⃣ 실제 LTM 주소 생성 테스트")
    
    # 기존 테스트 지갑 삭제
    test_wallet = '/tmp/ltm_bc1_test_wallet'
    if os.path.exists(test_wallet):
        os.remove(test_wallet)
    
    # 새 LTM 지갑 생성
    cmd = [
        sys.executable,
        '/home/junny/electrum/electrum/electrum',
        '--ltm',
        '--offline',
        'create',
        '-w', test_wallet
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ LTM 지갑 생성 성공")
        else:
            print(f"❌ 지갑 생성 실패: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 지갑 생성 오류: {e}")
        return False
    
    # 3. 여러 주소 생성하여 형식 확인
    print("\n3️⃣ bc1 주소 형식 검증")
    
    addresses = []
    for i in range(5):
        cmd = [
            sys.executable,
            '/home/junny/electrum/electrum/electrum',
            '--ltm',
            '--offline',
            'createnewaddress',
            '-w', test_wallet
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                address = result.stdout.strip()
                addresses.append(address)
                prefix = address[:3] if len(address) >= 3 else address
                print(f"  주소 {i+1}: {address[:20]}... (접두사: {prefix})")
            else:
                print(f"❌ 주소 {i+1} 생성 실패")
        except Exception as e:
            print(f"❌ 주소 {i+1} 생성 오류: {e}")
    
    # 4. 주소 형식 분석
    print("\n4️⃣ 주소 형식 분석")
    
    bc1_count = sum(1 for addr in addresses if addr.startswith('bc1'))
    ltm1_count = sum(1 for addr in addresses if addr.startswith('ltm1'))
    other_count = len(addresses) - bc1_count - ltm1_count
    
    print(f"  bc1 주소: {bc1_count}개")
    print(f"  ltm1 주소: {ltm1_count}개") 
    print(f"  기타 주소: {other_count}개")
    
    if bc1_count == len(addresses):
        print("✅ 모든 LTM 주소가 bc1 형식 사용 (비트코인 호환)")
    elif ltm1_count == len(addresses):
        print("⚠️ 모든 LTM 주소가 ltm1 형식 사용 (LTM 전용)")
    else:
        print("❌ 주소 형식이 일관되지 않음")
    
    # 5. 정리
    if os.path.exists(test_wallet):
        os.remove(test_wallet)
        print("\n🧹 테스트 지갑 파일 정리 완료")
    
    print("\n" + "=" * 60)
    print("📊 LTM bc1 주소 형식 테스트 완료")
    
    if bc1_count > 0:
        print("✅ LTM 네트워크가 비트코인 호환 bc1 주소 형식을 사용합니다")
    else:
        print("⚠️ LTM 네트워크가 독립적인 주소 형식을 사용합니다")
    
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_ltm_bc1_addresses()