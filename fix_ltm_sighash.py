#!/usr/bin/env python3
"""
LTM SIGHASH 호환성 수정 스크립트
LTM의 변경된 SIGHASH 값에 맞춰 Electrum 수정
"""

import os
import sys
import shutil
from pathlib import Path

def backup_transaction_file():
    """transaction.py 백업"""
    print("💾 transaction.py 백업 중...")
    
    transaction_file = Path("electrum/transaction.py")
    backup_file = Path("electrum/transaction.py.backup")
    
    if transaction_file.exists():
        shutil.copy2(transaction_file, backup_file)
        print("✅ 백업 완료")
        return True
    else:
        print("❌ transaction.py 파일을 찾을 수 없음")
        return False

def create_ltm_sighash_patch():
    """LTM 전용 SIGHASH 패치 생성"""
    print("🔧 LTM SIGHASH 패치 생성 중...")
    
    # LTM 전용 SIGHASH 설정을 위한 패치
    patch_code = '''
# LTM 전용 SIGHASH 확장 (Original Sighash 클래스 확장)
class LTMSighash(Sighash):
    """LTM 네트워크를 위한 확장된 SIGHASH 클래스"""
    
    # LTM에서 사용하는 커스텀 SIGHASH 값들
    # 담당자에게 확인한 실제 값들로 교체 필요
    LTM_ALL = 0x41      # LTM의 변경된 ALL 값 (예시)
    LTM_NONE = 0x42     # LTM의 변경된 NONE 값 (예시)  
    LTM_SINGLE = 0x43   # LTM의 변경된 SINGLE 값 (예시)
    
    @classmethod
    def is_valid_ltm(cls, sighash: int) -> bool:
        """LTM 네트워크에서 유효한 SIGHASH인지 확인"""
        ltm_valid_flags = {
            # 기본 비트코인 SIGHASH
            0x01, 0x02, 0x03,
            0x81, 0x82, 0x83,
            # LTM 전용 SIGHASH (담당자 확인 필요)
            0x41, 0x42, 0x43,
            0xc1, 0xc2, 0xc3,
        }
        return sighash in ltm_valid_flags
    
    @classmethod
    def convert_to_ltm(cls, standard_sighash: int) -> int:
        """표준 SIGHASH를 LTM SIGHASH로 변환"""
        conversion_map = {
            cls.ALL: cls.LTM_ALL,
            cls.NONE: cls.LTM_NONE,
            cls.SINGLE: cls.LTM_SINGLE,
            cls.ALL | cls.ANYONECANPAY: cls.LTM_ALL | 0x80,
            cls.NONE | cls.ANYONECANPAY: cls.LTM_NONE | 0x80,
            cls.SINGLE | cls.ANYONECANPAY: cls.LTM_SINGLE | 0x80,
        }
        return conversion_map.get(standard_sighash, standard_sighash)
    
    @classmethod 
    def convert_from_ltm(cls, ltm_sighash: int) -> int:
        """LTM SIGHASH를 표준 SIGHASH로 변환"""
        conversion_map = {
            cls.LTM_ALL: cls.ALL,
            cls.LTM_NONE: cls.NONE, 
            cls.LTM_SINGLE: cls.SINGLE,
            cls.LTM_ALL | 0x80: cls.ALL | cls.ANYONECANPAY,
            cls.LTM_NONE | 0x80: cls.NONE | cls.ANYONECANPAY,
            cls.LTM_SINGLE | 0x80: cls.SINGLE | cls.ANYONECANPAY,
        }
        return conversion_map.get(ltm_sighash, ltm_sighash)

# LTM 네트워크 감지 함수
def is_ltm_network():
    """현재 네트워크가 LTM인지 확인"""
    from .constants import get_current_network
    try:
        network = get_current_network()
        return getattr(network, 'NET_NAME', '') == 'ltm'
    except:
        return False

# 기존 Sighash.is_valid 메서드를 LTM 호환성으로 패치
_original_is_valid = Sighash.is_valid

@classmethod
def patched_is_valid(cls, sighash: int, *, is_taproot: bool = False) -> bool:
    """LTM 네트워크를 고려한 SIGHASH 검증"""
    if is_ltm_network():
        return LTMSighash.is_valid_ltm(sighash)
    return _original_is_valid(sighash, is_taproot=is_taproot)

# 패치 적용
Sighash.is_valid = patched_is_valid
'''

    patch_file = Path("ltm_sighash_patch.py")
    with open(patch_file, "w") as f:
        f.write(patch_code)
    
    print("✅ LTM SIGHASH 패치 생성 완료")
    return True

