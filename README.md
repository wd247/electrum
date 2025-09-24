# Electrum LTM - Lightweight LTM (Laptop Mining) client

이 프로젝트는 원본 Electrum을 기반으로 LTM (Laptop Mining) 코인을 지원하도록 수정된 버전입니다.

```
Licence: MIT Licence
Original Author: Thomas Voegtlin
Language: Python (>= 3.10)
Homepage: https://electrum.org/
LTM Fork: https://github.com/wd247/electrum
```

## LTM 네트워크 정보

- **코인명**: LTM (Laptop Mining)
- **알고리즘**: SHA-256d (Bitcoin 호환)
- **블록 시간**: 1분
- **난이도 조정**: 적응형 (매 블록마다)
- **주소 형식**: bc1 (Bitcoin 호환 Bech32)
- **네트워크**: 메인넷 전용 (테스트넷 없음)
- **제네시스 블록**: `20a1cb14930e9cc8f0b7e6872b0630a86c135a6903aec70b6c4e63457c7948a8`
- **프로젝트 시작**: "David project begins"

## LTM 네트워크 서버

- **메인 서버**: ltm-wallet.gnc.ne.kr:50008 (TCP), :50009 (SSL)
- **백업 서버**: 54.169.107.75:50008
- **프로토콜**: ElectrumX 1.16.0

