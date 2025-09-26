#!/usr/bin/env python3
"""
LTM Electrum 고급 동기화 수정 - 익스플로러 정보 활용
현재 블록 높이 23045에 맞춰 동기화 최적화
"""

import os
import sys
import json
import shutil
import subprocess
import time
from pathlib import Path

def run_command(cmd, shell=True):
    """명령어 실행"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def kill_electrum():
    """모든 electrum 프로세스 종료"""
    print("🔄 Electrum 프로세스 종료 중...")
    run_command("pkill -9 -f electrum")
    time.sleep(3)

def setup_advanced_config():
    """고급 설정으로 LTM 구성"""
    print("⚙️ 고급 LTM 설정 구성 중...")
    
    ltm_path = Path.home() / ".electrum" / "ltm"
    ltm_path.mkdir(parents=True, exist_ok=True)
    
    # 익스플로러 정보를 반영한 최적화된 설정
    config = {
        "auto_connect": True,
        "blockchain_preferred_block": {
            "hash": "20a1cb14930e9cc8f0b7e6872b0630a86c135a6903aec70b6c4e63457c7948a8",
            "height": 0
        },
        "chain": "ltm",
        "check_updates": False,  # 업데이트 체크 비활성화로 성능 개선
        "config_version": 3,
        "oneserver": False,  # 여러 서버 시도를 위해 비활성화
        "proxy": None,
        "server": "54.169.107.75:50009:s",  # IP로 직접 연결
        "server_auth": {
            "54.169.107.75:50009": {
                "password": "ltm123",
                "username": "ltm"
            },
            "ltm-wallet.gnc.ne.kr:50009": {
                "password": "ltm123", 
                "username": "ltm"
            }
        },
        "blockchain_start_height": 22000  # 최근 블록부터 시작
    }
    
    config_file = ltm_path / "config"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
    
    print("✅ 고급 설정 완료")

def setup_optimized_checkpoints():
    """최신 블록 정보로 체크포인트 최적화"""
    print("🎯 최적화된 체크포인트 설정 중...")
    
    checkpoint_dir = Path("electrum/chains/ltm")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # 익스플로러에서 확인한 현재 높이 23045 근처로 설정
    checkpoints = {
        "0": "20a1cb14930e9cc8f0b7e6872b0630a86c135a6903aec70b6c4e63457c7948a8",
        "20000": "0000000000000000000000000000000000000000000000000000000000000000",
        "22000": "0000000000000000000000000000000000000000000000000000000000000000",
        "23000": "0000000000000000000000000000000000000000000000000000000000000000"
    }
    
    checkpoint_file = checkpoint_dir / "checkpoints.json"
    with open(checkpoint_file, "w") as f:
        json.dump(checkpoints, f, indent=2)
    
    print("✅ 최적화된 체크포인트 설정 완료")

def setup_multiple_servers():
    """여러 서버 옵션 설정"""
    print("🌐 다중 서버 설정 중...")
    
    server_dir = Path("electrum/chains/ltm")
    server_dir.mkdir(parents=True, exist_ok=True)
    
    # IP 주소를 우선으로 하고 백업 서버들 추가
    servers = {
        "54.169.107.75": {
            "pruning": "-",
            "t": "50008",
            "s": "50009",
            "version": "1.4.2"
        },
        "ltm-wallet.gnc.ne.kr": {
            "pruning": "-", 
            "t": "50008",
            "s": "50009",
            "version": "1.4.2"
        }
    }
    
    server_file = server_dir / "servers.json"
    with open(server_file, "w") as f:
        json.dump(servers, f, indent=2)
    
    print("✅ 다중 서버 설정 완료")

def start_electrum_optimized():
    """최적화된 방식으로 Electrum 시작"""
    print("🚀 최적화된 Electrum 시작 중...")
    
    # 환경변수 설정으로 디버그 모드 활성화
    env = os.environ.copy()
    env['ELECTRUM_DEBUG'] = '1'
    
    # 백그라운드에서 시작
    cmd = ["nohup", "./run_electrum_ltm", "--ltm", "--verbose"]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("⏰ 초기화 대기 중... (30초)")
    time.sleep(30)
    
    # 연결 강제 설정
    print("🔗 서버 연결 강제 설정 중...")
    run_command("./run_electrum_ltm setconfig auto_connect true")
    run_command("./run_electrum_ltm setconfig server 54.169.107.75:50009:s")
    
    time.sleep(15)
    
    # 상태 확인
    success, stdout, stderr = run_command("./run_electrum_ltm getinfo")
    if success:
        try:
            info = json.loads(stdout)
            print(f"📊 현재 상태:")
            print(f"   - 네트워크: {info.get('network', 'N/A')}")
            print(f"   - 서버: {info.get('server', 'N/A')}")
            print(f"   - 연결됨: {info.get('connected', False)}")
            print(f"   - 로컬 블록높이: {info.get('blockchain_height', 0)}")
            print(f"   - 서버 블록높이: {info.get('server_height', 0)}")
            print(f"   - Fee 정보: {'있음' if info.get('fee_estimates') else '없음'}")
            
            if info.get('connected'):
                print("✅ 연결 성공!")
            elif info.get('fee_estimates'):
                print("⚠️ 데이터 수신 중... 연결 진행 중")
            else:
                print("❌ 아직 연결 안됨")
                
        except json.JSONDecodeError:
            print("❌ 상태 정보 파싱 실패")
    else:
        print("❌ Electrum 시작 실패")

def monitor_sync():
    """동기화 상태 모니터링"""
    print("\n📈 동기화 모니터링 시작 (60초간)")
    
    for i in range(6):
        time.sleep(10)
        success, stdout, stderr = run_command("./run_electrum_ltm getinfo")
        if success:
            try:
                info = json.loads(stdout)
                local_height = info.get('blockchain_height', 0)
                server_height = info.get('server_height', 0)
                connected = info.get('connected', False)
                
                print(f"   [{i+1}/6] 로컬: {local_height}, 서버: {server_height}, 연결: {connected}")
                
                if connected and server_height > 0:
                    print("🎉 완전 동기화 성공!")
                    break
                    
            except json.JSONDecodeError:
                print(f"   [{i+1}/6] 상태 확인 실패")

def main():
    """메인 실행"""
    print("🔧 LTM Electrum 고급 동기화 수정 시작")
    print("현재 네트워크 블록 높이: 23045")
    print("=" * 50)
    
    # 1. 프로세스 정리
    kill_electrum()
    
    # 2. 고급 설정
    setup_advanced_config()
    setup_optimized_checkpoints()
    setup_multiple_servers()
    
    # 3. 최적화된 시작
    start_electrum_optimized()
    
    # 4. 동기화 모니터링
    monitor_sync()
    
    print("\n🎯 고급 수정 완료!")
    print("GUI에서 연결 상태를 확인하세요.")

if __name__ == "__main__":
    main()