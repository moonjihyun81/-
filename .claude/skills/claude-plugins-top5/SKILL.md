---
name: claude-plugins-top5
description: Claude Code 공식 마켓 플러그인 5종(claude-code-setup·hookify·commit-commands·playwright·ralph-loop)을 설치·점검하고, 진단 → 규칙 → 구현·검증 → 기록 순서로 한 작업에 연결해 쓴다. "플러그인 top5", "추천 플러그인 설치", "hookify로 파일 막기", ".env 수정 막기", "커밋·PR 자동", "playwright로 화면 검사", "ralph loop", "반복해서 완성시켜" 같은 요청에 사용.
---

# Claude Code 플러그인 Top 5 실전

출처: 신영선 「Claude Code 자동화 실전 가이드북」(2026.10.23, Anthropic·Microsoft 공식 자료 기반).
사용자는 비개발자일 수 있으니 한국어로, 한 번에 한 단계씩, 명령은 복사해서 넣을 수 있게 안내한다.
다섯 개를 한꺼번에 켜지 말고 **지금 막힌 지점에 맞는 하나부터** 적용한다.

## 0. 어떤 도구를 고를까

| 막힌 지점 | 도구 | 하는 일 | 오해하기 쉬운 점 |
| --- | --- | --- | --- |
| 뭘 자동화할지 모름 | `claude-code-setup` | 프로젝트를 읽고 MCP·훅·스킬 추천 | **추천만** 한다. 설정 파일은 안 바뀐다 |
| 중요한 파일이 자꾸 바뀜 | `hookify` | 말로 한 규칙 → 훅 규칙 파일 | 기본 action은 `warn`(알림). 막으려면 `block` |
| 커밋·PR이 귀찮음 | `commit-commands` | 커밋 / 푸시 / PR 생성 | `/commit`만으로는 푸시·PR 안 됨 |
| 화면이 진짜 되는지 모름 | `playwright` (MCP) | AI가 브라우저를 열고 입력·클릭 | MCP는 탐색, 반복 검사 파일은 Playwright Test(별개) |
| 끝까지 반복해서 완성 | `ralph-loop` | Stop 훅이 같은 요청을 다시 넣음 | 완료 보장 아님. 상한 도달 ≠ 성공 |

실제 작업 순서: **진단(setup) → 규칙(hookify) → 구현·검증(ralph + playwright) → 기록(commit)**.

## 1. 준비물 확인 (터미널)

```
claude --version
git --version
node --version      # Playwright MCP: 18 이상
python3 --version   # Hookify: 3.7 이상
gh --version        # PR 생성 시 필요
```

없는 도구는 공식 안내대로 설치하고 새 터미널을 연다. 모든 장에 다 필요한 건 아니다.
`/`로 시작하는 명령은 **Claude Code 대화창**, 나머지는 **터미널**에 입력한다.

## 2. 설치 (프로젝트 폴더 터미널, 한 줄씩)

```
claude plugin install claude-code-setup@claude-plugins-official --scope local
claude plugin install hookify@claude-plugins-official --scope local
claude plugin install commit-commands@claude-plugins-official --scope local
claude plugin install playwright@claude-plugins-official --scope local
claude plugin install ralph-loop@claude-plugins-official --scope local
```

- 범위: `local`(나만·이 저장소) / `user`(내 모든 프로젝트) / `project`(팀과 공유). 연습은 `local`.
- 공식 마켓이 안 보이면: `/plugin marketplace add anthropics/claude-plugins-official`
- 설치 후 Claude Code 재시작 또는 `/reload-plugins` → `/plugin`의 Installed·Errors 확인 → `/help`에 명령 확인 → `/mcp`에 playwright 연결 확인.
- 명령은 충돌을 피해 `/플러그인:명령` 형태로 쓴다. 이름이 다르면 `/help`에 보이는 이름이 우선.
- 플러그인은 내 컴퓨터에서 도는 도구라 핸드폰 앱에선 설치할 수 없다.

## 3. 5위 · claude-code-setup (진단)

그대로 보낼 요청:
```
이 프로젝트에 맞는 Claude Code 자동화를 추천해 줘.
먼저 README, 의존성 파일, 테스트·포맷 설정을 읽어 줘.
각 추천에 근거 파일 경로, 줄어드는 반복 작업,
필요한 설치와 권한, 적용 후 확인 방법을 적어 줘.
관련 있는 분류별로 우선순위가 높은 1–2개만 골라 줘.
이번에는 파일을 만들거나 수정하지 마.
```
- 좋은 추천 = "왜 필요한가"에 **파일 경로와 실제 작업**이 연결됨. 근거가 없으면 "실제 파일을 확인하고 다시 추천해 줘".
- 웹 UI가 없는데 Playwright를 추천하면 걸러낸다. 이미 있는 설정을 또 만들라는 추천도 제외.
- 적용은 **별도 요청**: 하나만 골라 "기존 설정과 충돌 확인 → 바꿀 파일·실행 시점·실패 시 동작·되돌리는 법"을 먼저 설명받고, 맞으면 "위에서 선택한 설정을 적용해 줘".
- 확인: 변경 파일 보기 → 약속한 시점에 검사가 도는지 → 정상/의도적 실패 비교 → 해제 시 원래대로 돌아오는지. "검사가 실행됐다" ≠ "검사를 통과했다".

