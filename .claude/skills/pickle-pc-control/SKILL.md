---
name: pickle-pc-control
description: 피클(Pickle) AI 비서나 클로드에서 깃허브 액션 셀프호스티드 러너로 내 윈도우 PC를 원격 조종하는 방법(nahyunseok/pickle-pc-control)을 설치·점검하고 바로 쓰게 안내한다. 러너 설치, 창 없이 백그라운드 자동 실행, pc-commander 워크플로, 화면 캡처(capture.py)·마우스 클릭(click.py), gh workflow run으로 명령 보내기와 결과 읽기, 보안 수칙까지 다룬다. "피클 PC 연동", "폰으로 PC 조종", "PC 원격 제어", "셀프호스티드 러너", "pc-commander", "PC 화면 캡처해줘", "PC에서 명령 실행" 같은 요청에 사용.
---

# 피클 → 내 PC 원격 조종 (pickle-pc-control)

원본: https://github.com/nahyunseok/pickle-pc-control (MIT). 이 스킬 폴더에 원본 파일을 함께 넣어 두었다.
사용자는 비개발자일 수 있으니 한국어로, 한 번에 한 단계씩, 명령은 복사해서 넣을 수 있게 안내한다.

## 0. 구조 한눈에

```
피클 앱/클로드 ──(gh workflow run pc-commander.yml -f command="...")──▶ GitHub (비공개 저장소)
                                                                         │ 작업 대기열
내 윈도우 PC의 셀프호스티드 러너 ◀──(PC가 먼저 바깥으로 접속해서 가져감)──┘
   └─ PowerShell / 파이썬 실행 → 결과는 GitHub 실행 로그에 남음
```

- 포트포워딩·고정 IP 필요 없음(PC가 바깥으로만 연결).
- 별도 LLM API 비용 없음. 깃허브 액션 셀프호스티드 러너는 실행 시간 과금이 없다.
- PC가 켜져 있고 로그인돼 있어야 명령이 실행된다.

| 파일 (이 폴더) | 역할 |
| --- | --- |
| `templates/pc-commander.yml` | 원본 워크플로 (명령 1개 받아 PowerShell로 실행) |
| `templates/pc-commander-safe.yml` | **권장** 보강판: 저장소 주인만 실행, 10분 제한, 한 번에 하나 |
| `scripts/setup-hidden-runner.ps1` | 러너를 창 없이, 로그인 때마다 자동 실행하게 등록 |
| `tools/capture.py` | 화면 캡처 → 1280px JPEG → Base64로 로그에 출력 |
| `tools/click.py` | `python click.py <x> <y> [클릭수]` 좌표 클릭 |
| `requirements.txt` | pillow, mss, pyautogui |

## 1. 꼭 지킬 보안 수칙 (설치 전에 먼저 말해 준다)

1. **저장소는 반드시 Private.** 공개 저장소에 셀프호스티드 러너를 달면 남이 PR로 내 PC에서 코드를 돌릴 수 있다.
2. 이 구조는 "저장소에 쓰기 권한이 있는 사람 = 내 PC를 마음대로 조종"이다. 협업자를 넣지 말고, 토큰(PAT)은 절대 공유·채팅에 붙여 넣지 않는다. 토큰은 필요한 저장소 하나만, 만료일을 짧게.
3. 원본은 `-RunLevel Highest`(관리자 권한)로 러너를 돌린다. 관리자 프로그램을 조종할 필요가 없으면 `scripts/setup-hidden-runner.ps1`에서 `-RunLevel Highest`를 `-RunLevel Limited`로 바꾸라고 권한다.
4. 가능하면 `pc-commander-safe.yml`을 쓴다.
5. 삭제·포맷·종료·결제처럼 되돌리기 어려운 명령은 보내기 전에 사용자에게 한 번 더 확인받는다.

## 2. 상황 확인

