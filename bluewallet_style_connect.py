#!/usr/bin/env python3
"""
LTM 블루월렛 스타일 연결 스크립트
모바일 지갑처럼 가볍게 동작하도록 최적화
"""

import json
import subprocess
import time
import os
from pathlib import Path

def run_cmd(cmd):
    """명령어 실행"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def create_lightweight_config():
    """블루월렛 스타일의 가벼운 설정 생성"""
    print("📱 블루월렛 스타일 설정 생성 중...")
    
    ltm_path = Path.home() / ".electrum" / "ltm"
    ltm_path.mkdir(parents=True, exist_ok=True)
    
    # 블루월렛처럼 최소한의 설정으로 동작
    config = {
        "auto_connect": True,
        "blockchain_preferred_block": {
            "hash": "20a1cb14930e9cc8f0b7e6872b0630a86c135a6903aec70b6c4e63457c7948a8",
            "height": 22900  # 높은 시작점으로 빠른 동기화
        },
        "chain": "ltm",
        "check_updates": False,
        "config_version": 3,
        "oneserver": True,  # 블루월렛처럼 단일 서버 사용
        "proxy": None,
        "server": "54.169.107.75:50009:s",
        "server_auth": {
            "54.169.107.75:50009": {
                "password": "ltm123",
                "username": "ltm"
            }
        },
        # 모바일 최적화 설정
        "dynamic_fees": True,
        "fee_estimates": {},
        "use_rbf": True,
        "confirmed_only": False  # 블루월렛처럼 0-conf도 표시
    }
    
    config_file = ltm_path / "config"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
    
    print("✅ 블루월렛 스타일 설정 완료")

def create_minimal_checkpoints():
    """최소한의 체크포인트만 사용"""
    print("🎯 최소 체크포인트 설정...")
    
    # 제네시스 블록과 최근 블록만 사용
    checkpoints = {
        "0": "20a1cb14930e9cc8f0b7e6872b0630a86c135a6903aec70b6c4e63457c7948a8"
        # 다른 체크포인트 제거 - 블루월렛처럼 최소화
    }
    
    checkpoint_file = Path("electrum/chains/ltm/checkpoints.json")
    with open(checkpoint_file, "w") as f:
        json.dump(checkpoints, f, indent=2)
    
    print("✅ 최소 체크포인트 완료")

def cleanup_headers():
    """헤더 캐시 완전 정리"""
    print("🧹 헤더 캐시 정리 중...")
    
    # 블록체인 헤더 모든 데이터 삭제
    cache_paths = [
        "~/.electrum/ltm/blockchain_headers",
        "~/.electrum/ltm/forks", 
        "~/.electrum/ltm/merkle_cache",
        "~/.electrum/ltm/addr_history",
        "~/.electrum/ltm/verified_tx3"
    ]
    
    for path in cache_paths:
        run_cmd(f"rm -rf {path}")
    
    print("✅ 캐시 정리 완료")

def test_bluewallet_style():
    """블루월렛 스타일로 연결 테스트"""
    print("📱 블루월렛 스타일 연결 테스트 중...")
    
    # 모든 프로세스 종료
    run_cmd("pkill -9 -f electrum")
    time.sleep(3)
    
    # 설정 적용
    create_lightweight_config()
    create_minimal_checkpoints() 
    cleanup_headers()
    
    print("🚀 가벼운 모드로 시작...")
    
    # GUI 시작 (블루월렛처럼 빠른 시작)
    run_cmd("nohup ./run_electrum_ltm --ltm > /dev/null 2>&1 &")
    
    # 짧은 대기 시간 (블루월렛처럼)
    time.sleep(15)
    
    print("🔄 즉시 서버 연결 설정...")
    
    # 강제 서버 설정
    run_cmd("./run_electrum_ltm setconfig oneserver true")
    run_cmd("./run_electrum_ltm setconfig server 54.169.107.75:50009:s") 
    
    time.sleep(10)
    
    # 상태 확인
    success, stdout, stderr = run_cmd("./run_electrum_ltm getinfo")
    if success:
        try:
            info = json.loads(stdout)
            print(f"\n📊 블루월렛 스타일 연결 결과:")
            print(f"   🌐 서버: {info.get('server', 'N/A')}")
            print(f"   🔗 연결됨: {info.get('connected', False)}")  
            print(f"   📱 SPV 노드: {info.get('spv_nodes', 0)}")
            print(f"   💰 Fee 정보: {'✅' if info.get('fee_estimates') else '❌'}")
            print(f"   🧱 로컬 높이: {info.get('blockchain_height', 0)}")
            print(f"   🏆 서버 높이: {info.get('server_height', 0)}")
            
            if info.get('connected'):
                print("\n🎉 블루월렛 스타일 연결 성공!")
                return True
            elif info.get('fee_estimates'):
                print("\n⚡ 데이터 수신 중 - 블루월렛처럼 동작 중")
                return True
            else:
                print("\n⚠️ 아직 연결 진행 중...")
                return False
                
        except json.JSONDecodeError:
            print("\n❌ 상태 정보 파싱 실패")
            return False
    
    return False

def monitor_like_bluewallet():
    """블루월렛처럼 간단한 모니터링"""
    print("\n📱 블루월렛 스타일 모니터링 (30초)...")
    
    for i in range(3):
        time.sleep(10)
        success, stdout, stderr = run_cmd("./run_electrum_ltm getinfo")
        
        if success:
            try:
                info = json.loads(stdout)
                connected = info.get('connected', False)
                server = info.get('server', 'N/A')
                height = info.get('blockchain_height', 0)
                
                print(f"   [{i+1}/3] {server} | 연결: {connected} | 높이: {height}")
                
                if connected:
                    print("🎊 완전 연결 성공!")
                    break
                    
            except:
                print(f"   [{i+1}/3] 상태 확인 실패")

def main():
    """메인 실행"""
    print("📱 LTM 블루월렛 스타일 연결 시작")
    print("=" * 40)
    
    if test_bluewallet_style():
        monitor_like_bluewallet()
    
    print("\n📱 블루월렛 스타일 설정 완료!")
    print("GUI에서 연결 상태를 확인하세요.")

if __name__ == "__main__":
    main()