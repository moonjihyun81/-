---
name: fashn-vton
description: FASHN AI의 오픈소스 가상 피팅 모델 FASHN VTON v1.5(fashn-AI/fashn-vton-1.5, Apache-2.0·상업 사용 가능·마스크 불필요·가벼움)로 "사람 사진 + 옷 사진 → 그 옷을 입은 사진"을 만든다. 설치, 가중치 다운로드, 파이썬·CLI 실행, 옵션(tops/bottoms/one-pieces, 모델컷/누끼컷, 스텝·시드) 고르기, GPU가 없을 때 대안(허깅페이스 Spaces·FASHN API), 라이선스 주의점까지 안내한다. "가상 피팅", "virtual try-on", "VTON", "fashn", "옷 입혀보기", "상품 사진을 모델에 입혀줘", "룩북 피팅컷" 같은 요청에 사용. 비상업 연구용·로고 디테일 비교는 idm-vton 스킬.
---

# FASHN VTON v1.5 — 옷 사진을 사람 사진에 입히기

출처: https://github.com/fashn-AI/fashn-vton-1.5 (Apache-2.0, 2026 공개 v1.5.0)
한 줄 요약: **사람 사진 1장 + 옷 사진 1장 → 그 옷을 입은 사실적인 사진.** 마스크(옷 영역 칠하기)를 직접 만들 필요 없이 픽셀 공간에서 바로 생성한다.

사용자는 비개발자일 수 있으니 한국어로, 한 단계씩, 명령어는 복사해서 쓸 수 있게 준다.

## 0. 먼저 고르기: 어디서 돌릴까

| 방법 | 필요한 것 | 언제 |
| --- | --- | --- |
| ① 허깅페이스 데모 https://huggingface.co/spaces/fashn-ai/fashn-vton-1.5 | 브라우저만 | 몇 장 시험해 볼 때. 설치 없음 |
| ② 내 PC/서버에 설치 (아래 1~4단계) | NVIDIA GPU + CUDA 권장, 디스크 약 2.3GB | 여러 장 반복 작업, 자동화 |
| ③ FASHN 유료 API https://docs.fashn.ai | API 키 | 서비스에 붙이거나 GPU가 없을 때 |

- GPU 없이 CPU로도 돌아가지만 매우 느리다(float32로 변환됨). 이 클라우드 세션 컨테이너에는 GPU가 없으니, 여기서는 코드 작성·점검까지만 하고 실행은 사용자 PC·GPU 서버·①/③으로 안내한다.
- RTX 30xx/40xx, A100, H100 같은 Ampere 이상 GPU면 bf16으로 빠르게 돈다. 그보다 오래된 GPU는 float32.

## 1. 설치 (Python 3.10~3.12)

```bash
git clone https://github.com/fashn-AI/fashn-vton-1.5.git
cd fashn-vton-1.5
python -m venv .venv && source .venv/bin/activate     # 윈도우: .venv\Scripts\activate
pip install -e .
```

GPU가 없으면(CPU 전용) 이것도 실행:

```bash
pip uninstall -y onnxruntime-gpu && pip install onnxruntime
```

## 2. 가중치 받기 (약 2GB)

```bash
python scripts/download_weights.py --weights-dir ./weights
```

결과 구조:

```
weights/
├── model.safetensors          # 피팅 본체 (HF: fashn-ai/fashn-vton-1.5)
└── dwpose/
    ├── yolox_l.onnx           # 사람 찾기
    └── dw-ll_ucoco_384.onnx   # 포즈(관절) 추정
```

사람 영역 분석기(fashn-human-parser, 약 244MB)는 첫 실행 때 허깅페이스 캐시에 자동으로 받아진다. 저장 위치를 바꾸려면 `HF_HOME` 환경변수를 지정한다.
가중치가 없으면 파이프라인이 "Missing model weights" 오류와 함께 위 명령을 알려준다.

## 3. 실행

### 명령어 한 줄 (CLI)

```bash
python examples/basic_inference.py \
  --weights-dir ./weights \
  --person-image 사람사진.jpg \
  --garment-image 옷사진.jpg \
  --category tops \
  --garment-photo-type flat-lay \
  --num-samples 2 \
  --output-dir outputs
```

결과는 `outputs/output_00.png`, `output_01.png` …로 저장된다.

### 파이썬 코드

```python
from fashn_vton import TryOnPipeline
from PIL import Image

pipeline = TryOnPipeline(weights_dir="./weights")   # GPU 자동 사용, device="cpu"로 강제 가능

person  = Image.open("person.jpg").convert("RGB")
garment = Image.open("garment.jpg").convert("RGB")

result = pipeline(
    person_image=person,
    garment_image=garment,
    category="tops",              # "tops" | "bottoms" | "one-pieces"
    garment_photo_type="model",   # "model"(사람이 입은 사진) | "flat-lay"(누끼·바닥컷)
    num_samples=1,                # 1~4장
    num_timesteps=30,             # 20 빠름 / 30 보통 / 50 고품질
    guidance_scale=1.5,
    seed=42,                      # 같은 시드 = 같은 결과
    segmentation_free=True,       # 기본값. 체형 보존 + 옷 부피 자유
)
for i, img in enumerate(result.images):
    img.save(f"out_{i:02d}.png")
```

