#!/usr/bin/env python3
"""
LTM 지갑 생성 및 테스트 스크립트
완전한 LTM 네트워크 지원 확인
"""

import os
import sys
import subprocess
import time

# Electrum 경로 추가
sys.path.insert(0, '/home/junny/electrum')

def run_electrum_cmd(cmd_args, timeout=30):
    """Electrum 명령어 실행"""
    base_cmd = [
        sys.executable,
        '/home/junny/electrum/electrum/electrum',
        '--ltm',  # LTM 메인넷 사용
        '--offline'  # 오프라인 모드
    ]
    
    full_cmd = base_cmd + cmd_args
    print(f"🔧 실행: {' '.join(full_cmd)}")
    
    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd='/home/junny/electrum'
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "타임아웃"
    except Exception as e:
        return -2, "", str(e)

def test_ltm_electrum():
    """LTM Electrum 기본 기능 테스트"""
    
    print("=" * 60)
    print("🚀 LTM Electrum 통합 테스트")
    print("=" * 60)
    
    # 1. 버전 확인
    print("\n1️⃣ LTM 네트워크 버전 확인")
    code, out, err = run_electrum_cmd(['version'])
    if code == 0:
        print(f"✅ 버전: {out.strip()}")
    else:
        print(f"❌ 버전 확인 실패: {err}")
        return False
    
    # 2. 도움말 확인
    print("\n2️⃣ 명령어 도움말 확인")
    code, out, err = run_electrum_cmd(['help'])
    if code == 0:
        print("✅ 도움말 표시 성공")
        if 'create' in out and 'gui' in out:
            print("   주요 명령어들 확인됨")
    else:
        print(f"❌ 도움말 실패: {err}")
    
    # 3. 서버 정보 확인 (오프라인이므로 설정만 확인)
    print("\n3️⃣ LTM 네트워크 설정 확인")
    try:
        from electrum import constants
        ltm_net = constants.LTMMainnet()
        print(f"✅ LTM 메인넷 제네시스: {ltm_net.GENESIS}")
        print(f"   체크포인트: {ltm_net.CHECKPOINTS}")
        print(f"   기본 서버: {ltm_net.DEFAULT_SERVERS}")
    except Exception as e:
        print(f"❌ LTM 네트워크 설정 오류: {e}")
        return False
    
    # 4. 새 시드 생성 테스트
    print("\n4️⃣ 새 시드 생성 테스트")
    code, out, err = run_electrum_cmd(['make_seed'])
    if code == 0:
        seed_words = out.strip().split()
        if len(seed_words) >= 12:
            print(f"✅ 시드 생성 성공 ({len(seed_words)}개 단어)")
            print(f"   시드: {' '.join(seed_words[:3])}... (나머지 숨김)")
        else:
            print(f"❌ 시드가 너무 짧음: {out}")
    else:
        print(f"❌ 시드 생성 실패: {err}")
    
    # 5. 임시 지갑 생성 테스트 
    print("\n5️⃣ 임시 LTM 지갑 생성 테스트")
    temp_wallet = '/tmp/test_ltm_wallet'
    
    # 기존 임시 지갑 삭제
    if os.path.exists(temp_wallet):
        os.remove(temp_wallet)
    
    # 새 지갑 생성 (시드 자동 생성)
    code, out, err = run_electrum_cmd([
        'create', 
        '-w', temp_wallet,
        '--seed_type=bip39'
    ], timeout=60)
    
    if code == 0:
        print("✅ LTM 지갑 생성 성공")
        
        # 지갑 정보 확인
        code2, out2, err2 = run_electrum_cmd([
            'getinfo',
            '-w', temp_wallet
        ])
        
        if code2 == 0:
            print("✅ 지갑 정보 조회 성공")
            print("   지갑이 올바르게 생성되었습니다")
        else:
            print(f"⚠️ 지갑 정보 조회 실패: {err2}")
        
        # 임시 지갑 정리
        if os.path.exists(temp_wallet):
            os.remove(temp_wallet)
            print("   임시 지갑 파일 정리 완료")
            
    else:
        print(f"❌ LTM 지갑 생성 실패: {err}")
        if "seed" in err.lower():
            print("   시드 관련 문제일 수 있습니다")
    
    print("\n" + "=" * 60)
    print("📊 LTM Electrum 통합 테스트 완료")
    print("=" * 60)
    
    return True

def main():
    """메인 실행 함수"""
    try:
        test_ltm_electrum()
        print("\n🎉 모든 테스트가 완료되었습니다!")
        print("\n📋 다음 단계:")
        print("  1. 실제 LTM 서버와 연결 테스트")
        print("  2. GUI 모드로 LTM 지갑 사용")
        print("  3. LTM 코인 송수신 테스트")
        print("\n🔧 GUI 실행: python3 electrum/electrum --ltm gui")
        
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()