## 4. 4위 · hookify (파일 보호 규칙)

요청:
```
/hookify:hookify 이 프로젝트의 .env와 .env.* 파일을
Edit/Write 도구로 수정하려 하면 action: block으로 막아 줘.
파일 경로를 검사하는 규칙으로 만들고 설명을 보여 줘.
```

생성 파일: 프로젝트 루트 `.claude/hookify.<규칙이름>.local.md`. 예시 `.claude/hookify.protect-env.local.md`:
```
---
name: protect-env
enabled: true
event: file
action: block
conditions:
  - field: file_path
    operator: regex_match
    pattern: (^|[\\/])\.env(?:\.[^\\/]*)?$
---
환경 파일은 이 작업에서 편집하지 않습니다.
필요한 변경은 별도 요청으로 설명해 주세요.
```
- 4요소: `event`(bash=셸 명령 / file=파일 편집 / stop=종료 시점), `conditions`(필드+조건, **여러 개면 모두 만족해야** 발동), `action`(warn|block), `enabled: true`.
- 위 패턴은 `.env`, `.env.local`, `config/.env.production`, `.env.example`에 걸리고 `src/env.ts`엔 안 걸린다. 대소문자 구분.
- 파일 보호는 `file_path` 조건으로. `new_text`로 걸면 파일 보호가 안 된다.
- 규칙 수정은 다음 도구 호출부터 반영(재시작 불필요).
- 한계: Bash 덮어쓰기·외부 프로그램은 file 규칙 밖일 수 있다. "절대 수정 불가"가 필요하면 파일 권한·격리를 따로 설계.
- **시험**: 비밀 없는 가짜 `.env.practice`에 `TEST_ONLY=1` 추가를 요청 → 차단·내용 유지 확인 → `README.practice.md`는 허용되는지 → `.env.example`도 막히는지 확인.
- 관리: `/hookify:list`, `/hookify:configure`, `/hookify:help`.
- 안 막히면: `action`이 warn인지, `enabled`, `event: file`, `file_path` 조건 순서로 점검. 다 막히면 정규식이 너무 넓은지 확인.

## 5. 3위 · commit-commands (기록)

| 명령 | 하는 일 |
| --- | --- |
| `/commit-commands:commit` | 변경·최근 기록을 읽고 메시지 작성해 **로컬 커밋** (관련 파일을 스테이징할 수 있음) |
| `/commit-commands:commit-push-pr` | 커밋 → origin 푸시 → `gh`로 PR 생성 (main이면 작업 브랜치 생성) |
| `/commit-commands:clean_gone` | 원격이 `[gone]`인 로컬 브랜치·worktree **삭제** — 실행 전 `git fetch --prune`, `git branch -vv`, `git worktree list`로 대상 확인 |

커밋 전 요청:
```
이번 작업 범위는 [작업 범위]야.
먼저 git status와 diff를 보고 포함될 파일을 알려 줘.
관계없는 변경과 비밀 파일은 포함하지 마.
실제로 수정한 이유와 동작을 커밋 메시지에 반영해 줘.
```
- 푸시·PR 전 터미널 확인: `git status` / `git branch --show-current` / `git remote -v` / `gh auth status` (로그인: `gh auth login`).
- 좋은 메시지: "fix: 빈 이메일로 문의가 전송되는 문제 수정". 나쁜 메시지: "수정", "완료". 실행 안 한 검사를 "테스트 통과"로 쓰지 않는다.
- 완료 확인 4가지: ① 올바른 저장소 ② 의도한 브랜치 ③ Files changed에 내 작업만 ④ 테스트 기록이 실제와 같은가. PR 링크가 있어도 틀리면 미완료.
- 꼬였을 때: 커밋할 게 없음 → `git status`, `git log -1 --oneline`. 푸시 실패 → 원격·인증·권한 확인 후 **실패한 단계부터** 이어감(재커밋 금지). PR 실패 → 원격 브랜치·기존 PR 확인. 강제 푸시부터 하지 않는다.
- 기록 기본형: `변경: … / 검증: [명령] / [결과] / 미확인: …`

## 6. 2위 · Playwright MCP (브라우저 검증)

