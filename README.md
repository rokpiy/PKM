# PKM (Personal Knowledge Management) System

Obsidian → Atomic Notes → Graph DB → Agentic Reasoning 시스템 구현

## 📋 현재 구현 상태

### ✅ Stage 1: Atomic Note Agent (완료)
- Obsidian Vault 로더
- Google Gemini 기반 Atomic Note 분해 Agent
- JSON 및 마크다운 출력

### ✅ Stage 2: Entity & Relationship Extraction (완료)
- Gemini 결과 기반 Entity 개선
- Regex 패턴 매칭으로 추가 관계 추출
- 한글/영문 관계 패턴 지원
- spaCy 불필요 (경량화)

### ✅ Stage 3: Neo4j Graph DB 구축 (완료)
- Atomic Notes → Knowledge Graph 변환
- Entity와 Relationship을 Graph로 저장
- Neo4j Cypher 쿼리 지원
- Graph 시각화 및 탐색

### ✅ Stage 4: Knowledge Graph Reasoning (완료)
- Graph 기반 추론 엔진
- 질문에서 엔티티 추출 및 Graph 탐색
- 연관된 노트와 경로 자동 검색
- LLM을 위한 Context Engineering

### 🔜 다음 단계
- Stage 5: Agentic Reasoning (LLM 통합)
- Stage 6: Self-Evolving System

## 🚀 설치

### 1. 가상환경 생성 및 활성화

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. API 키 설정

프로젝트 루트에 `.env` 파일을 생성하고 API 키를 추가하세요:

```bash
# .env.example을 복사하여 시작
cp .env.example .env

# API 키 입력
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

또는 직접 `.env` 파일을 편집:

```bash
# .env 파일
GEMINI_API_KEY=your-api-key-here
```

API 키는 [Google AI Studio](https://makersuite.google.com/app/apikey)에서 무료로 발급받을 수 있습니다.

**⚠️ 중요:** 
- `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다
- API 키는 절대 공개 레포지토리에 올리지 마세요

## 📖 사용 방법

### 🚀 Quick Start (권장)

가장 쉬운 방법:

```bash
./quick_start.sh
```

대화형 메뉴에서:
- `1`: Stage 1만 실행 (Atomic Notes 생성)
- `2`: Stage 2만 실행 (Entity 추출)
- `3`: Stage 3만 실행 (Graph DB Import)
- `4`: Stage 4만 실행 (Knowledge Graph Reasoning)
- `5`: 전체 파이프라인 (Stage 1 + 2 + 3)

### Stage 1: Atomic Notes 생성

#### 직접 실행:

```bash
python test_atomic_agent.py
```

**선택 옵션:**
1. **단일 노트 테스트** - 자동으로 적당한 노트 선택
2. **특정 노트 선택** - 목록에서 원하는 노트 선택
   - 단일: `3`
   - 여러개: `1,3,5`
   - 범위: `1-5`
   - 혼합: `1,3-5,7`
3. **전체 Vault** - 모든 노트 처리

### Stage 2: Entity & Relationship 추출

Stage 1 완료 후:

```bash
python test_entity_extraction.py
```

자동으로:
- Atomic Notes에서 엔티티 개선
- 추가 관계 추출
- `*_enhanced.json` 파일로 저장

### Stage 3: Neo4j Graph DB Import

#### 1. Neo4j 설치 및 실행

Docker를 사용하는 것이 가장 간단합니다:

```bash
# Neo4j 컨테이너 실행
docker run -d \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  --name neo4j-pkm \
  neo4j:latest
```

**포트:**
- `7474`: Neo4j Browser (웹 UI)
- `7687`: Bolt 프로토콜 (Python 연결)

**기본 인증:**
- Username: `neo4j`
- Password: `password` (`.env`에서 변경 가능)

#### 2. .env 파일에 Neo4j 설정 추가

```bash
# Neo4j Graph Database (Stage 3)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

#### 3. Graph DB Import 실행

Stage 1과 2 완료 후:

```bash
python tests/test_graph_import.py
```

**선택 옵션:**
1. **기존 데이터 유지하고 추가** - 새로운 데이터만 추가
2. **모든 데이터 삭제 후 새로 시작** - 완전히 새로 Import

#### 4. Neo4j Browser에서 확인

브라우저에서 `http://localhost:7474` 접속:

**유용한 Cypher 쿼리:**

