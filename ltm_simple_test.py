#!/usr/bin/env python3
"""
LTM 코인 단순 테스트
Electrum 없이 기본 기능 검증
"""

import hashlib
import json
import socket
import os
from datetime import datetime

class SimpleLTMTest:
    def __init__(self):
        self.genesis_hash = "20a1cb14930e9cc8f0b7e6872b0630a86c135a6903aec70b6c4e63457c7948a8"
        self.server_host = "ltm-wallet.gnc.ne.kr"
        self.server_port = 50009
        
    def test_sha256(self):
        """SHA-256 해싱 테스트"""
        print("\n🔐 SHA-256 테스트:")
        test_data = "David project begins"
        hash_result = hashlib.sha256(test_data.encode()).hexdigest()
        print(f"   입력: {test_data}")
        print(f"   SHA-256: {hash_result}")
        return True
        
    def test_genesis_hash(self):
        """제네시스 해시 검증"""
        print(f"\n🌟 제네시스 해시: {self.genesis_hash}")
        if len(self.genesis_hash) == 64:
            print("   ✅ 해시 길이 OK (64자)")
        else:
            print("   ❌ 해시 길이 오류")
            return False
        return True
        
    def test_server_connection(self):
        """서버 연결 테스트"""
        print(f"\n🌐 서버 연결 테스트: {self.server_host}:{self.server_port}")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.server_host, self.server_port))
            sock.close()
            
            if result == 0:
                print("   ✅ 서버 연결 성공")
                return True
            else:
                print("   ❌ 서버 연결 실패")
                return False
        except Exception as e:
            print(f"   ❌ 연결 오류: {e}")
            return False
            
    def test_config_files(self):
        """설정 파일 검증"""
        print("\n📁 설정 파일 테스트:")
        
        files_to_check = [
            "electrum/chains/ltm/servers.json",
            "electrum/chains/ltm/checkpoints.json",
            "electrum/chains/ltm/fallback_lnnodes.json"
        ]
        
        all_ok = True
        for file_path in files_to_check:
            if os.path.exists(file_path):
                try:
                    with open(file_path) as f:
                        json.load(f)
                    print(f"   ✅ {file_path}")
                except json.JSONDecodeError as e:
                    print(f"   ❌ {file_path} - JSON 오류: {e}")
                    all_ok = False
            else:
                print(f"   ❌ {file_path} - 파일 없음")
                all_ok = False
                
        return all_ok
        
    def test_adaptive_difficulty(self):
        """적응형 난이도 계산 시뮬레이션"""
        print("\n⚡ 적응형 난이도 시뮬레이션:")
        
        # 1분 목표 (60초)
        target_time = 60
        current_difficulty = 1000000
        
        # 시나리오들
        scenarios = [
            (30, "빠른 블록"),    # 30초 - 난이도 증가 필요
            (60, "정상 블록"),    # 60초 - 난이도 유지
            (120, "느린 블록")    # 120초 - 난이도 감소 필요
        ]
        
        for actual_time, desc in scenarios:
            ratio = actual_time / target_time
            new_difficulty = int(current_difficulty * ratio)
            change = ((new_difficulty - current_difficulty) / current_difficulty) * 100
            
            print(f"   {desc}: {actual_time}초")
            print(f"   현재 난이도: {current_difficulty:,}")
            print(f"   새 난이도: {new_difficulty:,} ({change:+.1f}%)")
            print()
            
        return True

def main():
    """메인 테스트 실행"""
    print("=" * 50)
    print("🚀 LTM (Laptop Mining) 코인 간단 테스트")
    print("=" * 50)
    
    tester = SimpleLTMTest()
    
    tests = [
        ("SHA-256 기능", tester.test_sha256),
        ("제네시스 해시", tester.test_genesis_hash),
        ("서버 연결", tester.test_server_connection),
        ("설정 파일", tester.test_config_files),
        ("적응형 난이도", tester.test_adaptive_difficulty)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"   ❌ {test_name} 테스트 오류: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 기본 테스트 성공!")
        print("\n다음 단계:")
        print("  1. Electrum 의존성 해결")
        print("  2. 실제 LTM 지갑 생성")
        print("  3. 블록체인 동기화 테스트")
    else:
        print("⚠️  일부 테스트 실패. 설정 확인 필요")
    
    print("=" * 50)

if __name__ == "__main__":
    main()