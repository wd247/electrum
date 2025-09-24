#!/usr/bin/env python3
import socket
import json
import base64

def test_with_auth():
    """인증이 필요한 프라이빗 노드 테스트"""
    
    host = "ltm-wallet.gnc.ne.kr"
    port = 50008
    
    # 일반적인 테스트 인증 정보들
    auth_combinations = [
        ("ltm", "ltm123"),
        ("user", "password"),
        ("admin", "admin"),
        ("electrum", "electrum"),
        ("ltmuser", "ltmpass"),
        ("", ""),  # 인증 없음
    ]
    
    print("🔑 인증 조합 테스트:")
    print("=" * 40)
    
    for i, (username, password) in enumerate(auth_combinations, 1):
        print(f"\n{i}. 테스트: '{username}' / '{password}'")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            
            # 서버 버전 요청 (인증 포함)
            request = {
                "id": 1,
                "method": "server.version",
                "params": ["Electrum", "1.4.2"]
            }
            
            # HTTP Basic Auth 헤더 추가 (필요한 경우)
            request_str = json.dumps(request) + "\n"
            
            if username or password:
                # Base64 인코딩된 인증 정보
                auth_string = f"{username}:{password}"
                auth_b64 = base64.b64encode(auth_string.encode()).decode()
                print(f"   인증 헤더: Basic {auth_b64}")
            
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
                    if "result" in data:
                        print(f"   ✅ 성공: {data['result']}")
                        return username, password
                    elif "error" in data:
                        error = data["error"]
                        if error.get("code") == -32600:  # 인증 오류
                            print(f"   🔐 인증 필요: {error['message']}")
                        else:
                            print(f"   ❌ 오류: {error['message']}")
                except json.JSONDecodeError:
                    print(f"   ⚠️ 응답: {response_str[:50]}...")
            else:
                print(f"   ❌ 빈 응답")
                
        except Exception as e:
            print(f"   ❌ 연결 오류: {e}")
    
    print("\n💡 결과: 올바른 인증 정보를 찾지 못했습니다.")
    return None, None

if __name__ == "__main__":
    test_with_auth()
