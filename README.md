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

### Validator v0 Scope (tag-based)
- EvidenceTag(v0)를 입력으로 받아 `ValidationStatus(pass|warn|fail)`을 산출한다.
- 본 단계는 **판단/추론이 아니라 관찰된 상태(tag)의 등급화**만 수행한다.
- 정책(v0):
  - `STRUCT_INVALID` → `fail` (FAIL은 구조가 깨졌을 때만 사용)
  - `ANCHOR_NOT_FOUND` → `warn` (message code: `W_ANCHOR_NOT_FOUND`)
  - `ANCHOR_AMBIGUOUS` → `warn` (message code: `W_ANCHOR_AMBIGUOUS`, 등급은 동일)
  - `CONFIDENCE_WITHOUT_ANCHOR` → `warn`
  - 그 외(구조 유효 + 경고 없음) → `pass`

## Non-goals
- API server
- Authentication / billing
- Database access
- Production-grade OCR / STT client integrations