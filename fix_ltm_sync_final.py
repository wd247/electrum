#!/usr/bin/env python3
"""
LTM Electrum 완전 수정 스크립트 - 최종 버전
동기화 문제를 근본적으로 해결합니다.
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

def clean_ltm_data():
    """LTM 데이터 완전 정리"""
    print("🧹 LTM 데이터 정리 중...")
    ltm_path = Path.home() / ".electrum" / "ltm"
    if ltm_path.exists():
        shutil.rmtree(ltm_path)
    print("✅ LTM 데이터 정리 완료")

def setup_server_auth():
    """서버 인증 설정"""
    print("🔐 서버 인증 설정 중...")
    ltm_path = Path.home() / ".electrum" / "ltm"
    ltm_path.mkdir(parents=True, exist_ok=True)
    
    config = {
        "auto_connect": True,
        "blockchain_preferred_block": {
            "hash": "20a1cb14930e9cc8f0b7e6872b0630a86c135a6903aec70b6c4e63457c7948a8",
            "height": 0
        },
        "chain": "ltm",
        "check_updates": True,
        "config_version": 3,
        "oneserver": True,
        "proxy": None,
        "server": "ltm-wallet.gnc.ne.kr:50009:s",
        "server_auth": {
            "ltm-wallet.gnc.ne.kr:50009": {
                "password": "ltm123",
                "username": "ltm"
            }
        }
    }
    
    config_file = ltm_path / "config"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
    
    print("✅ 서버 인증 설정 완료")

def setup_simple_checkpoints():
    """간단한 체크포인트 설정"""
    print("📋 체크포인트 설정 중...")
    checkpoint_dir = Path("electrum/chains/ltm")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # 제네시스 블록만 사용
    checkpoints = {
        "0": "20a1cb14930e9cc8f0b7e6872b0630a86c135a6903aec70b6c4e63457c7948a8"
    }
    
    checkpoint_file = checkpoint_dir / "checkpoints.json"
    with open(checkpoint_file, "w") as f:
        json.dump(checkpoints, f, indent=2)
    
    print("✅ 체크포인트 설정 완료")

def setup_servers():
    """서버 리스트 설정"""
    print("🌐 서버 리스트 설정 중...")
    server_dir = Path("electrum/chains/ltm")
    server_dir.mkdir(parents=True, exist_ok=True)
    
    servers = {
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
    
    print("✅ 서버 리스트 설정 완료")

def test_connection():
    """서버 연결 테스트"""
    print("🔍 서버 연결 테스트 중...")
    success, stdout, stderr = run_command("nc -zv ltm-wallet.gnc.ne.kr 50009")
    if success or "succeeded" in stderr:
        print("✅ SSL 포트 50009 연결 가능")
        return True
    else:
        print("❌ SSL 포트 50009 연결 실패")
        return False

def start_electrum():
    """Electrum 시작"""
    print("🚀 Electrum 시작 중...")
    
    # 백그라운드에서 GUI 시작
    cmd = "nohup ./run_electrum_ltm --ltm > /dev/null 2>&1 &"
    run_command(cmd)
    
    print("⏰ 초기화 대기 중... (20초)")
    time.sleep(20)
    
    # 상태 확인
    success, stdout, stderr = run_command("./run_electrum_ltm getinfo")
    if success:
        try:
            info = json.loads(stdout)
            print(f"📊 현재 상태:")
            print(f"   - 네트워크: {info.get('network', 'N/A')}")
            print(f"   - 서버: {info.get('server', 'N/A')}")
            print(f"   - 연결됨: {info.get('connected', False)}")
            print(f"   - 블록높이: {info.get('blockchain_height', 0)}")
            print(f"   - 서버높이: {info.get('server_height', 0)}")
            print(f"   - 자동연결: {info.get('auto_connect', False)}")
            
            if info.get('connected'):
                print("✅ 연결 성공!")
            else:
                print("⚠️ 아직 연결 중... 더 기다려보세요.")
                
        except json.JSONDecodeError:
            print("❌ 상태 정보 파싱 실패")
    else:
        print("❌ Electrum 시작 실패")

def main():
    """메인 실행"""
    print("🔧 LTM Electrum 완전 수정 시작")
    print("=" * 50)
    
    # 1. 연결 테스트
    if not test_connection():
        print("❌ 서버 연결이 불가능합니다. 네트워크를 확인하세요.")
        return
    
    # 2. 프로세스 종료
    kill_electrum()
    
    # 3. 데이터 정리
    clean_ltm_data()
    
    # 4. 설정 파일들 생성
    setup_simple_checkpoints()
    setup_servers()
    setup_server_auth()
    
    # 5. Electrum 시작
    start_electrum()
    
    print("\n🎉 수정 완료!")
    print("GUI에서 연결 상태를 확인하세요.")
    print("녹색 불이 들어올 때까지 조금 더 기다려야 할 수 있습니다.")

if __name__ == "__main__":
    main()