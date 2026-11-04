---
name: markitdown
description: 마이크로소프트의 무료 문서 변환 도구 MarkItDown(microsoft/markitdown)으로 PDF·워드·파워포인트·엑셀 등을 마크다운으로 바꿔 클로드에 넣을 때 토큰을 줄이고 답변을 정확하게 만든다. 설치, 파일·폴더 변환, markitdown-mcp로 클로드 코드·데스크톱 연결, 마크다운이 손해인 경우까지 안내한다. "PDF 토큰 줄이기", "마크잇다운", "markitdown 설치", "문서 마크다운으로 변환", "엑셀을 클로드에" 같은 요청에 사용.
---

# MarkItDown으로 문서를 마크다운으로 바꿔 넣기

마이크로소프트가 공개한 무료 오픈소스(MIT) 변환 도구다. 저장소: https://github.com/microsoft/markitdown
사용자는 비개발자일 수 있으니 한국어로, 한 번에 한 단계씩, 명령은 복사해서 넣을 수 있게 안내한다.

## 0. 먼저 판단: 마크다운이 맞는 문서인가

| 문서 성격 | 권장 | 예시 |
| --- | --- | --- |
| **읽어야 하는** 문서 | 마크다운으로 변환 | 계약서, 매뉴얼, 보고서, 정책 문서, 단가표 |
| **봐야 하는** 문서 | PDF·이미지 그대로 | 차트 모양, 디자인 시안, 사진 속 내용, 손글씨, 스캔본 |

왜 줄어드나: 클로드는 PDF를 페이지마다 글자 + 페이지 이미지로 함께 처리한다. 글자만 페이지당 보통 1,500~3,000 토큰이고 여기에 이미지 토큰이 더해진다. 마크다운은 제목(`#`)·목록·표 구조만 남기고 이미지 토큰이 빠진다.
줄어드는 정도는 문서마다 다르다. 글자 위주일수록 크게 줄고, 표·그래프·사진이 핵심이면 덜 줄어든다. 확실히 알고 싶으면 6단계 방법으로 직접 비교한다.

## 1. 상황 확인

| 확인할 것 | 방법 | 안 되면 |
| --- | --- | --- |
| 파이썬 버전 | `python3 --version` (윈도우: `python --version`) | 3.10~3.14가 필요. https://www.python.org 에서 설치 |
| 이미 설치됐는지 | `markitdown --help` | 2단계로 |

## 2. 설치

가상환경에 설치하면 컴퓨터가 깔끔하게 유지된다(권장).

```bash
python3 -m venv .venv
source .venv/bin/activate          # 윈도우: .venv\Scripts\activate
pip install 'markitdown[all]'
```

필요한 형식만 설치하려면: `pip install 'markitdown[pdf,docx,pptx,xlsx]'`
`[all]` 없이 `pip install markitdown`만 하면 PDF·워드 등이 변환되지 않으니 주의한다.

## 3. 변환

파일 하나:

```bash
markitdown 정산정책.pdf -o 정산정책.md
markitdown 사업계획서.pptx -o 사업계획서.md
markitdown 거래처단가표.xlsx -o 거래처단가표.md
```

폴더 통째로:

```bash
# 맥 · 리눅스
for f in *.pdf; do markitdown "$f" -o "${f%.pdf}.md"; done
```

```powershell
# 윈도우 (PowerShell)
Get-ChildItem *.pdf | ForEach-Object { markitdown $_.FullName -o ($_.BaseName + ".md") }
```

지원 형식: PDF, 워드, 파워포인트, 엑셀, 이미지(메타데이터·글자 인식), 음성(받아쓰기), HTML, CSV, JSON, XML, ZIP(안의 파일 전부), 유튜브 링크, 전자책(EPUB).

사용자가 명령어를 어려워하면 클로드 코드가 대신 실행한다. 예: "markitdown 설치해주고, 이 폴더의 PDF·워드·엑셀 파일 전부 마크다운으로 변환해서 md 폴더에 저장해줘. 변환 전후 파일 크기도 표로 보여줘."
이때 원본 파일은 지우거나 덮어쓰지 않고, 결과는 별도 폴더(`md/`)에 저장한다.