```cypher
// 모든 Atomic Notes 보기
MATCH (n:AtomicNote) RETURN n LIMIT 25

// 특정 Entity 주변 그래프 보기
MATCH (e:Entity {name: "AI"})-[r]-(related)
RETURN e, r, related

// Entity 통계
MATCH (e:Entity) RETURN e.domain as domain, count(*) as count

// 가장 많이 연결된 Entity Top 10
MATCH (e:Entity)-[r]-()
RETURN e.name, count(r) as connections
ORDER BY connections DESC
LIMIT 10
```

### Stage 4: Knowledge Graph Reasoning

Stage 3 완료 후, Graph를 탐색하고 질문에 답변할 수 있습니다:

```bash
python tests/test_kg_reasoning.py
```

**대화형 옵션:**
1. **대화형 질문** - 자유롭게 질문 입력
2. **샘플 질문 테스트** - 미리 준비된 질문으로 테스트
3. **엔티티 정보 조회** - 특정 엔티티의 상세 정보
4. **엔티티 간 경로 탐색** - 두 개념이 어떻게 연결되어 있는지 확인

**예시 질문:**
- "AI와 머신러닝의 관계는?"
- "스타트업에서 네트워킹이 중요한 이유는?"
- "PKM 시스템은 어떻게 작동하나?"

**Python 코드로 직접 사용:**

```python
from kg_reasoning import KGReasoner, create_graph_context_for_llm

# Reasoner 초기화
reasoner = KGReasoner("bolt://localhost:7687", ("neo4j", "password"))

# 질문 분석 및 Graph 탐색
result = reasoner.reasoning_chain("AI란 무엇인가?", depth=2)

print(f"발견된 엔티티: {result['entities']}")
print(f"관련 노트: {len(result['related_notes'])}개")

# LLM을 위한 Context 생성
context = create_graph_context_for_llm(result, max_tokens=1000)
print(context)

reasoner.close()
```

### 옵션 2: Python 코드로 직접 사용 (Stage 1)

```python
import sys
from pathlib import Path

# src 폴더를 경로에 추가
sys.path.insert(0, str(Path('src')))

from atomic_note_agent import AtomicNoteAgent
from obsidian_loader import ObsidianVaultLoader

# Agent 초기화
agent = AtomicNoteAgent()

# 단일 노트 분해
loader = ObsidianVaultLoader("~/Documents/Obsidian Vault")
notes = loader.load_vault()

result = agent.decompose_note(notes[0])
print(f"생성된 Atomic Notes: {len(result['atomic_notes'])}개")

# 전체 Vault 분해
results = agent.decompose_vault("~/Documents/Obsidian Vault")
```

### 옵션 3: 개별 스크립트 실행

```bash
# Stage 1만 실행
python tests/test_atomic_agent.py

# Stage 2만 실행 (Stage 1 완료 후)
python tests/test_entity_extraction.py
```

## 📂 출력 구조

```
PKM/
├── atomic_notes/           # JSON 형식 출력
│   └── note_name_atomic.json
├── atomic_notes_md/        # 마크다운 형식 출력
│   └── note_YYYYMMDD_001_title.md
└── ...
```

### JSON 출력 예시

```json
{
  "atomic_notes": [
    {
      "id": "note_20251216_001",
      "title": "핵심 개념",
      "content": "1-2문장 설명",
      "detailed_content": "상세 내용",
      "extracted_entities": ["Entity1", "Entity2"],
      "relationships": [
        {
          "from": "Entity1",
          "type": "relates_to",
          "to": "Entity2"
        }
      ],
      "domain": "ai",
      "confidence": "high"
    }
  ],
  "hierarchy": {
    "parent_concept": ["child1", "child2"]
  },
  "summary": "전체 문서 요약"
}
```

### 마크다운 출력 예시

```markdown
---
type: atomic_note
source: Original Note
id: note_20251216_001
domain: ai
confidence: high
entities: ["Entity1", "Entity2"]
---

# 핵심 개념

## 핵심 개념
1-2문장 설명

## 상세 내용
상세 내용...

## 추출된 엔티티
`Entity1`, `Entity2`

## 관계
- `Entity1` --[relates_to]--> `Entity2`
```

## 🎯 Atomic Note 원칙

1. **단일 책임**: 하나의 개념/아이디어만 포함
2. **독립성**: 독립적으로 이해 가능
3. **연결성**: 다른 노트와 링크 가능
4. **구조화**: 명확한 메타데이터 포함

