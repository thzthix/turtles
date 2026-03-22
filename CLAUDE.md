# CLAUDE.md — Turtle Analyzer Agent

## 프로젝트 개요

거북이 이미지를 업로드하면 종류(5종)와 암수를 판별하는 AI 에이전트.
Pydantic AI + Claude 멀티모달 + FastAPI 기반.

## 기술 스택

- Python 3.13
- Pydantic AI (latest) + Pydantic v2
- Anthropic Claude API (멀티모달 이미지 분석)
- FastAPI + Uvicorn
- Ruff (formatter + linter)
- pytest + pytest-asyncio (테스트)

## 판별 대상

- 종류: 붉은귀거북, 페닌슐라쿠터, 보석거북, 옐로우밸리, 핑크밸리
- 암수 판별

## 디렉토리 구조

```
turtle_agent/
  __init__.py
  models.py        # Pydantic 응답/요청 모델만
  agent.py         # Pydantic AI 에이전트 정의만
  tools.py         # 에이전트 tool 정의만
  server.py        # FastAPI 라우팅만
  exceptions.py    # 커스텀 예외만
  data/
    species.json   # 거북이 도감 데이터
tests/
  conftest.py
  test_agent.py
  test_server.py
  test_tools.py
```

각 파일은 단일 책임. 경계를 넘지 않는다.

## 환경변수

| 변수명 | 필수 | 설명 |
|--------|------|------|
| `ANTHROPIC_API_KEY` | Y | Claude API 인증키 |
| `TURTLE_DB_PATH` | N | SQLite DB 경로 (기본값: `./turtle_analysis.db`) |
| `TURTLE_HOST` | N | 서버 호스트 (기본값: `0.0.0.0`) |
| `TURTLE_PORT` | N | 서버 포트 (기본값: `8000`) |

`.env` 파일은 `.gitignore`에 포함. 절대 커밋하지 않는다.

## 실행 방법

```bash
uv run uvicorn turtle_agent.server:app --host 0.0.0.0 --port 8000 --reload
```

## 에이전트 Tool

에이전트가 판별 과정에서 자율적으로 호출할 수 있는 tool 목록.
모든 tool은 `tools.py`에 정의한다.

### 1. 거북이 도감 조회 (`lookup_species`)

- 입력: 종 이름 (`str`)
- 출력: 해당 종의 상세 정보 (서식지, 수명, 외형 특징, 주의사항 등)
- 데이터 소스: `data/species.json`
- 용도: 판별 결과에 종 상세 정보를 보강

### 2. 판별 이력 저장 (`save_analysis`)

- 입력: 분석 결과 (`TurtleAnalysisResult`)
- 출력: 저장 성공 여부 + 저장 ID
- 저장소: SQLite (향후 PostgreSQL 전환 가능)
- 용도: 분석 이력 축적, 통계 조회 기능의 기반

### 향후 확장 예정

- 이미지 전처리 tool (크롭/리사이즈)
- 신뢰도 기반 재분석 tool

## 코드 컨벤션

### Python / 타입

- Python 3.13 문법 사용: `str | None` (`Optional` 사용 금지), `from __future__ import annotations` 불필요
- 모든 함수에 타입 힌트 필수
- `Any` 타입 사용 최소화

### Pydantic v2 문법

- `model_config = ConfigDict(...)` 사용 (`class Config:` 금지)
- `.model_dump()` 사용 (`.dict()` 금지)
- `@field_validator` 사용 (`@validator` 금지)
- 필드 문서화는 `Field(description=...)` 사용

### 네이밍

- PEP 8 준수
- Pydantic 모델: 용도별 접미사 — `*Result`, `*Request`, `*Error`
- 예: `TurtleAnalysisResult`, `TurtleAnalysisRequest`

### 독스트링

- 인라인 주석(`#`) 사용 금지 — 코드가 스스로 설명하도록 네이밍으로 해결
- 독스트링은 FastAPI 엔드포인트와 public 함수에만 작성 (Swagger 문서 자동 생성용)
- Pydantic 필드는 `Field(description=...)` 으로 문서화

### 함수

- 한 함수 30줄 이내 — 넘어가면 분리
- 파라미터 3개 이하 — 초과 시 Pydantic 모델로 묶기
- 리턴 타입 항상 명시 (`-> None` 포함)
- I/O 있는 함수(API 호출, DB, 파일) → `async def` / 순수 계산 → `def`

### 에러 핸들링

- 커스텀 예외는 `exceptions.py`에 정의
- FastAPI 레이어에서 커스텀 예외 → `HTTPException` 변환
- 에이전트/모델 레이어에서는 `HTTPException` 직접 사용 금지

### 포매터/린터

- Ruff 사용 (formatter + linter 겸용)
- 설정은 `pyproject.toml`에 명시

## Ruff 설정 (pyproject.toml)

```toml
[tool.ruff]
target-version = "py313"
line-length = 120

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "T20",  # flake8-print
    "RUF",  # ruff-specific
]
```

## API 응답 형식

모든 API 응답은 동일한 래퍼 구조를 사용한다:

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

실패 시:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_IMAGE",
    "message": "지원하지 않는 이미지 형식입니다"
  }
}
```

## 테스트 컨벤션

- `pytest` + `pytest-asyncio` 사용
- 테스트 파일은 `tests/` 디렉토리에 `test_*.py` 형식
- LLM 호출 모킹: `agent.override(model=TestModel(...))` 사용
- 실제 API 호출 테스트는 별도 마커: `@pytest.mark.integration`
- 테스트 함수명: `test_<대상>_<시나리오>` (예: `test_analyze_valid_image`)

## 커밋 / PR

- Conventional Commits 형식: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- 커밋 메시지, PR 제목, PR 설명 모두 한글 필수
- 커밋 단위: 기능 하나 (메서드 단위 X)
- 예: `feat: 거북이 종류 판별 엔드포인트 추가`

## 작업 흐름

한 기능을 구현할 때 반드시 아래 순서를 따른다. 한 번에 여러 기능을 동시 구현하지 않는다.

1. 인풋/아웃풋 스펙 정의 (Pydantic 모델)
2. 함수 시그니처 작성
3. 테스트 코드 먼저 작성
4. 구현
5. 테스트 통과 확인
6. 커밋
7. 다음 기능으로