| 확인할 것 | 방법 (PC의 PowerShell) | 안 되면 |
| --- | --- | --- |
| 윈도우 PC인가 | - | 이 가이드는 윈도우 전용 |
| 파이썬 | `python --version` | https://www.python.org 설치(“Add to PATH” 체크) |
| 비공개 저장소 | GitHub에서 새 저장소 만들 때 Private 선택 | 기존 저장소면 Settings → Danger Zone → Change visibility |
| 러너 이미 있나 | 저장소 Settings → Actions → Runners 에 초록 `Idle` | 3단계로 |

## 3. 러너 설치 (PC, PowerShell 관리자 권한)

GitHub 저장소 → **Settings → Actions → Runners → New self-hosted runner → Windows** 화면을 열어 둔다. 거기 나오는 토큰을 쓴다(1시간 유효). 최신 버전 번호도 그 화면 명령을 따르는 게 가장 정확하다.

```powershell
cd $env:USERPROFILE
mkdir actions-runner; cd actions-runner
Invoke-WebRequest -Uri "https://github.com/actions/runner/releases/download/v2.338.2/actions-runner-win-x64-2.338.2.zip" -OutFile "runner.zip"
Expand-Archive -Path "runner.zip" -DestinationPath "." ; Remove-Item runner.zip
./config.cmd --url https://github.com/<내아이디>/<저장소이름> --token <발급받은토큰>
```

`config.cmd`가 묻는 질문은 모두 엔터(기본값). "Run as service?"도 N(엔터) — 서비스로 돌리면 화면 캡처·클릭이 안 된다(보이지 않는 세션에서 실행되기 때문). 대신 4단계의 숨김 실행을 쓴다.
반드시 `%USERPROFILE%\actions-runner`에 설치한다(4단계 스크립트가 이 경로를 찾는다).

## 4. 창 없이 자동 실행 등록 (한 번만)

이 스킬 폴더의 `scripts/setup-hidden-runner.ps1`을 PC로 옮긴 뒤 관리자 PowerShell에서:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup-hidden-runner.ps1
```

하는 일: `run-hidden.vbs` 생성 → 작업 스케줄러에 `GitHubRunner-Hidden`(로그인 시 실행) 등록 → 즉시 시작.
확인: 저장소 Settings → Actions → Runners 에서 러너가 초록 **Idle**.

## 5. 워크플로 넣기

저장소에 `.github/workflows/pc-commander.yml` 파일을 만들고 `templates/pc-commander-safe.yml`(권장) 또는 `templates/pc-commander.yml` 내용을 붙여 넣는다. 파일 이름은 `pc-commander.yml`로 둬야 아래 명령이 그대로 맞는다.

## 6. 화면·마우스 도구 설치 (PC)

```powershell
pip install pillow mss pyautogui
mkdir $env:USERPROFILE\pc-tools
```

`tools/capture.py`, `tools/click.py`를 `C:\Users\<계정명>\pc-tools\`에 복사한다.

## 7. 사용법

### 피클 앱에서
깃허브 계정을 연결한 뒤 자연어로 말하면 된다: "PC 화면 캡처해줘", "바탕화면 파일 목록 보여줘", "확인 버튼 눌러줘".

### 직접(또는 클로드가) 명령 보내기 — gh CLI
`gh auth login`이 된 컴퓨터에서:

```bash
REPO=<내아이디>/<저장소이름>
gh workflow run pc-commander.yml -R $REPO -f command="Get-ChildItem $env:USERPROFILE\Desktop"
sleep 5
RUN=$(gh run list -R $REPO -w pc-commander.yml -L 1 --json databaseId -q '.[0].databaseId')
gh run watch $RUN -R $REPO --exit-status
gh run view $RUN -R $REPO --log | sed 's/^[^\t]*\t[^\t]*\t[^ ]* //'
```

주의: 명령 속 `$env:...`는 bash가 먼저 바꿔 버리지 않게 작은따옴표로 감싸거나 `\$`로 쓴다:
`-f command='Get-ChildItem $env:USERPROFILE\Desktop'`

### 자주 쓰는 명령

| 하고 싶은 일 | command 값 |
| --- | --- |
| 화면 캡처 | `python $env:USERPROFILE\pc-tools\capture.py` |
| 좌표 클릭 | `python $env:USERPROFILE\pc-tools\click.py 960 540 1` |
| 더블클릭 | `python $env:USERPROFILE\pc-tools\click.py 960 540 2` |
| 파일 목록 | `Get-ChildItem $env:USERPROFILE\Desktop` |
| 프로그램 실행 | `Start-Process notepad` |
| 실행 중 프로그램 | `Get-Process \| Sort-Object CPU -Descending \| Select-Object -First 10` |
| 디스크 여유 공간 | `Get-PSDrive -PSProvider FileSystem` |
| 배터리·사양 | `Get-CimInstance Win32_Battery`, `Get-CimInstance Win32_ComputerSystem` |
| 글자 입력 | `python -c "import pyautogui; pyautogui.write('hello')"` (한글은 클립보드: `Set-Clipboard '안녕'; python -c "import pyautogui; pyautogui.hotkey('ctrl','v')"`) |
| 단축키 | `python -c "import pyautogui; pyautogui.hotkey('alt','tab')"` |

### 화면 캡처 결과 이미지로 바꾸기
로그의 `===START_SCREEN_CHUNK===`와 `===END_SCREEN_CHUNK===` 사이 줄을 이어 붙여 Base64 디코딩한다.

```bash
gh run view $RUN -R $REPO --log | sed 's/^[^\t]*\t[^\t]*\t[^ ]* //' \
 | sed -n '/===START_SCREEN_CHUNK===/,/===END_SCREEN_CHUNK===/p' | sed '1d;$d' | tr -d '\r\n ' | base64 -d > screen.jpg
