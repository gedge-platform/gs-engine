# sockperfTester

sockperf 기능테스트 프로그램

```shell
# on Linux
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# setting
vim settings.py

# run
python main.py
```

### settgins.py 설정

- Server IP
  - Client가 접속할 Servier IP 입력
- Port
  - Client가 접속할 Servier Port 입력
  - Server/Client 가 같은 Port 사용
- Client IP
  - Client가 Server로의 접속에 사용할 IP
- ITERATION
  - 테스트 반복 횟 수
- MESSAGE_SIZE
  - 전송 Message Size 별로 테스트를 수행할 수 있음
- TEST_TYPE
  - sockperf에서 지원하는 TEST 유형 작성
  - under-load, ping-pong, throughput

### 정보
- `mps=max` 옵션은 default
- tcp 시험의 경우, TCP Protocol의 `Time_Wait`을 기다리기 위해, 실행 간격을 10초 단위로 조정
- 실제 명령어는 SockperfTester의 self.command 참조


