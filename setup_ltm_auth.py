#!/usr/bin/env python3

import json
import os

def add_server_auth():
    """LTM 설정에 서버 인증 정보 추가"""
    
    config_file = os.path.expanduser("~/.electrum/ltm/config")
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # 서버 인증 정보 추가
        config["server_auth"] = {
            "ltm-wallet.gnc.ne.kr:50008": {
                "username": "user",
                "password": "password"
            }
        }
        
        # proxy를 HTTP auth proxy로 설정 (서버 인증용)
        config["proxy"] = None
        
        # 서버를 인증 포함하여 설정
        config["server"] = "user:password@ltm-wallet.gnc.ne.kr:50008:t"
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
            
        print("✅ 서버 인증 정보가 추가되었습니다:")
        print(f"  - 서버: ltm-wallet.gnc.ne.kr:50008")
        print(f"  - 사용자: user")
        print(f"  - 인증: 설정됨")
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 실패: {e}")
        return False

if __name__ == "__main__":
    print("🔐 LTM 서버 인증 설정")
    print("=" * 30)
    
    if add_server_auth():
        print("\n✅ 인증 설정 완료! 이제 Electrum을 재시작하세요.")
    else:
        print("\n❌ 인증 설정 실패")