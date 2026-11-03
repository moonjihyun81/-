---
name: find-skills
description: 사용자가 "하고 싶은 일"만 말하면 맞는 클로드 스킬을 skills.sh(vercel-labs/skills)에서 찾아 설치 수·출처·깃허브 별로 거른 뒤 한국어로 설명하고, 허락을 받으면 설치까지 한다. find-skills 설치·점검과 설치한 스킬 관리(list·check·update·remove)도 안내한다. "맞는 스킬 찾아줘", "~하는 스킬 있어?", "find-skills 설치", "스킬 추천", "스킬 정리" 같은 요청에 사용.
---

# 스킬 찾아서 설치하기 (find-skills)

스킬은 찾는 게 아니라 **찾게 시키는 것**이다. 사용자는 스킬 이름을 몰라도 된다.
사용자는 비개발자일 수 있으니 한국어로, 한 번에 한 단계씩, 명령은 복사해서 넣을 수 있게 안내한다.

## 1. 준비 확인

| 확인할 것 | 조건 | 안 되면 |
| --- | --- | --- |
| 클로드 코드 | 컴퓨터의 클로드 코드(터미널·데스크톱 앱·에디터) + 유료 구독 또는 Anthropic Console(API) 계정 | 일반 채팅창(웹·앱 대화)에서는 쓸 수 없음 |
| Node.js | `node -v` 결과 v22.20 이상 (`npx` 필요) | nodejs.org 에서 LTS 설치 후 터미널 새로 열기 |

## 2. 원본 find-skills 설치 (사용자가 원할 때)

이 스킬과 별개로, Vercel이 공개한 원본 find-skills(skills.sh 설치 수 1위)를 깔 수도 있다.

```
npx skills add vercel-labs/skills --skill find-skills
```

- 설치 중 에이전트 목록이 나오면 **Claude Code** 선택 → 클로드 코드를 새로 열어(새 세션) 사용.
- 기본은 현재 폴더(프로젝트)에만 설치된다. 모든 폴더에서 쓰려면 `-g`, 에이전트를 바로 정하려면 `-a claude-code`:

```
npx skills add vercel-labs/skills --skill find-skills -g -a claude-code
```

## 3. 찾기 — 하고 싶은 일 → 검색어

1. 사용자의 말을 짧은 영어 검색어로 바꾼다. (예: "우리 가게 홈페이지 디자인 예쁘게" → `web design`, "엑셀 매출 정리" → `excel` / `spreadsheet`, "PDF 계약서 요약" → `pdf`, "사업계획서 PPT" → `pptx` / `presentation`, "인스타 릴스 대본·캡션" → `social media` / `copywriting`)
2. 검색한다:

```
npx skills find <검색어>
```

3. 결과가 엉뚱하면 검색어를 바꿔 한두 번 더 찾는다. 요청이 모호하면 "무엇을 · 어디에 · 어떤 결과로"를 사용자에게 한 번만 묻는다.
4. 필요하면 https://skills.sh 의 스킬 페이지(`skills.sh/<owner>/<repo>/<skill>`)에서 설치 수를 확인한다.

## 4. 거르기 — 추천 전에 품질 확인 (필수)

검색 결과를 그대로 추천하지 않는다. 아래 세 가지를 먼저 본다.

| 기준 | 좋음 | 조심 |
| --- | --- | --- |
| 설치 수 | 1천 회 이상 | 100회 미만 |
| 만든 곳(출처) | anthropics · vercel-labs · microsoft 같은 공식 출처 | 모르는 개인 계정 |
| 깃허브 별 | 100개 이상 | 100개 미만은 의심부터 |

설치 전에는 그 스킬의 `SKILL.md`를 읽고 무슨 일을 하는지 요약하고, 위험한 명령(파일 삭제, 비밀번호·키 전송, 모르는 스크립트 다운로드·실행 등)이 있는지 짚어 준다.

## 5. 보여 주기

기본은 **3개까지**, 설치 수 많은 순. 각 스킬마다:

- 이름 · 하는 일(한국어로 쉽게 한 줄)
- 설치 수 · 만든 곳 · 깃허브 별 (위 기준 통과 여부 ✓/⚠)
- 설치 명령: `npx skills add <owner>/<repo> --skill <스킬이름>`
- skills.sh 링크

맞는 스킬이 없으면 솔직히 없다고 말하고, 클로드가 그냥 직접 도와줄 수 있는지 제안한다.

## 6. 설치 — 사용자가 고른 다음에만

- 사용자가 고르기 전에는 설치하지 않는다.
- 설치 명령 실행 시 클로드 코드가 "Do you want to proceed?"로 묻는다. 내용을 보고 `1. Yes`를 골라야 설치된다고 알려 준다.
- 설치 후 클로드 코드를 새로 열어야(새 세션) 스킬이 잡힌다.

## 7. 설치한 스킬 관리

| 하고 싶은 일 | 명령어 |
| --- | --- |
| 설치한 스킬 목록 | `npx skills list` |
| 업데이트 있는지 확인 | `npx skills check` |
| 업데이트 | `npx skills update` |
| 안 쓰는 스킬 지우기 | `npx skills remove <스킬이름>` |

## 8. 잘 안 될 때

| 이럴 때 | 이렇게 |
| --- | --- |
| npx를 못 찾음 | Node.js(22.20 이상) 설치 후 터미널 새로 열기 |
| 설치했는데 클로드가 안 씀 | 클로드 코드 새로 열기 · "find-skills로 찾아줘"라고 직접 말하기 |
| 결과가 엉뚱함 | 무엇을 · 어디에 · 어떤 결과로를 더 구체적으로 |
| 설명이 영어라 어려움 | 하는 일을 한국어로 쉽게 풀어서 설명 |
| 너무 많이 나옴 | 설치 수 많은 순으로 3개만 |

## 사용자가 복사해 쓰는 문장

```
(하고 싶은 일)을 하고 싶어. 맞는 스킬 찾아줘.
설치 수가 많고 믿을 만한 곳에서 만든 것 위주로 3개만 골라 주고,
각각 무슨 일을 하는지 한국어로 쉽게 설명해 줘.
설치는 내가 고른 다음에 해 줘.
```

```
설치하기 전에 이 스킬 SKILL.md 내용을 요약하고, 위험한 명령이 있는지 봐 줘.
```

## 주의

- 스킬은 남이 만든 지시문과 코드다. 설치 수 · 만든 곳 · 깃허브 별을 확인하는 습관을 안내한다.
- 설치 수·순위·전체 스킬 수는 계속 바뀐다. 숫자를 말할 때는 지금 확인한 값인지 밝힌다.
- find-skills는 Vercel(vercel-labs/skills)이 공개한 스킬이다.

## 공식 링크

- find-skills 페이지: https://skills.sh/vercel-labs/skills/find-skills
- find-skills 설명서: https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md
- skills 명령어: https://github.com/vercel-labs/skills
- 전체 순위: https://skills.sh
- 클로드 코드: https://code.claude.com/docs/en/overview
