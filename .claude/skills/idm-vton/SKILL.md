---
name: idm-vton
description: 카이스트 연구팀의 가상 피팅 모델 IDM-VTON(yisol/IDM-VTON, ECCV 2024)으로 "사람 사진 + 옷 사진 + 옷 설명 문장 → 그 옷을 입은 사진"을 만든다. SDXL 기반이라 옷의 로고·프린트·질감 보존이 강점이지만 비상업(CC BY-NC-SA 4.0) 전용. 허깅페이스 데모 사용법, 로컬 그라디오 데모 설치, 마스크 직접 칠하기, 데이터셋 추론·학습, 라이선스 주의까지 안내한다. "IDM-VTON", "idm vton", "로고 살려서 옷 입혀줘", "프린트 티 피팅", "가상 피팅 연구용", "옷 입혀보기 고품질" 같은 요청에 사용. 판매·상업용 피팅이면 fashn-vton 스킬을 쓴다.
---

# IDM-VTON — 디테일 살린 가상 피팅 (비상업·연구용)

출처: https://github.com/yisol/IDM-VTON · 논문 https://arxiv.org/abs/2403.05139 (ECCV 2024)
한 줄 요약: **사람 사진 + 옷 사진 + 옷 설명 한 줄 → 그 옷을 입은 사진.** SDXL(대형 이미지 생성 모델)에 옷 전용 인코더(GarmentNet)와 IP-Adapter를 붙여 로고·글자·패턴 같은 세부를 잘 지킨다.

> ⚠️ **먼저 말할 것: 상업적 사용 금지.** 코드와 가중치 모두 CC BY-NC-SA 4.0. 판매 상세페이지, 광고, 유료 서비스에는 쓸 수 없다. 개인 시안·연구·포트폴리오 연습용. 상업용이면 **fashn-vton** 스킬(Apache-2.0)로 안내한다.

사용자는 비개발자일 수 있으니 한국어로, 한 단계씩, 명령어는 복사해서 쓸 수 있게 준다.

## 0. 어디서 돌릴까

| 방법 | 필요한 것 | 언제 |
| --- | --- | --- |
| ① 허깅페이스 데모 https://huggingface.co/spaces/yisol/IDM-VTON | 브라우저만 | 대부분의 경우 이걸로 충분. 무료 GPU라 대기열이 있을 수 있음 |
| ② 로컬 그라디오 데모 (아래 2~4단계) | NVIDIA GPU(CUDA 11.8), conda, 넉넉한 VRAM·디스크 | 반복 작업, 내 PC에서 비공개로 |
| ③ 데이터셋 추론·학습 (5단계) | VITON-HD / DressCode 데이터셋, 고성능 GPU | 연구·논문 재현·직접 학습 |

- SDXL 기반 fp16 모델이라 **GPU 필수**. CPU로는 사실상 못 돌린다. VRAM은 공식 문서에 수치가 없다. SDXL 계열이므로 16GB 이상을 권장 수준으로 안내하되 "추정"이라고 말한다.
- 이 클라우드 세션에는 GPU가 없다. 여기서는 설정·코드 점검까지만 하고 실행은 ①이나 사용자 GPU 환경으로 안내한다.

## 1. 허깅페이스 데모 쓰는 법 (가장 쉬움)

1. **Human**: 사람 사진 업로드.
2. **Use auto-generated mask** 체크(기본 ON) → 자동으로 **상의 영역**을 마스크로 잡는다.
   - 자동 마스크는 코드상 **상의(upper_body) 전용**이다. 하의·원피스를 바꾸려면 체크를 끄고 **펜으로 바꿀 옷 부분을 직접 칠한다.**
3. **Use auto-crop & resizing**: 사람이 사진에서 작게 나왔거나 비율이 3:4가 아니면 체크.
4. **Garment**: 옷 사진 업로드(누끼·상품컷 권장).
5. **설명란**에 옷을 영어로 짧게: `Short Sleeve Round Neck T-shirts`, `Black oversized hoodie with white logo print`
   - 내부적으로 "model is wearing ○○" 문장이 된다. 색·핏·소매·넥라인을 넣으면 정확도가 오른다.
6. Advanced Settings: Denoising Steps 20~40(기본 30), Seed(기본 42).
7. **Try-on** → 오른쪽에 결과, 가운데에 실제 사용된 마스크가 보인다. 결과가 이상하면 먼저 마스크를 확인한다.

## 2. 로컬 설치 (conda)

```bash
git clone https://github.com/yisol/IDM-VTON.git
cd IDM-VTON
conda env create -f environment.yaml      # Python 3.10, PyTorch 2.0.1 + CUDA 11.8, diffusers 0.25
conda activate idm
```

본체 가중치(`yisol/IDM-VTON`, SDXL 기반 UNet·GarmentNet·VAE·텍스트/이미지 인코더)는 첫 실행 때 허깅페이스에서 자동으로 받는다. 용량이 크니 디스크 여유를 확인한다(`HF_HOME`으로 위치 변경 가능).

## 3. 전처리 체크포인트 넣기

https://huggingface.co/spaces/yisol/IDM-VTON/tree/main/ckpt 에서 받아 아래 구조로 둔다.

```
ckpt/
├── densepose/model_final_162be9.pkl        # 몸 표면 좌표(DensePose)
├── humanparsing/parsing_atr.onnx           # 사람 부위 분할
├── humanparsing/parsing_lip.onnx
└── openpose/ckpts/body_pose_model.pth      # 관절(포즈)
```

## 4. 로컬 데모 실행

```bash
python gradio_demo/app.py
```