여러 벌을 돌릴 땐 `TryOnPipeline`을 **한 번만** 만들고 반복문에서 `pipeline(...)`만 호출한다(모델 로딩이 가장 느림).

## 4. 옵션 고르는 법

| 옵션 | 값 | 고르는 기준 |
| --- | --- | --- |
| `category` | `tops` | 상의: 티셔츠, 블라우스, 재킷 |
|  | `bottoms` | 하의: 바지, 치마, 반바지 |
|  | `one-pieces` | 전신: 원피스, 점프수트 |
| `garment_photo_type` | `model` | 옷 사진이 **사람이 입고 있는** 사진일 때 (기본값). 옷 사진에서 포즈를 읽고 옷 부분만 떼어 쓴다 |
|  | `flat-lay` | 옷만 찍은 상품컷·누끼·바닥 촬영일 때. 옷 사진 전체를 그대로 쓴다 |
| `num_timesteps` | 20 / 30 / 50 | 시안은 20, 최종은 50 |
| `seed` | 정수 | 마음에 드는 결과가 나오면 시드를 기록해 재현 |
| `segmentation_free` | True(기본) / False | 기본 그대로. 원래 옷 모양을 벗어나는 넉넉한 옷(오버핏, 롱코트)에 유리. 결과가 원래 옷 윤곽에 갇혀야 할 때만 False(CLI: `--no-segmentation-free`) |
| `guidance_scale` | 1.5 | 보통 건드리지 않는다. 높이면 옷 디테일이 강해지지만 색이 과해질 수 있다 |

상·하의를 둘 다 바꾸려면 **두 번** 돌린다: 상의로 1차 결과 → 그 결과를 사람 사진으로 넣고 하의로 2차.

## 5. 좋은 결과를 위한 사진 준비

- 사람 사진: 전신 또는 무릎 위까지, 정면·약간 측면, 팔이 몸통을 가리지 않게. 얼굴·손이 잘리지 않게.
- 옷 사진: 옷 전체가 보이게, 주름·접힘 적게, 단색 배경. 로고·프린트는 정면에서 선명하게.
- 입력은 내부에서 비율을 유지한 채 모델 입력 크기로 줄이고 패딩한다. 극단적인 가로/세로 비율은 피한다.
- 결과에서 로고 글자·작은 프린트는 뭉개질 수 있다 → 최종 상세페이지용이면 원본 상품컷과 함께 쓴다.

## 6. 문제 해결

| 증상 | 해결 |
| --- | --- |
| `Missing model weights` | 2단계 다운로드 명령 실행, `--weights-dir` 경로 확인 |
| onnxruntime CUDA 관련 오류 | CUDA 설정 확인, 아니면 1단계의 CPU용 onnxruntime으로 교체 |
| CUDA out of memory | `num_samples=1`, 다른 GPU 프로그램 종료 |
| 너무 느림 | CPU로 돌고 있는지 로그의 `Using device:` 확인. `num_timesteps=20` |
| 옷이 엉뚱한 부위에 | `category` 확인, 사람 사진에서 해당 부위가 가려지지 않았는지 확인 |
| 누끼컷인데 결과가 이상 | `garment_photo_type="flat-lay"` 로 바꿨는지 확인 |
| 마스크가 어떻게 잡히는지 보고 싶음 | 저장소의 `scripts/debug_masks.py` 사용 |

## 7. 라이선스·주의

- 코드와 피팅 모델: **Apache-2.0** — 상업적 사용 가능(고지 유지).
- DWPose, YOLOX: Apache-2.0.
- **fashn-human-parser**(자동 다운로드되는 사람 분석기): NVIDIA SegFormer Source Code License를 따른다. 이 라이선스는 상업적 사용을 제한할 수 있으니, 판매용 서비스·유료 상세페이지 제작에 쓰기 전에 https://github.com/NVlabs/SegFormer/blob/master/LICENSE 를 직접 확인하라고 안내한다. 확실하지 않으면 "상업용이면 FASHN 유료 API가 안전하다"고 말한다.
- 실존 인물 사진은 본인 동의를 받은 것만 쓴다. 남의 사진에 옷을 입혀 오해를 부르는 용도는 돕지 않는다.

## 8. 다른 스킬과 연결

- **idm-vton**: 같은 가상 피팅이지만 비상업(CC BY-NC-SA) 연구용, 로고·프린트 디테일에 강함. 상업용이면 이 스킬(fashn-vton), 개인 시안·연구·디테일 비교면 idm-vton. 두 모델 비교표는 idm-vton 스킬 9절.
- **outfit-swap**: 2D·반실사 캐릭터의 의상 교체는 그쪽(생성형 편집). 실사 사람 + 실제 상품 사진이면 이 스킬.
- **the-given-brand**: 더기븐 티셔츠 누끼컷을 AI 모델 사진에 입혀 룩북·피드 시안을 만들 때 → `category="tops"`, `garment_photo_type="flat-lay"`, 브랜드 모델 규칙은 the-given-brand를 따른다.
- 결과 검수는 outfit-swap의 <프롬프트 3> 방식(원본과 결과를 항목별로 비교)을 그대로 쓴다.
