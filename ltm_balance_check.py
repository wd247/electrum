#!/usr/bin/env python3
"""
LTM 주소 잔액 조회 도구
직접 서버 통신으로 잔액 확인
"""

import socket
import json
import sys

def query_ltm_server(address):
    """LTM 서버에서 주소 잔액 조회"""
    
    print("🔍 LTM 주소 잔액 조회")
    print("=" * 50)
    
    # 주소 검증
    print(f"📍 대상 주소: {address}")
    
    if not address.startswith('bc1'):
        print("❌ bc1 형식이 아닌 주소입니다")
        return False
    
    if len(address) != 42:
        print("⚠️ 비표준 주소 길이입니다")
    
    print("✅ 주소 형식 검증 완료")
    
    # LTM 서버 연결
    server_host = "ltm-wallet.gnc.ne.kr"
    server_port = 50009
    
    print(f"\n🌐 LTM 서버 연결: {server_host}:{server_port}")
    
    try:
        # 소켓 연결
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((server_host, server_port))
        print("✅ 서버 연결 성공")
        
        # Electrum 서버 프로토콜로 잔액 조회
        request = {
            "id": 1,
            "method": "blockchain.address.get_balance",
            "params": [address]
        }
        
        request_str = json.dumps(request) + "\n"
        print(f"📤 요청 전송: {request['method']}")
        
        sock.send(request_str.encode())
        
        # 응답 받기
        response = sock.recv(4096).decode().strip()
        print("📥 서버 응답 수신")
        
        sock.close()
        
        # 응답 파싱
        try:
            response_data = json.loads(response)
            
            if "result" in response_data:
                balance = response_data["result"]
                
                print(f"\n💰 잔액 정보:")
                print(f"  확정된 잔액: {balance.get('confirmed', 0)} satoshi")
                print(f"  미확정 잔액: {balance.get('unconfirmed', 0)} satoshi")
                
                # LTM 단위로 변환 (1 LTM = 100,000,000 satoshi)
                confirmed_ltm = balance.get('confirmed', 0) / 100000000
                unconfirmed_ltm = balance.get('unconfirmed', 0) / 100000000
                
                print(f"  확정된 잔액: {confirmed_ltm:.8f} LTM")
                print(f"  미확정 잔액: {unconfirmed_ltm:.8f} LTM")
                
                total_ltm = confirmed_ltm + unconfirmed_ltm
                print(f"  총 잔액: {total_ltm:.8f} LTM")
                
                return True
                
            elif "error" in response_data:
                error = response_data["error"]
                print(f"❌ 서버 오류: {error}")
                return False
            else:
                print(f"⚠️ 예상치 못한 응답: {response}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ 응답 파싱 오류: {e}")
            print(f"Raw 응답: {response}")
            return False
            
    except socket.timeout:
        print("❌ 서버 연결 타임아웃")
        return False
    except ConnectionRefused:
        print("❌ 서버 연결 거부됨")
        return False
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("사용법: python3 ltm_balance_check.py <주소>")
        print("예시: python3 ltm_balance_check.py bc1qvhrr2sufl4q0xukh60fa6k7nq4gchjn5tz45da")
        sys.exit(1)
    
    address = sys.argv[1]
    success = query_ltm_server(address)
    
    if not success:
        print("\n💡 참고사항:")
        print("  - LTM 서버가 온라인인지 확인하세요")
        print("  - 주소가 올바른 형식인지 확인하세요")
        print("  - 네트워크 연결 상태를 확인하세요")
        sys.exit(1)

if __name__ == "__main__":
    main()