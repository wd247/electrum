#!/usr/bin/env python3
"""
수정된 LTM HD 지갑 스크립트 - 라이브러리 통일
bitcoinutils 라이브러리로 모든 기능 통일
"""

import socket
import json
import hashlib
from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import PrivateKey, P2wpkhAddress
from bitcoinutils.hdwallet import HDWallet
from bitcoinutils.script import Script

# 설정
setup('mainnet')

# HD 지갑 설정
MNEMONIC_PHRASE = "purchase banner canyon mother harbor toss sad section bomb icon trim obey"
ACCOUNT_INDEX = 0
SCAN_ADDRESS_COUNT = 160
HOST = 'ltm-wallet.gnc.ne.kr'
PORT = 50008
CONSOLIDATION_ADDRESS_INDEX = 0
MIN_UTXO_VALUE = 1000
FEE_PER_INPUT = 148
BASE_FEE = 200

def generate_unified_hd_wallet(mnemonic_phrase, count=160, account_idx=0):
    """bitcoinutils로 통일된 HD 지갑 생성"""
    print(f"🔑 통일된 HD 지갑 생성 중... ({count}개)")
    
    try:
        # HDWallet 객체 생성
        hdwallet = HDWallet()
        
        # 니모닉에서 지갑 생성 (BIP84 - Native SegWit)
        hdwallet.from_mnemonic(mnemonic_phrase, passphrase="")
        
        # 계정 레벨까지 유도 (m/84'/0'/account_idx')
        account_path = f"m/84'/0'/{account_idx}'"
        account_wallet = hdwallet.from_path(account_path)
        
        addresses = []
        private_keys = []
        
        print("📍 주소 생성 진행률:")
        checkpoint_interval = max(1, count // 10)
        
        for i in range(count):
            # 외부 체인 주소 생성 (m/84'/0'/account_idx'/0/i)
            address_path = f"0/{i}"
            
            # 주소별 지갑 유도
            address_wallet = account_wallet.from_path(address_path)
            
            # 개인키 생성 (WIF 형식)
            private_key = address_wallet.private_key()
            private_keys.append(private_key.to_wif())
            
            # P2WPKH 주소 생성 (bc1으로 시작)
            public_key = private_key.get_public_key()
            address = public_key.get_segwit_address().to_string()
            addresses.append(address)
            
            # 진행률 표시
            if (i + 1) % checkpoint_interval == 0 or i == count - 1:
                progress = ((i + 1) / count) * 100
                print(f"   진행률: {progress:5.1f}% ({i + 1:3d}/{count})")
        
        print(f"✅ 통일된 HD 지갑 생성 완료!")
        print(f"   - 생성된 주소: {len(addresses)}개")
        print(f"   - 생성된 개인키: {len(private_keys)}개")
        
        return addresses, private_keys
        
    except Exception as e:
        print(f"❌ HD 지갑 생성 실패: {e}")
        return None, None

def verify_unified_wallet_consistency(addresses, private_keys, sample_count=10):
    """통일된 지갑의 일관성 검증"""
    print(f"🔍 지갑 일관성 검증 (샘플 {sample_count}개)...")
    
    # 검증할 인덱스들 선택
    import random
    sample_indices = list(range(min(sample_count, len(addresses))))
    if len(addresses) > sample_count:
        additional = random.sample(range(sample_count, len(addresses)), 
                                 min(3, len(addresses) - sample_count))
        sample_indices.extend(additional)
    
    match_count = 0
    error_count = 0
    
    for i in sample_indices:
        try:
            # 개인키에서 주소 재생성
            priv_key = PrivateKey(private_keys[i])
            pub_key = priv_key.get_public_key()
            derived_address = pub_key.get_segwit_address().to_string()
            
            # 비교
            if addresses[i] == derived_address:
                match_count += 1
                print(f"   ✅ #{i:3d}: 일치 - {addresses[i]}")
            else:
                print(f"   ❌ #{i:3d}: 불일치!")
                print(f"        저장된: {addresses[i]}")
                print(f"        계산된: {derived_address}")
        
        except Exception as e:
            error_count += 1
            print(f"   ⚠️ #{i:3d}: 검증 실패 - {e}")
    
    success_rate = match_count / len(sample_indices) * 100
    print(f"\n📊 검증 결과:")
    print(f"   - 일치: {match_count}개")
    print(f"   - 오류: {error_count}개")
    print(f"   - 성공률: {success_rate:.1f}%")
    
    return success_rate == 100.0

def generate_zpub_from_mnemonic(mnemonic_phrase, account_idx=0):
    """니모닉에서 정확한 zpub 생성"""
    print(f"🔑 니모닉에서 zpub 생성 (계정 {account_idx})...")
    
    try:
        # HDWallet 객체 생성
        hdwallet = HDWallet()
        hdwallet.from_mnemonic(mnemonic_phrase, passphrase="")
        
        # BIP84 계정 레벨로 유도 (m/84'/0'/account_idx')
        account_path = f"m/84'/0'/{account_idx}'"
        account_wallet = hdwallet.from_path(account_path)
        
        # 확장 공개키 추출 (zpub)
        zpub = account_wallet.extended_public_key()
        
        print(f"   생성된 zpub: {zpub}")
        return zpub
        
    except Exception as e:
        print(f"   ❌ zpub 생성 실패: {e}")
        return None

# ElectrumX 통신 함수 (기존과 동일)
def electrumx_request(method, params):
    s = socket.create_connection((HOST, PORT))
    req = json.dumps({'id': 0, 'method': method, 'params': params}) + '\\n'
    s.sendall(req.encode())
    f = s.makefile('r')
    response_line = f.readline()
    s.close()
    res = json.loads(response_line)
    if 'result' not in res:
        raise Exception(f"ElectrumX error: {res}")
    return res['result']

def address_to_scripthash(address_str):
    """주소를 script hash로 변환"""
    if address_str.startswith('bc1'):
        addr = P2wpkhAddress(address_str)
    else:
        raise Exception(f"지원하지 않는 주소 형식: {address_str}")
    
    spk = addr.to_script_pub_key().to_hex()
    sha = hashlib.sha256(bytes.fromhex(spk)).digest()
    return sha[::-1].hex()

def test_unified_wallet():
    """통일된 HD 지갑 테스트"""
    print("🧪 통일된 HD 지갑 테스트")
    print("=" * 50)
    print(f"📝 니모닉: {MNEMONIC_PHRASE}")
    print(f"🏦 계정: {ACCOUNT_INDEX}")
    print(f"🔢 생성 개수: {SCAN_ADDRESS_COUNT}\\n")
    
    # 1. 올바른 zpub 생성
    correct_zpub = generate_zpub_from_mnemonic(MNEMONIC_PHRASE, ACCOUNT_INDEX)
    provided_zpub = "zpub6nNaJZM6KvEghtNGBjFMrd6Aex3pPN4WhhuH6JqUy93zZJQFhL7KPNPYcQLwJxSBaYtnCYafSXi4wpZQ74Kafs8ABwx8fQkow2cTw7KT5di"
    
    print(f"\\n🔍 zpub 비교:")
    print(f"   제공된: {provided_zpub}")
    print(f"   계산된: {correct_zpub}")
    
    if correct_zpub == provided_zpub:
        print("   ✅ zpub 완전 일치!")
        zpub_match = True
    else:
        print("   ❌ zpub 불일치!")
        zpub_match = False
    
    # 2. HD 지갑 생성
    print(f"\\n" + "-" * 50)
    addresses, private_keys = generate_unified_hd_wallet(MNEMONIC_PHRASE, SCAN_ADDRESS_COUNT, ACCOUNT_INDEX)
    
    if not addresses or not private_keys:
        print("❌ HD 지갑 생성 실패")
        return False
    
    # 3. 일관성 검증
    print(f"\\n" + "-" * 50)
    is_consistent = verify_unified_wallet_consistency(addresses, private_keys)
    
    # 4. 첫 10개 주소 표시
    print(f"\\n🏠 첫 10개 주소:")
    for i in range(min(10, len(addresses))):
        print(f"   #{i:2d}: {addresses[i]}")
    
    # 5. 결과 요약
    print(f"\\n" + "=" * 50)
    print(f"📊 테스트 결과:")
    print(f"   - zpub 일치: {'✅' if zpub_match else '❌'}")
    print(f"   - 지갑 생성: {'✅' if addresses else '❌'}")
    print(f"   - 일관성 검증: {'✅' if is_consistent else '❌'}")
    
    if zpub_match and addresses and is_consistent:
        print(f"\\n🎉 모든 테스트 통과! 코드가 올바르게 작동합니다.")
        return True
    else:
        print(f"\\n⚠️ 일부 테스트 실패. 코드 수정이 필요합니다.")
        return False

def main():
    """메인 실행"""
    print("🔧 수정된 LTM HD 지갑 스크립트")
    print("=" * 60)
    
    # 테스트 실행
    success = test_unified_wallet()
    
    if success:
        print("\\n✅ 테스트 성공! 실제 UTXO 통합을 진행할 수 있습니다.")
    else:
        print("\\n❌ 테스트 실패! 코드를 수정해야 합니다.")

if __name__ == "__main__":
    main()