[![Build Status](https://api.cirrus-ci.com/github/spesmilo/electrum.svg?branch=master)](https://cirrus-ci.com/github/spesmilo/electrum)
[![Test coverage statistics](https://coveralls.io/repos/github/spesmilo/electrum/badge.svg?branch=master)](https://coveralls.io/github/spesmilo/electrum?branch=master)
[![Help translate Electrum online](https://d322cqt584bo4o.cloudfront.net/electrum/localized.svg)](https://crowdin.com/project/electrum)


## LTM 지갑 빠른 시작

### LTM 전용 실행 스크립트

LTM 네트워크 전용으로 Electrum을 실행하려면:

```bash
# 간단 실행 (LTM 네트워크만)
$ ./run_electrum_ltm_simple

# 완전한 LTM 설정으로 실행  
$ ./run_electrum_ltm
```

### LTM 잔액 조회 도구

특정 bc1 주소의 LTM 잔액을 명령줄에서 조회:

```bash
$ python3 ltm_balance_proper.py bc1qvhrr2sufl4q0xukh60fa6k7nq4gchjn5tz45da
```

### 주요 변경사항

1. **네트워크 설정**: Bitcoin에서 LTM으로 완전 변경
2. **주소 형식**: Bitcoin 호환 bc1 주소 사용
3. **난이도 조정**: 1분 블록에 맞춘 적응형 알고리즘
4. **테스트넷 제거**: 메인넷만 지원
5. **서버 설정**: LTM 전용 ElectrumX 서버

## Getting started

Electrum LTM은 순수 Python이며, 대부분의 종속성도 그렇지만 모든 것이 그런 것은 아닙니다. 
다음 섹션에서는 소스에서 실행하는 방법을 설명하지만 여기에 간단한 설명이 있습니다:

```
$ sudo apt-get install libsecp256k1-dev
$ ELECTRUM_ECC_DONT_COMPILE=1 python3 -m pip install --user ".[gui,crypto]"
```

### Not pure-python dependencies

#### Qt GUI

If you want to use the Qt interface, install the Qt dependencies:
```
$ sudo apt-get install python3-pyqt6
```

#### libsecp256k1

For elliptic curve operations,
[libsecp256k1](https://github.com/bitcoin-core/secp256k1)
is a required dependency.

If you "pip install" Electrum, by default libsecp will get compiled locally,
as part of the `electrum-ecc` dependency. This can be opted-out of,
by setting the `ELECTRUM_ECC_DONT_COMPILE=1` environment variable.
For the compilation to work, besides a C compiler, you need at least:
```
$ sudo apt-get install automake libtool
```
If you opt out of the compilation, you need to provide libsecp in another way, e.g.:
```
$ sudo apt-get install libsecp256k1-dev
```

#### cryptography

Due to the need for fast symmetric ciphers,
[cryptography](https://github.com/pyca/cryptography) is required.
Install from your package manager (or from pip):
```
$ sudo apt-get install python3-cryptography
```

#### hardware-wallet support

If you would like hardware wallet support,
[see this](https://github.com/spesmilo/electrum-docs/blob/master/hardware-linux.rst).


### LTM 종속성 설치

LTM Electrum을 실행하기 전에 추가 종속성을 설치해야 합니다:

```bash
# 필요한 패키지 설치
$ python3 -m pip install --user --break-system-packages aiorpcx
$ python3 -m pip install --user --break-system-packages electrum_aionostr
$ python3 -m pip install --user --break-system-packages nostr-sdk
```

### tar.gz에서 실행

공식 패키지(tar.gz)를 다운로드한 경우, 시스템에 설치하지 않고도 루트 디렉터리에서
Electrum LTM을 실행할 수 있습니다; 모든 순수 python 종속성은 'packages' 디렉터리에 포함되어 있습니다.

LTM 네트워크로 실행하려면:
```
$ ./run_electrum_ltm
```

기본 Electrum으로 실행하려면:
```
$ ./run_electrum
```

시스템에 Electrum을 설치할 수도 있습니다:
```
$ sudo apt-get install python3-setuptools python3-pip
$ python3 -m pip install --user .
```

이렇게 하면 'packages' 디렉터리를 사용하는 대신 Electrum에서 사용하는 Python 종속성을
다운로드하여 설치합니다. 또한 `~/.local/bin`에 `electrum`이라는 실행 파일이 생성되므로
`PATH` 변수에 있는지 확인하십시오.


### LTM 개발 버전 (git clone)

_(OS별 지침은 [Windows](contrib/build-wine/README_windows.md),
[macOS](contrib/osx/README_macos.md)를 참조하세요)_

LTM 포크를 GitHub에서 체크아웃:
```
$ git clone https://github.com/wd247/electrum.git
$ cd electrum
$ git submodule update --init
```

종속성 설치:
```
$ python3 -m pip install --user -e .
$ python3 -m pip install --user --break-system-packages aiorpcx electrum_aionostr nostr-sdk
```

번역 파일 생성 (선택사항):
```
$ sudo apt-get install gettext
$ ./contrib/locale/build_locale.sh electrum/locale/locale electrum/locale/locale
```

LTM Electrum 시작:
```
$ ./run_electrum_ltm
```

기본 Electrum 시작:
```
$ ./run_electrum
```

### LTM 테스트 실행

LTM 관련 테스트 실행:
```
$ python3 test_ltm_bc1_format.py      # bc1 주소 형식 테스트
$ python3 test_ltm_mainnet_only.py    # 메인넷 전용 테스트
$ python3 test_ltm_wallet.py          # LTM 지갑 기능 테스트
```

### 테스트 실행

일반 단위 테스트를 `pytest`로 실행:
```
$ pytest tests -v
```

특정 파일을 실행하려면 다음과 같이 직접 지정:
```
$ pytest tests/test_bitcoin.py -v
```

LTM 전용 테스트:
```
$ python3 test_ltm_bc1_format.py      # LTM bc1 주소 형식 검증
$ python3 test_ltm_mainnet_only.py    # 메인넷 전용 설정 검증  
$ python3 test_ltm_wallet.py          # LTM 지갑 기능 테스트
```

LTM 네트워크 연결 테스트:
```
$ python3 ltm_auth_test.py            # 서버 연결 및 인증 테스트
$ python3 ltm_balance_proper.py <주소>  # 실제 잔액 조회 테스트
```

## Creating Binaries

- [Linux (tarball)](contrib/build-linux/sdist/README.md)
- [Linux (AppImage)](contrib/build-linux/appimage/README.md)
- [macOS](contrib/osx/README.md)
- [Windows](contrib/build-wine/README.md)
- [Android](contrib/android/Readme.md)


## LTM 설정 파일

LTM 네트워크와 관련된 주요 파일들:

- **`electrum/constants.py`**: LTM 네트워크 상수 및 설정
- **`electrum/chains/ltm/`**: LTM 체인 관련 설정
  - `servers.json`: LTM 서버 목록
  - `checkpoints.json`: 체크포인트 데이터
  - `fallback_lnnodes.json`: 라이트닝 네트워크 노드 (빈 파일)
- **`electrum/ltm_blockchain.py`**: LTM 블록체인 로직
- **`electrum/ltm_version.py`**: LTM 버전 정보
- **`run_electrum_ltm`**: LTM 전용 실행 스크립트
- **`run_electrum_ltm_simple`**: LTM 간단 실행 스크립트

## 주요 구현 특징

1. **Bitcoin 호환성**: bc1 주소 형식으로 Bitcoin과 호환
2. **적응형 난이도**: 1분 블록에 최적화된 난이도 조정
3. **프라이빗 노드 지원**: 인증이 필요한 프라이빗 ElectrumX 서버 지원
4. **메인넷 전용**: 테스트넷 없는 단순한 네트워크 구조
5. **실시간 잔액 조회**: 명령줄 도구로 즉시 잔액 확인

## Contributing

소프트웨어 테스트, 버그 보고 또는 수정, 풀 리퀘스트 및 최근 변경 사항 검토, 테스트 작성,
또는 미해결 문제 해결에 대한 모든 도움을 환영합니다.

LTM 관련 기능 구현이나 코드베이스 개선/리팩토링도 물론 환영하지만, 특히 큰 변경사항의 경우
헛된 노력을 피하기 위해 이슈 트래커에서 먼저 논의하는 것을 권장합니다.

**LTM 포크**: [GitHub](https://github.com/wd247/electrum)
**원본 Electrum**: [GitHub](https://github.com/spesmilo/electrum)

원본 Electrum 개발에 대한 대부분의 커뮤니케이션은 Libera Chat의 `#electrum` 채널에서 IRC를 통해 이루어집니다.
IRC에 참여하는 가장 쉬운 방법은 웹 클라이언트 [web.libera.chat](https://web.libera.chat/#electrum)를 사용하는 것입니다.

번역 개선은 [Crowdin](https://crowdin.com/project/electrum)에서 해주세요.
