#!/usr/bin/env python3
"""
xpub에서 파생된 주소들의 LTM 잔액 확인 도구
"""

import sys
import os
sys.path.insert(0, '/home/junny/electrum')

from electrum import constants
from electrum.keystore import BIP32_KeyStore
from electrum.bitcoin import hash_160
from electrum.segwit_addr import encode_segwit_address, decode_segwit_address
import socket
import json
import hashlib

def xpub_to_addresses(xpub, count=20):
    """xpub에서 주소 파생"""
    
    # LTM 네트워크 설정
    constants.LTMMainnet.set_as_network()
    
    print(f"🔑 xpub 분석 및 주소 파생")
    print("=" * 60)
    print(f"xpub: {xpub}")
    print()
    
    try:
        # BIP32 KeyStore 생성
        keystore = BIP32_KeyStore({
            'xpub': xpub,
            'derivation': '',  # 루트부터 시작
        })
        
        addresses = []
        public_keys = []
        
        print(f"📋 파생된 주소 목록 (처음 {count}개)")
        print(f"   경로: m/0/n (Receiving addresses)")
        print("-" * 80)
        
        for i in range(count):
            # 공개키 파생 (0 = receiving, 1 = change)
            pubkey = keystore.derive_pubkey(0, i)
            
            # bc1 주소 생성
            address = pubkey_to_p2wpkh_address(pubkey)
            
            if address:
                addresses.append(address)
                public_keys.append(pubkey)
                
                print(f"{i+1:2d}. {address}")
                print(f"    공개키: {pubkey}")
                print()
            else:
                print(f"{i+1:2d}. 주소 생성 실패")
        
        return addresses, public_keys
        
    except Exception as e:
        print(f"❌ xpub 처리 오류: {e}")
        import traceback
        traceback.print_exc()
        return [], []

def pubkey_to_p2wpkh_address(pubkey_hex):
    """공개키를 P2WPKH (bc1) 주소로 변환"""
    try:
        # 공개키를 바이트로 변환
        if isinstance(pubkey_hex, str):
            pubkey_bytes = bytes.fromhex(pubkey_hex)
        else:
            pubkey_bytes = pubkey_hex
            
        # 공개키 해시 생성 (HASH160)
        pubkey_hash = hash_160(pubkey_bytes)
        
        # bc1 주소 생성 (Bech32) - LTM은 Bitcoin 호환
        address = encode_segwit_address('bc', 0, pubkey_hash)
        return address
        
    except Exception as e:
        print(f"주소 변환 오류: {e}")
        return None

def address_to_scripthash(address):
    """bc1 주소를 ElectrumX 스크립트해시로 변환"""
    try:
        # segwit 주소 디코딩
        witver, witprog = decode_segwit_address('bc', address)
        
        if witver is None or witprog is None:
            return None
            
        # P2WPKH 스크립트: OP_0 (0x00) + PUSH20 (0x14) + 20바이트 해시
        script = bytes([0, 20]) + bytes(witprog)
        
        # 스크립트 해시 계산 후 뒤집기 (ElectrumX 형식)
        script_hash = hashlib.sha256(script).digest()
        return script_hash[::-1].hex()
        
    except Exception as e:
        print(f"스크립트해시 변환 오류: {e}")
        return None

def check_balance_batch(addresses):
    """여러 주소의 잔액을 배치로 확인"""
    
    host = "ltm-wallet.gnc.ne.kr"
    port = 50008
    
    print(f"\n💰 잔액 확인 중...")
    print(f"서버: {host}:{port}")
    print("-" * 60)
    
    results = []
    total_balance = 0
    
    for i, address in enumerate(addresses):
        print(f"{i+1:2d}. {address}", end=" ")
        
        try:
            # 스크립트해시 변환
            scripthash = address_to_scripthash(address)
            if not scripthash:
                print("❌ 스크립트해시 변환 실패")
                continue
                
            # 서버 연결
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            
            # 잔액 조회 요청
            request = {
                "id": i+1,
                "method": "blockchain.scripthash.get_balance",
                "params": [scripthash]
            }
            
            request_str = json.dumps(request) + "\n"
            sock.send(request_str.encode())
            
            # 응답 받기
            response = b""
            while True:
                try:
                    chunk = sock.recv(1024)
                    if not chunk:
                        break
                    response += chunk
                    if b"\n" in response:
                        break
                except:
                    break
            
            sock.close()
            
            if response:
                response_str = response.decode().strip()
                data = json.loads(response_str)
                
                if "result" in data and isinstance(data["result"], dict):
                    confirmed = data["result"].get('confirmed', 0)
                    unconfirmed = data["result"].get('unconfirmed', 0)
                    total = confirmed + unconfirmed
                    
                    if total > 0:
                        print(f"💰 {total/1e8:.8f} LTM")
                        total_balance += total
                    else:
                        print("💤 0 LTM")
                        
                    results.append({
                        'address': address,
                        'confirmed': confirmed,
                        'unconfirmed': unconfirmed,
                        'total': total
                    })
                else:
                    print("❓ 응답 없음")
            else:
                print("❌ 연결 실패")
                
        except Exception as e:
            print(f"❌ 오류: {e}")
    
    return results, total_balance

def main():
    if len(sys.argv) != 2:
        print("사용법: python3 check_xpub_balance.py <xpub>")
        print("예시: python3 check_xpub_balance.py zpub6msz3PWEjrnvUYwm7B59KMzKB1Lk2Qjc7cXEKuAmCnzsbwZN3DL8gPNwLcYEtwdSR9BFrHUxuh9N6x7rZPxED5YrnHUtXXB7ckyH1HJvKuK")
        sys.exit(1)
    
    xpub = sys.argv[1].strip()
    
    # xpub 유효성 간단 체크
    if not (xpub.startswith('xpub') or xpub.startswith('ypub') or xpub.startswith('zpub')):
        print("❌ 올바른 xpub/ypub/zpub 형식이 아닙니다")
        sys.exit(1)
    
    # 주소 파생
    addresses, public_keys = xpub_to_addresses(xpub, count=20)
    
    if not addresses:
        print("❌ 주소 파생 실패")
        sys.exit(1)
    
    # 잔액 확인
    results, total_balance = check_balance_batch(addresses)
    
    # 결과 요약
    print(f"\n📊 잔액 확인 결과")
    print("=" * 50)
    
    active_addresses = [r for r in results if r['total'] > 0]
    
    if active_addresses:
        print(f"💰 활성 주소: {len(active_addresses)}개")
        for result in active_addresses:
            print(f"   {result['address']}: {result['total']/1e8:.8f} LTM")
        
        print(f"\n💎 총 잔액: {total_balance/1e8:.8f} LTM")
    else:
        print("💤 모든 주소가 비어있습니다 (잔액 0)")
    
    print(f"🔍 확인한 주소: {len(addresses)}개")
    print(f"📡 서버: ltm-wallet.gnc.ne.kr:50008")

if __name__ == "__main__":
    main()