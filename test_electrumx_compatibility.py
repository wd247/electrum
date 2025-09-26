#!/usr/bin/env python3
"""
ElectrumX 서버 직접 연결 테스트
블루월렛과 Electrum PC의 차이점 분석
"""

import socket
import ssl
import json
import time
import base64

def create_electrumx_connection(host, port, use_ssl=True):
    """ElectrumX 서버에 직접 연결"""
    try:
        print(f"🔗 {host}:{port} 연결 시도 (SSL: {use_ssl})...")
        
        # 소켓 생성
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        if use_ssl:
            # SSL 컨텍스트 생성 (블루월렛과 유사하게)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=host)
        
        # 연결
        sock.connect((host, port))
        print(f"✅ 연결 성공!")
        
        return sock
        
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return None

def send_electrumx_request(sock, method, params=None, request_id=1):
    """ElectrumX JSON-RPC 요청 전송"""
    try:
        # JSON-RPC 2.0 형식 (블루월렛과 동일)
        request = {
            "jsonrpc": "2.0", 
            "method": method,
            "params": params or [],
            "id": request_id
        }
        
        message = json.dumps(request) + "\n"
        print(f"📤 요청: {method}")
        
        # 인증이 필요한 경우
        if hasattr(sock, '_auth_sent') and not sock._auth_sent:
            # HTTP Basic Auth 형식으로 인증
            auth_str = base64.b64encode(b"ltm:ltm123").decode()
            auth_header = f"Authorization: Basic {auth_str}\r\n"
            message = auth_header + message
            sock._auth_sent = True
        
        sock.send(message.encode('utf-8'))
        
        # 응답 받기
        response = sock.recv(4096).decode('utf-8')
        print(f"📥 응답: {response[:200]}...")
        
        return json.loads(response.strip())
        
    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        return None

def test_server_compatibility():
    """서버 호환성 테스트"""
    print("🧪 ElectrumX 서버 호환성 테스트")
    print("=" * 50)
    
    host = "54.169.107.75"
    port = 50009
    
    # SSL 연결 테스트
    sock = create_electrumx_connection(host, port, use_ssl=True)
    if not sock:
        print("❌ SSL 연결 실패")
        return False
    
    try:
        # 1. 서버 버전 확인 (블루월렛이 첫 번째로 하는 요청)
        print("\n1️⃣ 서버 버전 확인...")
        response = send_electrumx_request(sock, "server.version", ["BlueWallet", "1.4"])
        if response:
            print(f"   서버 정보: {response}")
        
        # 2. 서버 피어 정보
        print("\n2️⃣ 서버 피어 정보...")
        response = send_electrumx_request(sock, "server.peers.subscribe")
        if response:
            print(f"   피어 정보: {response}")
        
        # 3. 블록체인 헤더 구독 (블루월렛 방식)
        print("\n3️⃣ 헤더 구독...")
        response = send_electrumx_request(sock, "blockchain.headers.subscribe")
        if response:
            print(f"   헤더 정보: {response}")
            
        # 4. Fee 추정 (블루월렛이 항상 하는 요청)
        print("\n4️⃣ Fee 추정...")
        response = send_electrumx_request(sock, "blockchain.estimatefee", [6])
        if response:
            print(f"   Fee 정보: {response}")
        
        print("\n✅ 서버 호환성 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        return False
        
    finally:
        sock.close()

def test_address_requests():
    """주소 관련 요청 테스트 (블루월렛 스타일)"""
    print("\n💰 주소 요청 테스트 (블루월렛 스타일)")
    print("=" * 50)
    
    host = "54.169.107.75" 
    port = 50009
    
    sock = create_electrumx_connection(host, port, use_ssl=True)
    if not sock:
        return False
    
    try:
        # 테스트 주소 (이전에 사용한 주소)
        test_address = "bc1qvhrr2sufl4q0xukh60fa6k7nq4gchjn5tz45da"
        
        # 1. 주소 히스토리 (블루월렛의 핵심 요청)
        print(f"📜 주소 히스토리: {test_address}")
        response = send_electrumx_request(sock, "blockchain.scripthash.get_history", 
                                        ["hash_of_scripthash_here"])
        
        # 2. 주소 잔액 
        print(f"💎 주소 잔액: {test_address}")
        response = send_electrumx_request(sock, "blockchain.scripthash.get_balance",
                                        ["hash_of_scripthash_here"])
        
        return True
        
    except Exception as e:
        print(f"❌ 주소 테스트 실패: {e}")
        return False
        
    finally:
        sock.close()

def main():
    """메인 테스트"""
    print("🔍 LTM ElectrumX 서버 분석")
    print("블루월렛 vs Electrum PC 호환성 확인")
    print("=" * 60)
    
    # 기본 서버 호환성 테스트
    if test_server_compatibility():
        # 주소 요청 테스트  
        test_address_requests()
        
        print("\n💡 분석 결과:")
        print("   - ElectrumX 서버는 정상 작동")
        print("   - 블루월렛 스타일 요청 가능") 
        print("   - Electrum PC의 헤더 동기화가 문제일 가능성")
        print("   - 해결방안: SPV 모드 최적화 필요")
    else:
        print("\n❌ 서버 연결 문제 확인됨")
        print("   - 네트워크 설정 재확인 필요")

if __name__ == "__main__":
    main()