#!/usr/bin/env python3

import socket
import json
import os

def get_correct_checkpoints():
    """올바른 현재 블록 높이로 체크포인트 생성"""
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
    
    # 현재 블록 22930 기준으로 올바른 체크포인트 생성
    heights = [0, 5000, 10000, 15000, 20000, 22000, 22500, 22800, 22900, 22920, 22925]
    
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

def setup_ltm_with_auth():
    """LTM 설정을 올바른 인증과 체크포인트로 초기화"""
    
    # 1. 디렉토리 생성
    ltm_dir = os.path.expanduser("~/.electrum/ltm")
    chains_dir = "/home/junny/electrum/electrum/chains/ltm"
    
    os.makedirs(ltm_dir, exist_ok=True)
    os.makedirs(chains_dir, exist_ok=True)
    
    print(f"✅ 디렉토리 생성: {ltm_dir}")
    
    # 2. 올바른 체크포인트 생성
    print("\n📍 올바른 체크포인트 생성...")
    checkpoints = get_correct_checkpoints()
    
    # 3. 체크포인트 파일 저장
    checkpoint_file = f"{chains_dir}/checkpoints.json"
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoints, f, indent=2)
    
    print(f"\n✅ 체크포인트 파일 저장: {len(checkpoints)}개")
    
    # 4. 올바른 설정 파일 생성 (ltm/ltm123 인증 포함)
    config = {
        "auto_connect": True,
        "chain": "ltm",
        "server": "ltm:ltm123@ltm-wallet.gnc.ne.kr:50008:t",
        "server_auth": {
            "ltm-wallet.gnc.ne.kr:50008": {
                "username": "ltm",
                "password": "ltm123"
            }
        },
        "oneserver": False,
        "proxy": None,
        "terms_of_use_accepted": 1
    }
    
    config_file = f"{ltm_dir}/config"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"✅ 설정 파일 생성: ltm/ltm123 인증")
    
    return True

if __name__ == "__main__":
    print("🔧 LTM 완전 올바른 초기화")
    print("=" * 40)
    
    if setup_ltm_with_auth():
        print("\n✅ 완전한 초기화 완료!")
        print("📋 설정된 내용:")
        print("  - 인증: ltm/ltm123")
        print("  - 서버: ltm-wallet.gnc.ne.kr:50008 (TCP)")
        print("  - 체크포인트: 현재 블록 22930 기준")
        print("\n🚀 이제 GUI를 시작할 수 있습니다!")
    else:
        print("\n❌ 초기화 실패")