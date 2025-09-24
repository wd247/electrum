#!/usr/bin/env python3
"""
LTM 프라이빗 노드에서 bc1 주소 잔액 조회
"""

import socket
import json
import hashlib
import sys

def bech32_decode(bech):
    """Bech32 디코딩 (간단한 구현)"""
    CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    
    if bech.find('1') == -1:
        return None, None
        
    hrp = bech[:bech.rfind('1')]
    data = bech[bech.rfind('1')+1:]
    
    decoded = []
    for c in data:
        if c not in CHARSET:
            return None, None
        decoded.append(CHARSET.find(c))
    
    # 5비트 -> 8비트 변환 (간단화)
    converted = []
    acc = 0
    bits = 0
    
    for value in decoded[1:-6]:  # 첫 witness version과 체크섬 제외
        acc = (acc << 5) | value
        bits += 5
        if bits >= 8:
            bits -= 8
            converted.append((acc >> bits) & 255)
    
    return hrp, bytes(converted)

def address_to_scripthash(address):
    """bc1 주소를 ElectrumX 스크립트해시로 변환"""
    try:
        if not address.startswith('bc1q'):
            return None
            
        hrp, data = bech32_decode(address)
        if not data or len(data) != 20:
            print(f"❌ Bech32 디코딩 실패 또는 잘못된 데이터 길이: {len(data) if data else 'None'}")
            return None
            
        # P2WPKH 스크립트: OP_0 (0x00) + PUSH20 (0x14) + 20바이트 해시
        script = bytes([0, 20]) + data
        
        # 스크립트 해시 계산 후 뒤집기 (ElectrumX 형식)
        script_hash = hashlib.sha256(script).digest()
        return script_hash[::-1].hex()
        
    except Exception as e:
        print(f"❌ 스크립트해시 변환 오류: {e}")
        return None

def query_balance(address):
    """LTM 잔액 조회"""
    
    host = "ltm-wallet.gnc.ne.kr" 
    port = 50008
    
    print("🔍 LTM 잔액 조회")
    print("=" * 40)
    print(f"주소: {address}")
    print(f"서버: {host}:{port}")
    
    # 스크립트해시 변환
    scripthash = address_to_scripthash(address)
    if not scripthash:
        print("❌ 스크립트해시 변환 실패")
        return False
    
    print(f"스크립트해시: {scripthash}")
    
    # 잔액 조회 시도
    methods = [
        ("blockchain.scripthash.get_balance", [scripthash]),
        ("blockchain.scripthash.get_history", [scripthash]),
    ]
    
    for method, params in methods:
        print(f"\n🔄 {method} 시도중...")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            
            request = {
                "id": 1,
                "method": method,
                "params": params
            }
            
            request_str = json.dumps(request) + "\n"
            sock.send(request_str.encode())
            
            response = b""
            while True:
                try:
                    chunk = sock.recv(1024)
                    if not chunk:
                        break
                    response += chunk
                    if b"\n" in response:
                        break
                except:
                    break
            
            sock.close()
            
            if response:
                response_str = response.decode().strip()
                data = json.loads(response_str)
                
                if "error" in data:
                    error = data["error"]
                    print(f"   ❌ 오류 {error.get('code', 'N/A')}: {error.get('message', 'Unknown')}")
                    
                elif "result" in data:
                    result = data["result"]
                    print(f"   ✅ 응답 받음: {type(result).__name__}")
                    
                    if method == "blockchain.scripthash.get_balance":
                        if isinstance(result, dict):
                            confirmed = result.get('confirmed', 0)
                            unconfirmed = result.get('unconfirmed', 0)
                            
                            print(f"\n💰 잔액 정보:")
                            print(f"  확정 잔액: {confirmed:,} satoshi")
                            print(f"  미확정 잔액: {unconfirmed:,} satoshi")
                            print(f"  확정 잔액: {confirmed/1e8:.8f} LTM")
                            print(f"  미확정 잔액: {unconfirmed/1e8:.8f} LTM")
                            print(f"  총 잔액: {(confirmed + unconfirmed)/1e8:.8f} LTM")
                            
                            return True
                        else:
                            print(f"   데이터: {result}")
                    
                    elif method == "blockchain.scripthash.get_history":
                        if isinstance(result, list):
                            tx_count = len(result)
                            print(f"   📜 거래 내역: {tx_count}건")
                            
                            if tx_count > 0:
                                print(f"   (이 주소는 활성 상태입니다)")
                                for i, tx in enumerate(result[:5]):  # 최대 5개
                                    tx_hash = tx.get('tx_hash', 'N/A')
                                    height = tx.get('height', 'N/A')
                                    print(f"     {i+1}. {tx_hash[:16]}... (블록: {height})")
                            else:
                                print(f"   (신규 주소 - 거래 내역 없음)")
                        else:
                            print(f"   데이터: {result}")
                
            else:
                print(f"   ❌ 서버 응답 없음")
                
        except Exception as e:
            print(f"   ❌ 연결 오류: {type(e).__name__}: {e}")
    
    return False

def main():
    if len(sys.argv) != 2:
        print("사용법: python3 ltm_balance_proper.py <bc1_주소>")
        print("예시: python3 ltm_balance_proper.py bc1qvhrr2sufl4q0xukh60fa6k7nq4gchjn5tz45da")
        sys.exit(1)
    
    address = sys.argv[1].strip()
    
    if not address.startswith('bc1q'):
        print("❌ bc1q로 시작하는 주소만 지원합니다")
        sys.exit(1)
    
    success = query_balance(address)
    
    if not success:
        print("\n❗ 잔액 조회 실패")
        print("💡 가능한 원인:")
        print("  - 프라이빗 노드 인증 필요")
        print("  - 주소에 거래 내역 없음")
        print("  - 네트워크 연결 문제")

if __name__ == "__main__":
    main()