- 플러그인으로 설치했다면 `/mcp`에서 확인만. 직접 등록은 `claude mcp add playwright npx @playwright/mcp@latest` — **둘 중 하나만** (중복 등록 금지).
- 개발 서버를 먼저 켜고, 주소·포트는 프로젝트가 실제 출력한 값으로.

첫 연결 시험:
```
Playwright로 http://localhost:3000을 열어 줘.
페이지 제목과 주요 버튼 이름을 알려 줘.
아직 폼 제출이나 파일 변경은 하지 마.
```

검사 요청 (입력과 기대 결과를 쌍으로):
```
Playwright로 [테스트 URL]을 검사해 줘. 실제 발송이 없는 테스트 환경에서만 진행해.
1. 빈 값으로 전송하면 제출이 막히는지
2. 이메일에 abc를 넣으면 막히는지
3. 정상 테스트 값으로 제출하면 완료 표시가 나오는지
4. 새로고침 후 다시 사용할 수 있는지
5. 화면 폭 390px에서 입력란·버튼이 잘리지 않는지
각 항목을 통과/실패/미확인으로 기록하고, 실패 시 재현 순서와 실제 메시지를 남겨 줘.
이번에는 코드를 수정하지 마.
```
- 결과에는 항목별 입력값·기대·실제·판정·증거(스크린샷, 콘솔·네트워크)가 있어야 한다. "괜찮아 보인다"는 통과가 아니다.
- 기대 결과는 요구사항에서 정한다. 없는 오류 문구를 추측해 정답으로 삼지 않는다. 확인 못 하면 "미확인".
- 실제 메일·결제가 연결돼 있으면 테스트 수신처나 모의 응답을 쓴다. 기본 프로필엔 로그인이 남을 수 있으니 테스트 계정 사용, 병렬 시 `--isolated` 고려.
- 반복 검사는 Playwright Test로 파일화: `npm init playwright@latest` → `tests/<이름>.spec.ts` 작성(`getByLabel`, `getByRole`, `expect(...).toBeVisible()`) → `npx playwright test tests/<이름>.spec.ts`. 서버 자동 시작은 `playwright.config.ts`의 `webServer`. 화면에 없는 요소에 맞춰 테스트를 지어내지 않는다.
- 실패 진단 4단계: 접속(서버·포트·인증) / 요소 선택(최신 스냅샷의 역할·접근성 이름) / 동작(버튼 활성·필수값·콘솔·네트워크) / 판정(응답 전에 검사했나 — 대기 시간 대신 대기 조건). 모바일 에뮬레이션 통과 ≠ 실기기 검증.
- 테스트를 통과시키려고 검사 삭제·기대 결과 변경 금지.

## 7. 1위 · Ralph Loop (반복 완성)

종료하려 할 때 Stop 훅이 **같은 프롬프트**를 다시 넣는다. 이전 수정은 파일·Git에 남아 다음 시도의 재료가 된다.
완료 기준이 명확하고 자동 검사 가능한 **작은 구현**에 맞는다("문의 폼 세 검증 사례 통과 + 기존 테스트 유지 시 완료"). 디자인 선택·운영 장애엔 부적합.

1) 프로젝트 루트에 `TASK_BRIEF.md`:
```
목표: [무엇을 고칠지]
범위: [바꿔도 되는 파일]만 변경.
검사: [사례 1] / [사례 2] / [사례 3] + 기존 테스트·빌드 확인. 실제 검사 명령: [명령]
테스트 환경만 사용. 비밀 파일·운영 설정 변경 금지.
테스트 삭제·검증 완화로 통과시키지 말 것.
진행과 실행 결과는 PROGRESS.md에 기록.
전부 충족했을 때만 <promise>DONE</promise> 출력.
막히면 원인·시도한 방법·남은 조건을 기록.
```

2) 대화창에서 (명령과 옵션을 **한 요청**으로):
```
/ralph-loop:ralph-loop "TASK_BRIEF.md를 읽고 수행해. 조건을 모두 검증한 경우에만 완료 신호를 출력해." --max-iterations 5 --completion-promise "DONE"
```
- `--max-iterations`: 반복 상한. **생략하면 무제한**이므로 반드시 넣는다(첫 실행 5회).
- `--completion-promise`: 완료 신호 문자열. 실제로 끝났을 때 `<promise>DONE</promise>` 출력.
- Stop 훅은 신호 문자열만 본다. 품질은 테스트 결과와 변경 내용으로 판단하게 한다.
- 중단: `Esc` → `/ralph-loop:cancel-ralph`. 취소해도 바꾼 파일은 그대로이니 `git diff`로 확인.
- 같은 오류만 반복되면 멈추고 과제를 쪼개거나 환경부터 고친다(인증 대기·네트워크·요구사항 충돌은 횟수로 안 풀림).
- 반복 횟수 ≠ 시간·사용량 상한. 세션 종료·절전·네트워크 단절 후 계속된다고 가정하지 않는다.
- 밤에 맡기기 전: 작은 작업으로 한 번 관찰 → 완료 조건·검사 명령·상한 → 변경 가능 파일·외부 행동 범위(푸시·배포·발송 불필요하면 제외) → 돌아와 직접 확인.
- Windows는 Git Bash 경로 확인. 캐시 파일을 임의로 고치지 않는다.

