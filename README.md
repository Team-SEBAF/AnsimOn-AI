# AnsimOn-AI

AnsimOn AI core repository.

## Scope
- Evidence text structuring
- Validator (policy-level rules)
- Evaluation / regression tests

### Validator v0.1-α Scope
- v1.3 스키마의 **구조적 정합성**만 검증한다.
- 최상위 필수 키 존재 여부를 검증한다.
- 각 필드의 공통 필드(`value`, `confidence`, `evidence_span`, `evidence_anchor`) 존재 여부를 검증한다.
- `confidence` 값의 형식(`high | medium | low`)을 검증한다.
- `evidence_span` ↔ `evidence_anchor`의 **null 정합성**을 검증한다.
- 본 단계에서는 **의미 해석, 법적 판단, 좌표 정확성 검증은 수행하지 않는다.**

## Non-goals
- API server
- Authentication / billing
- Database access
- Production-grade OCR / STT client integrations