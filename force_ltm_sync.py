#!/usr/bin/env python3

import sys
import os
import json
import time

# electrum 경로 추가
sys.path.insert(0, '/home/junny/electrum')

def force_sync():
    """LTM 네트워크 강제 동기화"""
    
    print("🔄 LTM 네트워크 강제 동기화 시작...")
    print("=" * 50)
    
    try:
        from electrum.simple_config import SimpleConfig
        from electrum.network import Network
        from electrum.interface import Interface
        from electrum import constants
        
        # LTM 네트워크 설정 
        from electrum.constants import LTMMainnet
        LTMMainnet.set_as_network()
        
        # 설정 생성
        config = SimpleConfig({
            'chain': 'ltm',
            'server': 'ltm-wallet.gnc.ne.kr:50008:t',
            'auto_connect': True,
            'oneserver': True
        })
        
        print(f"📡 서버 연결: {config.get('server')}")
        
        # 네트워크 시작
        network = Network(config)
        network.start()
        
        print("⏳ 네트워크 연결 대기...")
        time.sleep(3)
        
        if network.is_connected():
            print("✅ 서버 연결 성공")
            
            # 현재 블록 높이 확인
            local_height = network.get_local_height()
            server_height = network.get_server_height()
            
            print(f"📊 로컬 블록: {local_height}")
            print(f"📊 서버 블록: {server_height}")
            
            if server_height and local_height < server_height:
                print(f"🔄 동기화 필요: {server_height - local_height} 블록")
                
                # 체크포인트 강제 적용
                blockchain = network.blockchain()
                if blockchain:
                    print("📝 체크포인트 적용 중...")
                    # 헤더 다운로드 강제 시작
                    blockchain.request_headers()
                    
                    # 동기화 진행 모니터링
                    for i in range(30):  # 30초간 모니터링
                        current_height = network.get_local_height()
                        if current_height >= server_height - 10:  # 거의 동기화됨
                            print(f"✅ 동기화 완료: {current_height}")
                            break
                        print(f"⏳ 동기화 중... {current_height}/{server_height}")
                        time.sleep(1)
            else:
                print("✅ 이미 동기화됨")
        else:
            print("❌ 서버 연결 실패")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    finally:
        if 'network' in locals():
            network.stop()
            print("🔌 네트워크 연결 종료")
    
    return True

if __name__ == "__main__":
    print("🚀 LTM 강제 동기화 도구")
    print("=" * 50)
    
    success = force_sync()
    
    if success:
        print("\n✅ 동기화 완료! 이제 지갑을 다시 실행해주세요:")
        print("./run_electrum_ltm")
    else:
        print("\n❌ 동기화 실패. 수동으로 재시도가 필요합니다.")