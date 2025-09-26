#!/usr/bin/env python3
"""
LTM 주소 잔액 조회 도구 v2
새로운 서버 54.169.107.75:50008 사용
"""

import socket
import json
import sys

def query_ltm_server_v2(address):
    """새로운 LTM 서버에서 주소 잔액 조회"""
    
    print("🔍 LTM 주소 잔액 조회 v2")
    print("=" * 50)
    
    # 주소 검증
    print(f"📍 대상 주소: {address}")
    
    if not address.startswith('bc1'):
        print("❌ bc1 형식이 아닌 주소입니다")
        return False
    
    print("✅ 주소 형식 검증 완료")
    
    # 새로운 LTM 서버 연결
    server_host = "54.169.107.75"
    server_port = 50008
    
    print(f"\n🌐 LTM 서버 연결: {server_host}:{server_port}")
    
    try:
        # 소켓 연결
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
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
        print(f"   요청 내용: {request_str.strip()}")
        
        sock.send(request_str.encode())
        
        # 응답 받기 (더 많은 데이터 수신)
        response = b""
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            response += chunk
            if b"\n" in response:
                break
        
        response_str = response.decode().strip()
        print("📥 서버 응답 수신")
        print(f"   응답 길이: {len(response_str)} 바이트")
        
        if response_str:
            print(f"   Raw 응답: {response_str[:200]}...")
        else:
            print("   빈 응답")
        
        sock.close()
        
        # 응답 파싱
        if not response_str:
            print("❌ 서버에서 빈 응답을 받았습니다")
            return False
            
        try:
            response_data = json.loads(response_str)
            
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
                print(f"⚠️ 예상치 못한 응답 구조: {response_data}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ 응답 파싱 오류: {e}")
            print(f"   Raw 응답: {response_str}")
            
            # 다른 명령어도 시도해보기
            print("\n🔄 다른 방법 시도...")
            return try_alternative_method(server_host, server_port, address)
            
    except socket.timeout:
        print("❌ 서버 연결 타임아웃")
        return False
    except ConnectionRefused:
        print("❌ 서버 연결 거부됨")
        return False
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return False

def try_alternative_method(host, port, address):
    """대안 방법으로 서버 통신 시도"""
    
    print("🔄 대안 방법: 서버 정보 먼저 조회")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        # 서버 정보 조회
        request = {
            "id": 1,
            "method": "server.version",
            "params": ["Electrum", "1.4.2"]
        }
        
        request_str = json.dumps(request) + "\n"
        print(f"📤 서버 버전 조회: {request_str.strip()}")
        
        sock.send(request_str.encode())
        response = sock.recv(4096).decode().strip()
        sock.close()
        
        print(f"📥 서버 정보: {response}")
        
        if response and response != "":
            print("✅ 서버 통신 가능, 프로토콜 호환 문제일 수 있음")
        else:
            print("❌ 서버 통신 불가")
            
        return False
        
    except Exception as e:
        print(f"❌ 대안 방법 실패: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("사용법: python3 ltm_balance_check_v2.py <주소>")
        print("예시: python3 ltm_balance_check_v2.py bc1qvhrr2sufl4q0xukh60fa6k7nq4gchjn5tz45da")
        sys.exit(1)
    
    address = sys.argv[1]
    success = query_ltm_server_v2(address)
    
    if not success:
        print("\n💡 참고사항:")
        print("  - LTM 서버: 54.169.107.75:50008")
        print("  - Electrum 프로토콜 버전 확인 필요")
        print("  - 서버 설정 변경 가능성 확인")
        sys.exit(1)

if __name__ == "__main__":
    main()
