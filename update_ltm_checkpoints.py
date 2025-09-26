#!/usr/bin/env python3

import socket
import json
import struct

def get_block_header(host, port, height):
    """블록 헤더 가져오기"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        # 블록 헤더 요청
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
        if 'result' in data:
            return data['result']
        return None
        
    except Exception as e:
        print(f"오류: {e}")
        return None

def calculate_hash(hex_header):
    """블록 해시 계산 (SHA-256d)"""
    import hashlib
    
    header_bytes = bytes.fromhex(hex_header)
    hash1 = hashlib.sha256(header_bytes).digest()
    hash2 = hashlib.sha256(hash1).digest()
    # 리틀 엔디안으로 변환
    return hash2[::-1].hex()

def update_checkpoints():
    """체크포인트 업데이트"""
    server_host = "ltm-wallet.gnc.ne.kr"
    server_port = 50008
    
    # 업데이트할 블록 높이들 (더 최근으로)
    heights = [0, 10000, 15000, 20000, 22000, 22500, 22800, 22850, 22890, 22895]
    
    checkpoints = {}
    
    for height in heights:
        print(f"블록 {height} 처리 중...")
        header = get_block_header(server_host, server_port, height)
        
        if header:
            block_hash = calculate_hash(header)
            checkpoints[str(height)] = block_hash
            print(f"  -> {block_hash}")
        else:
            print(f"  -> 실패")
    
    # 체크포인트 파일 업데이트
    checkpoint_file = "/home/junny/electrum/electrum/chains/ltm/checkpoints.json"
    
    try:
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoints, f, indent=2)
        
        print(f"\n✅ 체크포인트 파일 업데이트 완료: {len(checkpoints)}개 블록")
        print(f"파일: {checkpoint_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 파일 저장 실패: {e}")
        return False

if __name__ == "__main__":
    print("🔄 LTM 체크포인트 업데이트")
    print("=" * 40)
    
    if update_checkpoints():
        print("\n✅ 체크포인트 업데이트 완료!")
        print("이제 Electrum을 재시작해주세요.")
    else:
        print("\n❌ 체크포인트 업데이트 실패")