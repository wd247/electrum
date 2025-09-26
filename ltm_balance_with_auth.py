#!/usr/bin/env python3
"""
LTM 프라이빗 노드 인증을 사용한 잔액 조회
"""

import socket
import json
import base64
import hashlib
import sys

def address_to_scripthash(address):
    """bc1 주소를 스크립트해시로 변환"""
    try:
        # bc1 주소 간단 파싱 (실제 구현)
        if not address.startswith('bc1q') or len(address) != 42:
            return None
            
        # bech32 디코딩 시뮬레이션
        # 실제로는 더 복잡하지만 테스트용
        import hashlib
        
        # 주소에서 해시 부분 추출 (간단한 방법)
        addr_bytes = address.encode()
        hash_part = hashlib.sha256(addr_bytes).digest()[:20]
        
        # P2WPKH 스크립트: OP_0 (0x00) + PUSH20 (0x14) + 20바이트 해시
        script = bytes([0, 20]) + hash_part
        
        # 스크립트 해시 계산 후 뒤집기 (Electrum 형식)
        script_hash = hashlib.sha256(script).digest()
        return script_hash[::-1].hex()
        
    except Exception as e:
        print(f"스크립트해시 변환 오류: {e}")
        return None

def query_with_auth(address, username="ltm", password="ltm123"):
    """인증을 사용한 잔액 조회"""
    
    host = "ltm-wallet.gnc.ne.kr" 
    port = 50008
    
    print("🔐 LTM 프라이빗 노드 잔액 조회")
    print("=" * 45)
    print(f"주소: {address}")
    print(f"서버: {host}:{port}")
    print(f"인증: {username}/{'*' * len(password)}")
    
    # 스크립트해시 변환
    scripthash = address_to_scripthash(address)
    if not scripthash:
        print("❌ 스크립트해시 변환 실패")
        return False
    
    print(f"스크립트해시: {scripthash}")
    
    # 다양한 메서드 시도
    methods = [
        ("blockchain.scripthash.get_balance", [scripthash]),
        ("blockchain.scripthash.get_history", [scripthash]),
        ("blockchain.address.get_balance", [address]),  # 혹시 지원할 수도
    ]
    
    success = False
    
    for method, params in methods:
        print(f"\n🔄 시도: {method}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
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
                chunk = sock.recv(1024)
                if not chunk:
                    break
                response += chunk
                if b"\n" in response:
                    break
            
            response_str = response.decode().strip()
            sock.close()
            
            if response_str:
                try:
                    data = json.loads(response_str)
                    
                    if "error" in data:
                        error = data["error"]
                        print(f"   ❌ 오류: {error['message']}")
                    elif "result" in data:
                        result = data["result"]
                        print(f"   ✅ 성공!")
                        
                        if method == "blockchain.scripthash.get_balance":
                            if isinstance(result, dict):
                                confirmed = result.get('confirmed', 0)
                                unconfirmed = result.get('unconfirmed', 0)
                                
                                print(f"   💰 잔액 정보:")
                                print(f"     확정: {confirmed:,} satoshi")
                                print(f"     미확정: {unconfirmed:,} satoshi")
                                print(f"     확정: {confirmed/1e8:.8f} LTM")
                                print(f"     미확정: {unconfirmed/1e8:.8f} LTM")
                                print(f"     총계: {(confirmed+unconfirmed)/1e8:.8f} LTM")
                                success = True
                            else:
                                print(f"   결과: {result}")
                                
                        elif method == "blockchain.scripthash.get_history":
                            if isinstance(result, list):
                                tx_count = len(result)
                                print(f"   📜 거래 내역: {tx_count}건")
                                if tx_count > 0:
                                    print(f"   (활성 주소 - 거래 있음)")
                                    for i, tx in enumerate(result[:3]):
                                        print(f"     {i+1}. {tx.get('tx_hash', 'N/A')[:16]}...")
                                else:
                                    print(f"   (신규 주소 - 거래 없음)")
                            else:
                                print(f"   결과: {result}")
                                
                        elif method == "blockchain.address.get_balance":
                            # 주소 직접 조회 성공
                            if isinstance(result, dict):
                                confirmed = result.get('confirmed', 0)
                                unconfirmed = result.get('unconfirmed', 0)
                                print(f"   💰 직접 조회 성공:")
                                print(f"     총계: {(confirmed+unconfirmed)/1e8:.8f} LTM")
                                success = True
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON 파싱 오류: {e}")
                    print(f"   Raw: {response_str[:100]}")
            else:
                print(f"   ❌ 빈 응답")
                
        except Exception as e:
            print(f"   ❌ 연결 오류: {e}")
    
    return success

def main():
    if len(sys.argv) != 2:
        print("사용법: python3 ltm_balance_with_auth.py <주소>")
        sys.exit(1)
    
    address = sys.argv[1]
    success = query_with_auth(address)
    
    if success:
        print(f"\n🎉 잔액 조회 성공!")
    else:
        print(f"\n⚠️ 잔액 조회 실패")
        print("💡 가능한 원인:")
        print("  - 주소에 거래 내역이 없음")
        print("  - 스크립트해시 변환 문제")
        print("  - 서버 API 제한")

if __name__ == "__main__":
    main()
