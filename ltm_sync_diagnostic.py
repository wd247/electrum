#!/usr/bin/env python3
"""
LTM 네트워크 동기화 및 서버 상태 진단 도구
"""

import socket
import json
import sys
import time

def test_server_connection(host, port):
    """서버 연결 및 기본 정보 테스트"""
    
    print(f"🔍 서버 테스트: {host}:{port}")
    print("-" * 40)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        # 1. 서버 버전 확인
        request = json.dumps({
            'id': 1, 
            'method': 'server.version',
            'params': ['Electrum-LTM', '1.4']
        }) + '\n'
        
        sock.send(request.encode())
        response = sock.recv(4096).decode().strip()
        
        data = json.loads(response)
        if 'result' in data:
            server_version, protocol_version = data['result']
            print(f"✅ 서버 버전: {server_version}")
            print(f"✅ 프로토콜: {protocol_version}")
        
        # 2. 현재 블록 높이 확인
        request = json.dumps({
            'id': 2, 
            'method': 'blockchain.headers.subscribe',
            'params': []
        }) + '\n'
        
        sock.send(request.encode())
        response = sock.recv(4096).decode().strip()
        
        data = json.loads(response)
        if 'result' in data:
            result = data['result']
            height = result.get('height', 'N/A')
            print(f"✅ 현재 블록: {height}")
            
        # 3. 서버 피어 수 확인
        request = json.dumps({
            'id': 3, 
            'method': 'server.peers.subscribe',
            'params': []
        }) + '\n'
        
        sock.send(request.encode())
        response = sock.recv(4096).decode().strip()
        
        data = json.loads(response)
        if 'result' in data:
            peers = data['result']
            print(f"✅ 연결된 피어: {len(peers)}개")
            
        sock.close()
        return True
        
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False

def get_blockchain_status():
    """블록체인 상태 확인"""
    
    host = "ltm-wallet.gnc.ne.kr"
    port = 50008
    
    print(f"\n📊 LTM 블록체인 상태")
    print("=" * 50)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        # 현재 헤더 정보
        request = json.dumps({
            'id': 1, 
            'method': 'blockchain.headers.subscribe',
            'params': []
        }) + '\n'
        
        sock.send(request.encode())
        response = sock.recv(4096).decode().strip()
        
        data = json.loads(response)
        if 'result' in data:
            result = data['result']
            height = result.get('height', 0)
            hex_header = result.get('hex', '')
            
            print(f"현재 블록 높이: {height}")
            print(f"헤더 길이: {len(hex_header)} bytes")
            
            # 헤더 파싱 (간단한 정보)
            if hex_header:
                header_bytes = bytes.fromhex(hex_header)
                version = int.from_bytes(header_bytes[0:4], 'little')
                timestamp = int.from_bytes(header_bytes[68:72], 'little')
                
                print(f"블록 버전: {version}")
                print(f"타임스탬프: {timestamp}")
                
                import datetime
                dt = datetime.datetime.fromtimestamp(timestamp)
                print(f"블록 시간: {dt}")
                
        sock.close()
        
    except Exception as e:
        print(f"❌ 블록체인 상태 확인 실패: {e}")

def test_sync_issue():
    """동기화 문제 진단"""
    
    print(f"\n🔧 동기화 문제 진단")
    print("=" * 30)
    
    # 1. 서버 목록 테스트
    servers = [
        ("ltm-wallet.gnc.ne.kr", 50008),
        ("54.169.107.75", 50008),
    ]
    
    for host, port in servers:
        success = test_server_connection(host, port)
        if success:
            print(f"✅ {host}:{port} - 정상")
        else:
            print(f"❌ {host}:{port} - 실패")
        print()
    
    # 2. 블록체인 상태
    get_blockchain_status()
    
    # 3. 권장사항
    print(f"\n💡 동기화 개선 권장사항:")
    print("1. 지갑 재시작: ./run_electrum_ltm")
    print("2. 서버 변경: 설정 > 네트워크 > 서버")
    print("3. 체크포인트 업데이트 완료 (22890블록까지)")
    print("4. 캐시 삭제: ~/.electrum/ltm/ 폴더 삭제 후 재시작")

def main():
    print("🚀 LTM 네트워크 진단 도구")
    print("=" * 40)
    
    test_sync_issue()

if __name__ == "__main__":
    main()