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

### Requirement State v0 Scope
- `EvidenceTag[]`(+ tag-validator 결과)를 기반으로 “요건 평가 가능 상태”만 분류한다.
- 출력: `RequirementState(EVALUATABLE|UNSTABLE|INVALID)`
- 정책(v0):
  - `INVALID`  ↔ `ValidationStatus.fail`
  - `UNSTABLE` ↔ `ValidationStatus.warn`
  - `EVALUATABLE` ↔ `ValidationStatus.pass`

## [TRIAL] Signals v0
법적 판단/결론을 만들지 않고, UI가 요구하는 "신호 수준(level)"만 근거 재현 가능하게 생성하는 **파생 출력(derived output)** 이다.

- 입력(모드1): 원문 텍스트
- 입력(모드2): v1.3 구조화 결과 + EvidenceTag[]
- 출력 공통: `mode`, `version`, `summary`, `signals[]`
- `signals[]`: `name`, `level`, `reason_codes[]`, `evidence[]`
  - `evidence[]`는 가능하면 `evidence_span` + `evidence_anchor(start_char/end_char)`를 포함
  - `evidence[]`가 비어 있을 수 있으며(근거 매칭 실패/근거 풀 없음 등), 이 경우 `reason_codes[]`로 “근거 부족”을 명시
  - `reason_codes[]` 네이밍(최소 규칙): `T_`(text), `E_`(위험/에러), `W_`(경고), `P_`(통과) 접두어 + 대문자/숫자/`_` (`^[TEWP]_[A-Z0-9_]+$`)

### `signals.name` ↔ UI 항목 매핑
| signals.name | UI 항목(예시 라벨) | mode |
|---|---|---|
| `repetition` | 반복 | text |
| `threat` | 위협 | text |
| `refusal` | 거절/거부 | text |
| `evidence_strength` | 증거 강도 | evidence |
| `clarity` | 명확성(근거 재현 가능성) | evidence |
| `safety` | 안전(파이프라인 상태) | evidence |

## Non-goals
- API server
- Authentication / billing
- Database access
- Production-grade OCR / STT client integrations