## 4. MCP로 클로드에 연결

연결해 두면 파일 경로나 링크만 알려줘도 클로드가 변환해서 읽는다.

```bash
pip install markitdown-mcp
```

**클로드 코드**:

```bash
claude mcp add markitdown -- markitdown-mcp
# 모든 프로젝트에서 쓰려면
claude mcp add -s user markitdown -- markitdown-mcp
# 확인
claude mcp list
```

**클로드 데스크톱**: 설정 → 개발자 → 설정 파일 편집(`claude_desktop_config.json`)에 아래를 추가하고 앱을 재시작한다. 이미 `mcpServers`가 있으면 그 안에 `markitdown` 항목만 추가한다(기존 항목을 지우지 않는다).

```json
{ "mcpServers": { "markitdown": { "command": "markitdown-mcp" } } }
```

가상환경에 설치했다면 `command`에 `markitdown-mcp`의 전체 경로(`which markitdown-mcp` 결과)를 넣어야 앱이 찾는다.

사용 예:
- 내 컴퓨터 파일: "file:///Users/내이름/Documents/정산정책.pdf 이 파일 마크다운으로 변환해서 읽고, 수수료·정산 주기·페널티 조항만 표로 정리해줘."
- 웹 문서: "https://[공지·약관 페이지 주소] 이 페이지 마크다운으로 바꿔서 핵심만 5줄로 요약해줘."

알아둘 것:
- MCP는 클로드에게 변환 도구를 쥐여주는 것이다. 채팅창에 끌어다 놓은 파일을 자동으로 바꾸지는 않는다. 경로(`file://`)나 링크를 알려줘야 변환한다.
- 이 서버에는 인증 기능이 없다. 내 컴퓨터에서만 쓰고 외부에 열지 않는다.

## 5. 이런 문서는 이렇게 시킨다 (쇼핑몰 예시)

| 문서 | 요청 예 |
| --- | --- |
| 플랫폼 정산 정책 PDF | "수수료 · 정산 주기 · 페널티만 표로, 지난 버전과 달라진 점도" |
| 거래처 단가표 엑셀 | "상품별 단가를 지난달과 비교해서 오른 것만 정리" |
| 사업계획서 · 제안서 PPT | "슬라이드별 핵심 한 줄 + 빠진 내용 지적" |
| 세무 · 노무 안내문 | "내가 이번 달에 해야 할 일만 날짜순으로" |
| 상품 매뉴얼 · 케어라벨 문서 | "상세페이지에 넣을 세탁·관리법 문구로 다듬어줘" |

## 6. 주의할 점

- **직접 비교해 보기**: 같은 문서를 PDF로 한 번, 마크다운으로 한 번 올려 사용량을 비교한다. 내 문서에서 얼마나 줄어드는지 바로 보인다.
- **스캔 PDF·사진 속 글자**: 기본 설치로는 거의 읽히지 않는다. 이미지 속 글자까지 뽑으려면 OCR 플러그인(`markitdown-ocr`)과 별도 AI(비전 모델) API 키가 필요하다. 이런 문서는 PDF 그대로 올리는 편이 쉽다.
- **변환 결과 훑어보기**: 복잡한 표나 2단 편집 문서는 순서가 섞일 수 있다. 숫자가 중요한 문서는 원본과 대조한다.
- **개인정보**: 변환은 내 컴퓨터에서 하지만, 결과를 어디에 올릴지는 사용자의 선택이다. 고객 주소·연락처가 든 파일은 필요한 부분만 남기고 올린다.

한 줄 정리: "읽어야 하는" 문서는 마크다운으로, "봐야 하는" 문서는 PDF 그대로.

출처: https://github.com/microsoft/markitdown (markitdown 0.1.9, markitdown-mcp 0.0.1a8, markitdown-ocr 0.1.2 기준), 원본 가이드 "MarkItDown_guide.pdf"(Online_Techtree)