브라우저에 뜨는 주소로 들어가 1단계와 똑같이 쓴다. 입력은 내부에서 **768×1024(3:4 세로)**로 맞춰진다. 처음부터 3:4 세로 사진을 쓰면 왜곡이 적다.

## 5. 데이터셋 추론·학습 (연구용)

데이터 구조는 저장소 README를 따른다(VITON-HD: `image / image-densepose / agnostic-mask / cloth / *_tagged.json`, DressCode: `upper_body / lower_body / dresses` 폴더에 `image-densepose`, `dc_caption.txt`).

```bash
# VITON-HD (상의)
accelerate launch inference.py --pretrained_model_name_or_path "yisol/IDM-VTON" \
  --width 768 --height 1024 --num_inference_steps 30 --output_dir result \
  --unpaired --data_dir DATA_DIR --seed 42 --test_batch_size 2 --guidance_scale 2.0

# DressCode (category: upper_body | lower_body | dresses)
accelerate launch inference_dc.py --pretrained_model_name_or_path "yisol/IDM-VTON" \
  --width 768 --height 1024 --num_inference_steps 30 --output_dir result \
  --unpaired --data_dir DATA_DIR --seed 42 --test_batch_size 2 --guidance_scale 2.0 \
  --category upper_body
```

- `--unpaired`: 다른 사람의 옷을 입히는 실제 피팅 상황. 빼면 원래 입던 옷으로 복원(평가용).
- 학습: IP-Adapter(`h94/IP-Adapter`의 `ip-adapter-plus_sdxl_vit-h.bin` → `ckpt/ip_adapter`, image encoder → `ckpt/image_encoder`)를 받은 뒤 `sh train_xl.sh` 또는
  `accelerate launch train_xl.py --gradient_checkpointing --use_8bit_adam --output_dir=result --train_batch_size=6 --data_dir=DATA_DIR`

## 6. 좋은 결과를 위한 요령

- 사람 사진: 3:4 세로, 상반신~전신, 정면, 팔이 몸통을 가리지 않게.
- 옷 사진: 단색 배경 누끼, 정면, 주름 적게. 로고·프린트가 선명할수록 그대로 옮겨진다(이 모델의 강점).
- 설명 문장은 영어로, 옷 종류 + 색 + 소매/넥라인 + 핏. 예: `White short sleeve crew neck t-shirt with red chest logo`
- 결과가 옷 경계에서 번지면 마스크를 조금 넓게 다시 칠한다. 손·머리카락이 마스크에 들어가면 그 부분도 다시 그려지니 피한다.

## 7. 문제 해결

| 증상 | 해결 |
| --- | --- |
| 하의/원피스인데 상의만 바뀜 | 자동 마스크 끄고 펜으로 직접 칠하기(자동 마스크는 상의 전용) |
| `ckpt/...` 파일 없음 오류 | 3단계 체크포인트 위치 확인 |
| CUDA out of memory | 다른 GPU 프로그램 종료, 더 큰 VRAM GPU, 아니면 허깅페이스 데모 |
| conda 설치 충돌 | CUDA 11.8 / PyTorch 2.0.1 고정이라 최신 드라이버·환경과 충돌할 수 있음 → 새 conda 환경, 또는 데모 사용 |
| 얼굴·배경이 바뀜 | 마스크가 너무 넓다. 옷 부분만 다시 칠하기 |
| 사람이 작게 찌그러짐 | auto-crop 체크, 또는 3:4로 미리 잘라서 업로드 |

## 8. 라이선스·윤리

- 코드·체크포인트: **CC BY-NC-SA 4.0** — 비상업, 출처 표시, 변형물도 같은 라이선스.
- 판매용 상품컷, 브랜드 광고, 유료 서비스, 고객 납품물에 쓰면 안 된다고 분명히 말한다. 대안: **fashn-vton**(Apache-2.0) 또는 유료 API.
- 실존 인물 사진은 본인 동의를 받은 것만 쓴다.

## 9. fashn-vton과 비교 (어느 쪽을 쓸까)

| | **fashn-vton** (FASHN VTON v1.5) | **idm-vton** (IDM-VTON) |
| --- | --- | --- |
| 역할 | 실무·상업용 빠른 피팅 | 연구·개인 시안용 고디테일 피팅 |
| 라이선스 | Apache-2.0 (상업 가능, 단 사람 분석기 라이선스 확인 필요) | CC BY-NC-SA 4.0 (**비상업만**) |
| 입력 | 사람 + 옷 + 카테고리 | 사람 + 옷 + **영어 옷 설명** (+ 필요시 직접 그린 마스크) |
| 마스크 | 필요 없음(maskless) | 자동(상의만) 또는 직접 칠하기 |
| 옷 종류 | tops / bottoms / one-pieces 모두 자동 | 데모 자동은 상의만, 나머지는 수동 마스크 |
| 설치 난도 | 쉬움(pip, 약 2GB) | 어려움(conda, CUDA 11.8 고정, SDXL 대용량) |
| GPU | 권장(CPU도 느리게 가능) | 필수 |
| 강점 | 체형 보존, 오버핏 등 옷 부피 자유, 가벼움 | 로고·글자·패턴 등 세부 보존 |

결정 규칙: **돈이 오가는 결과물이면 fashn-vton.** 개인 연습·연구·디테일 비교 실험이면 idm-vton도 시도. 같은 사진으로 둘 다 돌려 비교하고 싶다는 요청이면 두 스킬 순서대로 안내하고, 결과 비교는 outfit-swap의 <프롬프트 3> 방식으로 한다.
