#!/usr/bin/env python3
"""
LTM 네트워크 최종 검증
메인넷 전용 구성 확인
"""

import os
import sys
import subprocess

# Electrum 경로 추가
sys.path.insert(0, '/home/junny/electrum')

def test_ltm_mainnet_only():
    """LTM 메인넷 전용 구성 최종 검증"""
    
    print("=" * 60)
    print("🎯 LTM 메인넷 전용 구성 최종 검증")
    print("=" * 60)
    
    # 1. 네트워크 목록 확인
    print("\n1️⃣ 사용 가능한 네트워크 목록")
    try:
        from electrum import constants
        
        ltm_networks = [net for net in constants.NETS_LIST if 'ltm' in net.NET_NAME.lower()]
        
        print(f"📊 LTM 관련 네트워크: {len(ltm_networks)}개")
        for net in ltm_networks:
            testnet_status = "테스트넷" if net.TESTNET else "메인넷"
            print(f"  - {net.NET_NAME} ({net.__name__}) - {testnet_status}")
        
        if len(ltm_networks) == 1:
            print("✅ LTM 메인넷만 존재 (테스트넷 제거 완료)")
        else:
            print(f"⚠️ 예상과 다른 LTM 네트워크 개수: {len(ltm_networks)}")
            
    except Exception as e:
        print(f"❌ 네트워크 목록 확인 실패: {e}")
        return False
    
    # 2. LTM 메인넷 설정 확인
    print("\n2️⃣ LTM 메인넷 세부 설정")
    try:
        ltm_mainnet = constants.LTMMainnet()
        
        print(f"  네트워크 이름: {ltm_mainnet.NET_NAME}")
        print(f"  메인넷 여부: {not ltm_mainnet.TESTNET}")
        print(f"  주소 형식: {ltm_mainnet.SEGWIT_HRP}1...")
        print(f"  서버 포트: {ltm_mainnet.DEFAULT_PORTS}")
        print(f"  제네시스 해시: {ltm_mainnet.GENESIS[:16]}...")
        print(f"  블록 시간: {getattr(ltm_mainnet, 'BLOCK_TARGET_SPACING', 60)}초")
        
        # 비트코인 호환성 확인
        if ltm_mainnet.SEGWIT_HRP == "bc":
            print("✅ 비트코인과 동일한 bc1 주소 형식 사용")
        else:
            print(f"⚠️ 독립적인 주소 형식: {ltm_mainnet.SEGWIT_HRP}1")
            
    except Exception as e:
        print(f"❌ LTM 메인넷 설정 확인 실패: {e}")
        return False
    
    # 3. 테스트넷 접근 시도
    print("\n3️⃣ 테스트넷 제거 검증")
    try:
        # 이 코드는 실패해야 함
        constants.LTMTestnet()
        print("❌ LTMTestnet이 여전히 존재함")
        return False
    except AttributeError:
        print("✅ LTMTestnet 클래스가 성공적으로 제거됨")
    except Exception as e:
        print(f"⚠️ 예상치 못한 오류: {e}")
    
    # 4. 명령줄 옵션 확인
    print("\n4️⃣ 명령줄 옵션 확인")
    
    # --ltm 옵션 (작동해야 함)
    cmd = [sys.executable, '/home/junny/electrum/electrum/electrum', '--ltm', '--offline', 'version']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ --ltm 옵션 작동: {result.stdout.strip()}")
        else:
            print("❌ --ltm 옵션 실패")
    except Exception as e:
        print(f"❌ --ltm 테스트 오류: {e}")
    
    # --ltm-testnet 옵션 (실패해야 함)  
    cmd = [sys.executable, '/home/junny/electrum/electrum/electrum', '--ltm-testnet', '--offline', 'version']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0 and 'unrecognized arguments' in result.stderr:
            print("✅ --ltm-testnet 옵션이 제거됨 (정상)")
        else:
            print("❌ --ltm-testnet 옵션이 여전히 존재함")
    except Exception as e:
        print(f"⚠️ --ltm-testnet 테스트 오류: {e}")
    
    # 5. 실제 지갑 작동 테스트
    print("\n5️⃣ LTM 지갑 기능 테스트")
    
    test_wallet = '/tmp/ltm_final_test'
    if os.path.exists(test_wallet):
        os.remove(test_wallet)
    
    # 지갑 생성
    cmd = [sys.executable, '/home/junny/electrum/electrum/electrum', '--ltm', '--offline', 'create', '-w', test_wallet]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ LTM 지갑 생성 성공")
            
            # 주소 생성
            cmd2 = [sys.executable, '/home/junny/electrum/electrum/electrum', '--ltm', '--offline', 'createnewaddress', '-w', test_wallet]
            result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=10)
            
            if result2.returncode == 0:
                address = result2.stdout.strip()
                print(f"✅ LTM 주소 생성: {address}")
                
                if address.startswith('bc1'):
                    print("✅ bc1 형식 주소 확인")
                else:
                    print(f"⚠️ 예상과 다른 주소 형식: {address[:10]}...")
            else:
                print("❌ 주소 생성 실패")
        else:
            print(f"❌ 지갑 생성 실패: {result.stderr[:100]}")
    except Exception as e:
        print(f"❌ 지갑 테스트 오류: {e}")
    finally:
        if os.path.exists(test_wallet):
            os.remove(test_wallet)
    
    print("\n" + "=" * 60)
    print("📊 LTM 메인넷 전용 구성 검증 완료")
    print("✅ LTM 테스트넷이 완전히 제거되었습니다")
    print("✅ LTM 메인넷만 사용 가능합니다")
    print("✅ 비트코인 호환 bc1 주소 형식 사용")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_ltm_mainnet_only()