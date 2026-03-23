# AnsimOn-AI

AnsimOn AI core repository.

이 레포는 사용자가 업로드한 증거 데이터를 AI 입력으로 정규화하고, 분석 결과를 생성한 뒤, 타임라인 정리와 고소장 및 진술서 작성에 활용하는 핵심 로직을 담고 있습니다.

## 설치

### Python 의존성

프로젝트 의존성은 레포 루트의 `pyproject.toml` 기준으로 관리합니다.

```bash
python -m pip install -e .
```

### 시스템 의존성

아래 패키지는 OCR, PDF, STT 관련 기능 실행 시 필요합니다.

- `ffmpeg`
- `poppler-utils`
- `tesseract-ocr`
- `tesseract-ocr-kor`

Ubuntu 예시:

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg poppler-utils tesseract-ocr tesseract-ocr-kor
```

## 현재 범위

- Evidence text structuring
- Anchor 적용 및 validation
- Timeline prototype 생성
- Backend -> AI handoff용 계약 스키마 관리

## Pipeline Overview

현재 파이프라인은 아래 흐름을 기준으로 동작합니다.

1. 입력 증거를 타입별로 정규화합니다.
   텍스트, STT, OCR, 문서 추출, 폼 입력 등을 `StructuringInput` 형태로 변환합니다.
2. 구조화 파이프라인을 실행합니다.
   LLM 호출 후 JSON을 생성하고, anchor를 적용한 뒤 validator로 기본 정합성을 검증합니다.
3. 증거별 처리 결과를 타임라인 프로토타입 출력으로 조합합니다.
   각 증거의 텍스트, timestamp, title, description, tags를 기반으로 날짜/시간별 timeline item을 만듭니다.

현재 구조화 파이프라인의 내부 버전은 `schema v1.5`, `prompt v1.2` 기준입니다.