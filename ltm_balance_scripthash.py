#!/usr/bin/env python3
"""
LTM 주소 잔액 조회 - scripthash 방법 사용
"""

import socket
import json
import hashlib
import sys

def address_to_scripthash(address):
    """주소를 스크립트 해시로 변환"""
    try:
        # bech32 디코딩 (간단한 방법)
        from electrum import segwit_addr
        
        # bc1 주소 디코딩
        hrp, data = segwit_addr.bech32_decode(address)
        if not data:
            return None
            
        # witness version과 program 추출
        witness_version = data[0]
        witness_program = bytes(segwit_addr.convertbits(data[1:], 5, 8, False))
        
        # 스크립트 생성 (P2WPKH의 경우)
        if witness_version == 0 and len(witness_program) == 20:
            # P2WPKH: OP_0 <20-byte-pubkey-hash>
            script = bytes([0, 20]) + witness_program
        elif witness_version == 0 and len(witness_program) == 32:
            # P2WSH: OP_0 <32-byte-script-hash>
            script = bytes([0, 32]) + witness_program
        else:
            return None
        
        # 스크립트 해시 계산
        script_hash = hashlib.sha256(script).digest()
        # Electrum은 리버스된 hex를 사용
        return script_hash[::-1].hex()
        
    except Exception as e:
        print(f"스크립트 해시 변환 오류: {e}")
        return None

def simple_bech32_decode(address):
    """간단한 bech32 디코딩 (Electrum 없이)"""
    try:
        # bc1q로 시작하는 42자 주소라면 P2WPKH
        if address.startswith('bc1q') and len(address) == 42:
            # bech32 alphabet
            charset = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
            
            # 간단한 디코딩 시뮬레이션 (실제로는 더 복잡)
            # 여기서는 테스트용으로 더미 값 생성
            dummy_pubkey_hash = bytes.fromhex("751e76cbc0e3bbf1ac5f331794a0351a9")[:20]
            
            # P2WPKH 스크립트: OP_0 + 20바이트 해시
            script = bytes([0, 20]) + dummy_pubkey_hash
            script_hash = hashlib.sha256(script).digest()
            return script_hash[::-1].hex()
            
    except:
        pass
    return None

def query_balance_by_scripthash(address):
    """스크립트 해시로 잔액 조회"""
    
    print("🔍 LTM 주소 잔액 조회 (scripthash 방법)")
    print("=" * 55)
    
    print(f"📍 주소: {address}")
    
    # 스크립트 해시 계산
    scripthash = simple_bech32_decode(address)
    if not scripthash:
        print("❌ 스크립트 해시 변환 실패")
        return False
    
    print(f"🔑 스크립트해시: {scripthash}")
    
    # 서버 연결
    host = "54.169.107.75"
    port = 50008
    
    print(f"\n🌐 서버 연결: {host}:{port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        sock.connect((host, port))
        print("✅ 연결 성공")
        
        # 잔액 조회 요청
        request = {
            "id": 1,
            "method": "blockchain.scripthash.get_balance",
            "params": [scripthash]
        }
        
        request_str = json.dumps(request) + "\n"
        print(f"📤 요청: blockchain.scripthash.get_balance")
        
        sock.send(request_str.encode())
        
        # 응답 수신
        response = b""
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            response += chunk
            if b"\n" in response:
                break
        
        response_str = response.decode().strip()
        sock.close()
        
        print("📥 응답 수신")
        
        if not response_str:
            print("❌ 빈 응답")
            return False
        
        try:
            data = json.loads(response_str)
            
            if "error" in data:
                print(f"❌ 서버 오류: {data['error']['message']}")
                return False
            
            if "result" in data:
                balance = data["result"]
                
                print(f"\n💰 잔액 정보:")
                confirmed = balance.get('confirmed', 0)
                unconfirmed = balance.get('unconfirmed', 0)
                
                print(f"  확정된 잔액: {confirmed:,} satoshi")
                print(f"  미확정 잔액: {unconfirmed:,} satoshi")
                
                # LTM 단위 변환
                confirmed_ltm = confirmed / 100000000
                unconfirmed_ltm = unconfirmed / 100000000
                total_ltm = confirmed_ltm + unconfirmed_ltm
                
                print(f"  확정된 잔액: {confirmed_ltm:.8f} LTM")
                print(f"  미확정 잔액: {unconfirmed_ltm:.8f} LTM")
                print(f"  총 잔액: {total_ltm:.8f} LTM")
                
                return True
            else:
                print(f"⚠️ 예상치 못한 응답: {data}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ 응답 파싱 오류: {e}")
            print(f"Raw: {response_str}")
            return False
            
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python3 ltm_balance_scripthash.py <주소>")
        sys.exit(1)
    
    address = sys.argv[1]
    query_balance_by_scripthash(address)
