---
name: codex-pair
description: 클로드와 OpenAI 코덱스(챗GPT)를 한 화면에서 같이 쓰도록 공식 플러그인 openai/codex-plugin-cc를 설치·점검하고, 초안(클로드) → 검수(코덱스) → 마무리(클로드) 순서로 역할을 나눠 작업한다. "코덱스 설치", "챗GPT로 검수", "codex review", "/codex 명령이 안 보여" 같은 요청에 사용.
---

# 클로드 + 코덱스 같이 쓰기

OpenAI가 낸 Claude Code용 공식 플러그인 `codex@openai-codex`(저장소 `openai/codex-plugin-cc`)를 쓴다.
사용자는 비개발자일 수 있으니 한국어로, 한 번에 한 단계씩, 명령은 복사해서 넣을 수 있게 안내한다.

## 1. 상황 확인

| 확인할 것 | 조건 | 안 되면 |
| --- | --- | --- |
| 클로드 요금제 | Pro·Max·Team·Enterprise | 무료 요금제는 플러그인 불가 → 업그레이드부터 |
| 챗GPT 계정 | 무료 포함 계정 또는 OpenAI API 키 | 사용량은 코덱스 한도에서 차감(클로드와 별도) |
| Node.js | `node -v` 결과 v18.18 이상 | nodejs.org 에서 LTS 설치 |
| 회사 계정 | 관리자가 허용한 마켓플레이스만 추가 가능 | 거절되면 조직 관리자에게 `openai/codex-plugin-cc` 허용 요청 |

플러그인은 내 컴퓨터에서 도는 도구다. 핸드폰 앱에서는 설치할 수 없으니 데스크톱 앱 코드 탭이나 터미널 Claude Code에서 진행하라고 안내한다.

## 2. 설치

**터미널 Claude Code**: 한 줄씩 차례로 입력한다.

```
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

`/reload-plugins`를 빼면 `/codex` 명령이 보이지 않는다.

**클로드 데스크톱 앱**: 사용자 지정 → 플러그인 → 추가 → 마켓플레이스 추가 → 저장소에서 추가
(Customize → Plugins → Add → Add marketplace → Add from a repository)에 `openai/codex-plugin-cc`를 넣는다.
이어서 둘러보기(Discover) 탭에서 `codex`(출처 `openai-codex`)를 추가하고, 코드 탭에서 새 창을 열어 폴더를 고른 뒤 `/codex:setup`을 입력한다.

## 3. 셋업 점검

- `/codex:setup`: 코덱스 설치 여부와 로그인 상태를 보여 준다. 코덱스가 없으면 설치를 제안하니 허용한다(직접 설치: `npm install -g @openai/codex`).
- 로그인이 안 됐으면 `!codex login` → 챗GPT 계정으로 로그인 → `/codex:setup`을 다시 실행한다.
- **리뷰 게이트(`--enable-review-gate`)는 켜지 말 것.** 클로드와 코덱스가 계속 주고받으면서 사용량이 빠르게 닳는다. 사용자가 직접 지켜볼 때만 예외로 켠다.

## 4. 역할 나누기

순서는 항상 같다. 클로드가 만들고, 코덱스는 읽기만 하며 문제를 짚고, 클로드가 맞는 것만 골라 고친다.

| 하고 싶은 일 | 명령 / 말 |
| --- | --- |
| 초안 (클로드) | 예: "신제품 랜딩페이지 초안 만들어줘. 대상 30대 직장인, 목표 상담 신청, 모바일 기준." |
| 검수 (코덱스, 읽기 전용) | `/codex:review` · 브랜치 비교: `/codex:review --base main` |
| 설계부터 따져보기 | `/codex:adversarial-review <따져볼 관점>` |
| 막힌 문제 넘기기 | `/codex:rescue <문제>. 고치기 전에 원인부터 알려줘.` |
| 오래 걸리는 작업 | `--background`를 붙이고 `/codex:status`로 확인, `/codex:result`로 결과, `/codex:cancel`로 취소 |
| 코덱스로 대화 넘기기 | `/codex:transfer` → 출력된 `codex resume <id>`로 이어서 작업 |
| 마무리 (클로드) | "코덱스가 짚은 것 중 맞는 것만 고쳐줘. 고친 이유도 한 줄씩 적어줘." |

원칙:
- 검수는 초안이 끝난 뒤 **한 번만** 한다. 코덱스 사용량을 아낀다.
- 고치는 일은 클로드나 `/codex:rescue` **한쪽에만** 맡긴다. 둘 다 고치면 서로의 수정을 덮어쓴다.
- 코덱스에는 "고치지 말고 문제만 목록으로 짚어줘"처럼 검수와 수정을 나눠서 시킨다.
- 바꿀 때는 한 번에 하나씩 한다("3번째 문제만 고쳐줘", "디자인은 그대로 두고 문구만"). 그래야 무엇 때문에 좋아졌는지 알 수 있다.
- 처음에는 작은 작업물 하나로 시험한다. 파일이 많을수록 검수가 오래 걸린다.

## 5. 문제 해결

- **"검토할 변경 사항이 없다"**: 검수는 git 변경 내용을 읽는다. 폴더에서 `git init` 후 커밋하거나 파일을 수정한 뒤 다시 실행한다.
- **`/codex` 명령이 안 보임**: 터미널이면 `/reload-plugins`, 앱이면 코드 탭에서 새 창을 연다.
- **아무 반응이 없음**: `/codex:setup`으로 로그인 상태부터 확인한다.
- **한도 초과**: 챗GPT 계정의 코덱스 사용 한도를 확인한다(https://developers.openai.com/codex/pricing).

출처: https://github.com/openai/codex-plugin-cc (플러그인 v1.0.6 기준), https://support.claude.com/en/articles/13837440-use-plugins-in-claude
