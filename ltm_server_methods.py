#!/usr/bin/env python3
import socket
import json

def test_ltm_methods(address):
    host = "54.169.107.75"
    port = 50008
    
    methods_to_try = [
        ("server.version", ["Electrum", "1.4.2"]),
        ("server.features", []),
        ("blockchain.scripthash.get_balance", []),  # 이 방법을 시도해야 할 수도
        ("blockchain.address.get_balance", [address]),
        ("blockchain.address.get_history", [address]),
        ("blockchain.estimatefee", [1]),
        ("blockchain.block.header", [0])
    ]
    
    print(f"🔍 LTM 서버 메서드 테스트: {host}:{port}")
    print("=" * 60)
    
    for i, (method, params) in enumerate(methods_to_try, 1):
        print(f"\n{i}. 테스트 메서드: {method}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            
            request = {
                "id": i,
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
                        print(f"   ❌ 오류: {data['error']['message']}")
                    else:
                        print(f"   ✅ 성공: {str(data['result'])[:100]}")
                except:
                    print(f"   ⚠️ 응답: {response_str[:100]}")
            else:
                print("   ❌ 빈 응답")
                
        except Exception as e:
            print(f"   ❌ 연결 오류: {e}")

if __name__ == "__main__":
    test_ltm_methods("bc1qvhrr2sufl4q0xukh60fa6k7nq4gchjn5tz45da")
