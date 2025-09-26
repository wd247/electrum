#!/usr/bin/env python3
"""
LTM 주소 잔액 조회 - 최종 버전
ltm-wallet.gnc.ne.kr:50008 사용
"""

import socket
import json
import sys

def test_server_methods():
    """서버 지원 메서드 확인"""
    
    host = "ltm-wallet.gnc.ne.kr"
    port = 50008
    
    print(f"🔍 서버 메서드 테스트: {host}:{port}")
    print("=" * 50)
    
    # 서버 정보 조회
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        
        request = {
            "id": 1,
            "method": "server.version",
            "params": ["Electrum", "1.4.2"]
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
            data = json.loads(response_str)
            if "result" in data:
                server_info = data["result"]
                print(f"✅ 서버 정보: {server_info}")
                return True
            else:
                print(f"❌ 서버 오류: {data.get('error', '알 수 없음')}")
        else:
            print("❌ 빈 응답")
            
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
    
    return False

def query_address_balance(address):
    """주소 잔액 조회"""
    
    host = "ltm-wallet.gnc.ne.kr"
    port = 50008
    
    print(f"\n💰 주소 잔액 조회")
    print(f"주소: {address}")
    print(f"서버: {host}:{port}")
    
    # 다양한 메서드 시도
    methods_to_try = [
        ("blockchain.address.get_balance", [address]),
        ("blockchain.address.get_history", [address]),
        ("blockchain.address.listunspent", [address])
    ]
    
    for method, params in methods_to_try:
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
                        
                        if method == "blockchain.address.get_balance":
                            confirmed = result.get('confirmed', 0)
                            unconfirmed = result.get('unconfirmed', 0)
                            
                            print(f"   💰 잔액:")
                            print(f"     확정: {confirmed:,} satoshi ({confirmed/1e8:.8f} LTM)")
                            print(f"     미확정: {unconfirmed:,} satoshi ({unconfirmed/1e8:.8f} LTM)")
                            print(f"     총계: {(confirmed+unconfirmed)/1e8:.8f} LTM")
                            return True
                            
                        elif method == "blockchain.address.get_history":
                            tx_count = len(result) if isinstance(result, list) else 0
                            print(f"   📜 거래 내역: {tx_count}건")
                            if tx_count > 0:
                                print("   (거래가 있는 주소입니다)")
                            else:
                                print("   (거래 내역이 없는 주소입니다)")
                                
                        elif method == "blockchain.address.listunspent":
                            utxo_count = len(result) if isinstance(result, list) else 0
                            print(f"   💎 UTXO: {utxo_count}개")
                            
                            if utxo_count > 0:
                                total_value = sum(utxo.get('value', 0) for utxo in result)
                                print(f"   💰 총 잔액: {total_value:,} satoshi ({total_value/1e8:.8f} LTM)")
                                return True
                        
                        print(f"   상세 결과: {str(result)[:200]}...")
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON 파싱 오류: {e}")
            else:
                print("   ❌ 빈 응답")
                
        except Exception as e:
            print(f"   ❌ 연결 오류: {e}")
    
    return False

def main():
    if len(sys.argv) != 2:
        print("사용법: python3 ltm_balance_final.py <주소>")
        print("예시: python3 ltm_balance_final.py bc1qvhrr2sufl4q0xukh60fa6k7nq4gchjn5tz45da")
        sys.exit(1)
    
    address = sys.argv[1]
    
    print("🚀 LTM 주소 잔액 조회 (최종 버전)")
    print("=" * 55)
    
    # 서버 상태 확인
    if not test_server_methods():
        print("\n❌ 서버 연결 실패")
        sys.exit(1)
    
    # 주소 잔액 조회
    success = query_address_balance(address)
    
    if not success:
        print(f"\n⚠️ 모든 방법으로 잔액 조회에 실패했습니다")
        print("💡 가능한 원인:")
        print("  - 주소에 거래 내역이 없음")
        print("  - 서버 프로토콜 버전 불일치")
        print("  - LTM 네트워크 특화 설정 필요")

if __name__ == "__main__":
    main()