```

`INFO:1920x1080`처럼 원래 해상도가 같이 나온다. 이미지는 가로 1280px로 줄어 있으니 클릭 좌표는 **비율로 환산**한다: `실제 x = 이미지 x × (원래 가로 / 1280)`, y도 같은 비율. 클로드가 이미지를 보고 좌표를 고를 때 꼭 이 환산을 하고, 클릭 후 다시 캡처해서 결과를 확인한다.

## 8. 문제 해결

| 증상 | 원인·해결 |
| --- | --- |
| 실행이 "Queued"에서 멈춤 | PC 꺼짐/로그아웃, 러너 Offline. PC에서 `Start-ScheduledTask -TaskName "GitHubRunner-Hidden"` |
| 러너 Offline이 계속 | `%USERPROFILE%\actions-runner\_diag` 로그 확인. 토큰 만료로 등록 실패면 `./config.cmd remove` 후 3단계 다시 |
| `actions-runner 폴더를 찾을 수 없습니다` | 러너가 `%USERPROFILE%\actions-runner`가 아닌 곳에 설치됨. 그 경로로 다시 설치 |
| 스크립트 실행 금지 오류 | `Set-ExecutionPolicy -Scope Process Bypass` 후 다시 |
| 캡처가 검은 화면 / 클릭 안 됨 | 러너가 서비스로 돌거나 화면 잠김. 서비스 해제 후 4단계 방식 사용, 잠금 해제 상태 유지 |
| `python`을 못 찾음 | 러너가 PATH 변경 전에 시작됨. 러너 재시작(작업 스케줄러에서 종료 후 시작) |
| 한글이 깨짐 | 명령 앞에 `[Console]::OutputEncoding=[Text.Encoding]::UTF8;` (safe 템플릿엔 이미 들어 있음) |
| safe 템플릿에서 작업이 Skipped | 실행한 계정이 저장소 주인이 아님. 주인 계정의 토큰으로 실행 |
| `gh workflow run` 404 | 워크플로 파일이 기본 브랜치(main)에 없거나 이름이 다름 |

## 9. 끄기·삭제

```powershell
Unregister-ScheduledTask -TaskName "GitHubRunner-Hidden" -Confirm:$false
cd $env:USERPROFILE\actions-runner; ./config.cmd remove --token <Runners 화면의 제거 토큰>
```
그리고 피클 앱/`gh`에 준 토큰을 GitHub Settings → Developer settings 에서 폐기한다.