def apply_constants_patch():
    """constants.py에 LTM SIGHASH 설정 추가"""
    print("⚙️ constants.py에 LTM SIGHASH 설정 추가 중...")
    
    constants_file = Path("electrum/constants.py")
    if not constants_file.exists():
        print("❌ constants.py를 찾을 수 없음")
        return False
    
    # constants.py 읽기
    with open(constants_file, "r") as f:
        content = f.read()
    
    # LTM 클래스에 SIGHASH 설정 추가
    ltm_sighash_config = '''
    # LTM 전용 SIGHASH 설정
    LTM_SIGHASH_ALL = 0x41      # 담당자 확인 필요
    LTM_SIGHASH_NONE = 0x42     # 담당자 확인 필요
    LTM_SIGHASH_SINGLE = 0x43   # 담당자 확인 필요
    USE_CUSTOM_SIGHASH = True   # LTM은 커스텀 SIGHASH 사용
'''
    
    # LTMMainnet 클래스 찾아서 SIGHASH 설정 추가
    if "class LTMMainnet" in content:
        # LTMMainnet 클래스 내부에 추가할 설정
        class_insertion = content.replace(
            "class LTMMainnet(AbstractNet):",
            f"class LTMMainnet(AbstractNet):{ltm_sighash_config}"
        )
        
        with open(constants_file, "w") as f:
            f.write(class_insertion)
        
        print("✅ LTM SIGHASH 설정 추가 완료")
        return True
    
    print("⚠️ LTMMainnet 클래스를 찾을 수 없음")
    return False

def create_sighash_info_script():
    """SIGHASH 값 확인을 위한 정보 스크립트 생성"""
    print("📋 SIGHASH 정보 확인 스크립트 생성 중...")
    
    info_script = '''#!/usr/bin/env python3
"""
LTM SIGHASH 값 확인 스크립트
담당자에게 정확한 SIGHASH 값을 확인해야 합니다.
"""

def show_sighash_info():
    """SIGHASH 값 정보 표시"""
    print("🔍 SIGHASH 값 정보")
    print("=" * 50)
    
    print("📋 표준 비트코인 SIGHASH:")
    print("   SIGHASH_ALL = 0x01")
    print("   SIGHASH_NONE = 0x02") 
    print("   SIGHASH_SINGLE = 0x03")
    print("   SIGHASH_ANYONECANPAY = 0x80")
    
    print("\\n❓ LTM에서 사용하는 SIGHASH 값:")
    print("   담당자에게 다음 정보를 확인해주세요:")
    print("   1. LTM_SIGHASH_ALL = ?")
    print("   2. LTM_SIGHASH_NONE = ?") 
    print("   3. LTM_SIGHASH_SINGLE = ?")
    print("   4. ANYONECANPAY 플래그 사용 여부")
    
    print("\\n🛠️ 확인 방법:")
    print("   1. LTM 소스코드에서 SIGHASH 정의 확인")
    print("   2. 블루월렛이 사용하는 SIGHASH 값 확인")
    print("   3. ElectrumX 서버 로그에서 SIGHASH 오류 확인")

def test_current_sighash():
    """현재 Electrum의 SIGHASH 사용 확인"""
    try:
        import sys
        sys.path.append(".")
        from electrum.transaction import Sighash
        
        print("\\n🔧 현재 Electrum SIGHASH 설정:")
        print(f"   ALL: {hex(Sighash.ALL)}")
        print(f"   NONE: {hex(Sighash.NONE)}")
        print(f"   SINGLE: {hex(Sighash.SINGLE)}")
        print(f"   ANYONECANPAY: {hex(Sighash.ANYONECANPAY)}")
        
    except ImportError as e:
        print(f"❌ Electrum 모듈 로드 실패: {e}")

if __name__ == "__main__":
    show_sighash_info()
    test_current_sighash()
'''
    
    info_file = Path("ltm_sighash_info.py")
    with open(info_file, "w") as f:
        f.write(info_script)
    
    print("✅ SIGHASH 정보 스크립트 생성 완료")
    return True

def main():
    """메인 실행"""
    print("🔧 LTM SIGHASH 호환성 수정")
    print("=" * 50)
    
    print("⚠️ 중요: 담당자에게 LTM의 정확한 SIGHASH 값을 확인해야 합니다!")
    print()
    
    # 1. 백업 생성
    backup_transaction_file()
    
    # 2. SIGHASH 패치 생성
    create_ltm_sighash_patch()
    
    # 3. constants.py 패치
    apply_constants_patch()
    
    # 4. 정보 스크립트 생성
    create_sighash_info_script()
    
    print("\\n📋 다음 단계:")
    print("1. 담당자에게 LTM의 SIGHASH 값 확인")
    print("2. ltm_sighash_patch.py의 값들을 실제 값으로 수정")
    print("3. transaction.py에 패치 적용")
    print("4. Electrum 재시작 후 테스트")
    
    print("\\n💡 정보 확인: python3 ltm_sighash_info.py")

if __name__ == "__main__":
    main()