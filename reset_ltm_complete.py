#!/usr/bin/env python3

import socket
import json
import os

def get_latest_checkpoints():
    """최신 체크포인트 가져오기"""
    server_host = "ltm-wallet.gnc.ne.kr"
    server_port = 50008
    
    def get_block_header(height):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((server_host, server_port))
            
            request = {
                "jsonrpc": "2.0",
                "method": "blockchain.block.header",
                "params": [height],
                "id": 1
            }
            
            message = json.dumps(request) + '\n'
            sock.send(message.encode())
            
            response = sock.recv(4096).decode().strip()
            sock.close()
            
            data = json.loads(response)
            return data.get('result')
        except:
            return None
    
    def calculate_hash(hex_header):
        import hashlib
        header_bytes = bytes.fromhex(hex_header)
        hash1 = hashlib.sha256(header_bytes).digest()
        hash2 = hashlib.sha256(hash1).digest()
        return hash2[::-1].hex()
    
    # 최신 블록까지의 체크포인트
    heights = [0, 5000, 10000, 15000, 18000, 20000, 21000, 22000, 22500, 22800, 22900, 22905]
    
    checkpoints = {}
    
    for height in heights:
        print(f"블록 {height} 처리 중...")
        header = get_block_header(height)
        
        if header:
            block_hash = calculate_hash(header)
            checkpoints[str(height)] = block_hash
            print(f"  ✅ {block_hash}")
        else:
            print(f"  ❌ 실패")
    
    return checkpoints

def create_ltm_dirs():
    """LTM 디렉토리 구조 생성"""
    ltm_dir = os.path.expanduser("~/.electrum/ltm")
    chains_dir = "/home/junny/electrum/electrum/chains/ltm"
    
    os.makedirs(ltm_dir, exist_ok=True)
    os.makedirs(chains_dir, exist_ok=True)
    
    print(f"✅ 디렉토리 생성: {ltm_dir}")
    print(f"✅ 디렉토리 확인: {chains_dir}")

if __name__ == "__main__":
    print("🔧 LTM 완전 재초기화")
    print("=" * 40)
    
    # 1. 디렉토리 생성
    create_ltm_dirs()
    
    # 2. 최신 체크포인트 가져오기
    print("\n📍 최신 체크포인트 생성...")
    checkpoints = get_latest_checkpoints()
    
    # 3. 체크포인트 파일 저장
    checkpoint_file = "/home/junny/electrum/electrum/chains/ltm/checkpoints.json"
    
    try:
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoints, f, indent=2)
        
        print(f"\n✅ 체크포인트 파일 생성: {len(checkpoints)}개 블록")
        print(f"파일: {checkpoint_file}")
        print("\n✅ 재초기화 완료! 이제 GUI를 시작할 수 있습니다.")
        
    except Exception as e:
        print(f"❌ 파일 저장 실패: {e}")