## 8. 통합 흐름 (예: 문의 폼 하나 완성)

합격 조건을 먼저 적는다 (해석이 갈리는 "보기 좋다" 금지, 실제 개인정보 대신 연습 값):
A 필수 입력 비면 차단 · B 잘못된 이메일 차단 · C 정상 입력 → 완료 표시 · D 390px에서 사용 가능 · E 기존 검사 유지 + 변경 범위 준수.

1. **Setup**으로 진단 → 실제 파일 근거로 자동화 하나 선택.
2. **Hookify**로 `.env` 차단 규칙 → 가짜 파일로 시험.
3. A–E와 검사 명령을 `TASK_BRIEF.md`에 → 직접 구현하거나 **Ralph** 5회 상한.
4. **Playwright**로 A–D 확인, 재사용 검사는 테스트 파일로. 실패 항목만 수정·재검사, E도 확인.
5. `git diff`로 범위 확인 → `/commit-commands:commit`. 원격 준비됐을 때만 `commit-push-pr` → PR 내용 확인.

최종 보고 양식:
```
변경 파일: [경로와 변경 이유]
요구조건 A–E: [각각 통과/실패/미확인]
실행 근거: [명령, 종료 코드, 결과 파일]
브라우저: [입력, 실제 결과, 증거 위치]
남은 문제: [원인, 다음 행동]
기록: [커밋 해시 또는 PR URL]
```
상한 도달이나 PR 링크 생성만으로 합격이 아니다.

## 9. 문제 해결 (설치 → 연결 → 실행 → 판정 순서로, 한 번에 하나씩)

| 증상 | 확인할 것 |
| --- | --- |
| 명령이 안 보임 | `/plugin` Installed·Errors → 재시작 또는 `/reload-plugins` → `/help`에서 접두사 붙은 이름 |
| Setup이 설정을 안 바꿈 | 정상. 추천 후 구현을 따로 요청 |
| Hookify가 못 막음 | `action: block`, `enabled: true`, `event`, `file_path` 조건, 실제로 어떤 도구가 바꿨는지 |
| 커밋은 됐는데 PR 없음 | `/commit`만 실행했는지 → `gh` 인증·원격 브랜치·기존 PR |
| Playwright 접속 실패 | 서버 주소·포트·로그인·브라우저 설치, 도구가 없으면 `/mcp` |
| 브라우저 프로필 사용 중 | 여러 세션이 같은 프로필 공유 → 별도 프로필 / `--isolated` |
| Ralph가 계속 반복 | 완료 신호 문자열·`<promise>` 태그·검사 실패 원인 → 정체 시 중단·분할 |
| Ralph가 멈췄지만 미완료 | 상한 도달 / 훅 오류 / 세션·권한 제약 구분 → `PROGRESS.md` 보고 남은 조건만 재요청 |

진단 요청엔 오류 원문·실행 위치·사용 명령·기대 결과를 넣고, **토큰·환경 변수 값은 넣지 않는다**.

## 10. 7일 연습 (원하면 제안)

1일 프로젝트 파악(실행·검사 명령 한 문단) → 2일 Setup 진단 → 3일 Hookify 차단·허용 시험 → 4일 작은 커밋(가능하면 연습 브랜치 PR) → 5일 MCP로 폼 정상·오류 클릭 → 6일 Playwright Test 파일 하나 → 7일 Ralph 5회 상한.

다음 작업부터 남길 세 줄: `줄이고 싶은 반복 작업 / 이번 작업의 완료 조건 / 완료를 확인할 실제 근거`.

## 핵심 원칙 요약

- Setup은 추천이지 자동 적용이 아니다.
- Hookify 기본은 경고(warn)지 차단(block)이 아니다.
- `/commit`은 푸시·PR을 만들지 않는다.
- Playwright MCP(탐색)와 Playwright Test(반복 검사 파일)는 다르다.
- Ralph의 반복 종료는 품질 보증이 아니다. 상한은 꼭 건다.
- "실행됐다"가 아니라 **결과 파일·종료 코드·기록**으로 완료를 확인한다.

참고(공식): code.claude.com/docs/en/discover-plugins · github.com/anthropics/claude-plugins-official (plugins/claude-code-setup, hookify, commit-commands, ralph-loop) · github.com/microsoft/playwright-mcp · playwright.dev/docs/intro
