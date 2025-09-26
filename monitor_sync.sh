#!/bin/bash

# LTM 동기화 진행 모니터링
echo "🔄 LTM 동기화 진행 모니터링"
echo "================================"
echo "Ctrl+C로 종료"
echo ""

while true; do
    # 현재 시간
    timestamp=$(date "+%H:%M:%S")
    
    # getinfo 실행하고 결과 파싱
    info=$(cd /home/junny/electrum && ./run_electrum_ltm getinfo 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        # JSON에서 필요한 값 추출
        local_height=$(echo "$info" | grep -o '"blockchain_height": [0-9]*' | cut -d' ' -f2)
        server_height=$(echo "$info" | grep -o '"server_height": [0-9]*' | cut -d' ' -f2)
        connected=$(echo "$info" | grep -o '"connected": [a-z]*' | cut -d' ' -f2)
        
        if [[ "$local_height" != "" && "$server_height" != "" ]]; then
            remaining=$((server_height - local_height))
            
            if [[ $remaining -le 0 ]]; then
                echo "[$timestamp] ✅ 동기화 완료! 로컬: $local_height, 서버: $server_height"
                break
            else
                percentage=$((local_height * 100 / server_height))
                echo "[$timestamp] 🔄 동기화 중... $local_height/$server_height ($percentage%) - 남은 블록: $remaining (연결: $connected)"
            fi
        else
            echo "[$timestamp] ⏳ 네트워크 연결 대기중..."
        fi
    else
        echo "[$timestamp] ❌ Electrum 응답 없음"
    fi
    
    sleep 3
done

echo ""
echo "✅ 동기화 완료! GUI에서 최신 블록체인 정보를 확인할 수 있습니다."