## 🔧 프로젝트 구조

```
PKM/
├── src/                        # 핵심 소스 코드
│   ├── obsidian_loader.py          # Obsidian Vault 로더
│   ├── atomic_note_agent.py        # Atomic Note 분해 Agent
│   └── entity_extraction_simple.py # Entity & Relationship 추출
├── tests/                      # 테스트 스크립트
│   ├── test_atomic_agent.py        # Stage 1 테스트
│   └── test_entity_extraction.py   # Stage 2 테스트
├── docs/                       # 문서
│   ├── Obsidian-to-GraphDB-Implementation.md  # 전체 가이드
│   └── MODEL_INFO.md               # 모델 선택 가이드
├── quick_start.sh              # Quick start 스크립트
├── requirements.txt            # 의존성 패키지
├── .env.example                # 환경변수 예시
├── .gitignore                  # Git 제외 파일
└── README.md                   # 이 파일
```

## 📊 비용 예상

Google Gemini 2.0 Flash Experimental 기준:
- **무료 티어**: 월 10 RPM (분당 요청 수) - 실험 모델이라 제한적
- **유료 (1.5 Pro 참고)**: Input $1.25 / 1M tokens, Output $5.00 / 1M tokens

예상 비용 (유료 사용 시):
- 짧은 노트 (1000자): ~$0.002-0.005
- 긴 노트 (5000자): ~$0.01-0.02
- 전체 Vault (10개 노트): ~$0.10-0.20

**Gemini 2.0 Flash의 장점:**
- 🚀 **최신 모델**: 2024년 12월 출시
- ⚡ **빠른 속도**: 1.5 Flash보다 2배 빠름
- 🎯 **높은 품질**: 1.5 Pro 수준의 정확도
- 💰 **합리적 비용**: Claude 대비 여전히 저렴
- 🔬 **실험 단계**: 무료 티어에서 최신 기술 체험 가능

## ⚠️  주의사항

1. **API 키 보안**: `.gitignore`에 `.env` 추가 필수
2. **비용 관리**: 전체 Vault 분해 전 비용 확인
3. **백업**: 원본 노트는 변경되지 않지만 백업 권장

## 🐛 문제 해결

### API 키 오류
```bash
❌ GEMINI_API_KEY가 필요합니다
```
→ 환경변수 설정: `export GEMINI_API_KEY='your-key'`
→ API 키 발급: https://makersuite.google.com/app/apikey

### JSON 파싱 오류
```bash
❌ JSON 파싱 실패
```
→ Gemini 응답이 JSON 형식이 아닐 수 있음. 노트 내용 확인

### 패키지 설치 오류
```bash
error: externally-managed-environment
```
→ 가상환경 사용: `python3 -m venv venv && source venv/bin/activate`

## 📚 참고 자료

- [전체 구현 가이드](./docs/Obsidian-to-GraphDB-Implementation.md)
- [모델 선택 가이드](./docs/MODEL_INFO.md)
- [Google Gemini API 문서](https://ai.google.dev/docs)
- [Gemini API 키 발급](https://makersuite.google.com/app/apikey)
- [Obsidian 공식 문서](https://help.obsidian.md/)

## 🚀 Git 레포지토리 설정

```bash
# Git 초기화
git init
git add .
git commit -m "Initial commit: PKM System with Atomic Notes & Entity Extraction"

# GitHub 레포지토리 연결 (레포지토리 생성 후)
git remote add origin https://github.com/your-username/pkm-system.git
git branch -M main
git push -u origin main
```

**체크리스트:**
- ✅ `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- ✅ `atomic_notes/` 폴더가 제외되는지 확인
- ✅ `venv/` 폴더가 제외되는지 확인
- ✅ `.env.example`은 포함되어야 함

## 🚀 다음 단계

**Stage 3: Neo4j Graph DB 구축**
- Neo4j 설치 및 설정
- Graph 스키마 정의
- Entity & Relationship을 Graph로 변환

## 🔐 개인정보 보호

이 레포지토리는 다음을 **자동으로 제외**합니다:

- `.env` - API 키
- `atomic_notes/` - 생성된 Atomic Notes (개인 노트 포함)
- `atomic_notes_md/` - 생성된 마크다운 파일
- `venv/` - Python 가상환경

**Git에 올리기 전 확인:**
```bash
git status  # .env와 atomic_notes가 제외되었는지 확인
```

## 📝 라이센스

MIT License

