# 📖 PKM 시스템 사용 가이드

이 문서는 PKM 시스템의 Knowledge Graph 구축(Stage 1-3)과 MCP Server 사용 방법을 설명합니다.

## 📋 목차

- [Quick Start](#quick-start)
- [Stage 1: Atomic Notes 생성](#stage-1-atomic-notes-생성)
- [Stage 2: Entity & Relationship 추출](#stage-2-entity--relationship-추출)
- [Stage 3: Neo4j Graph DB Import](#stage-3-neo4j-graph-db-import)
- [MCP Server로 AI 도구에서 사용](#mcp-server로-ai-도구에서-사용)
- [Python 코드로 직접 사용](#python-코드로-직접-사용)
- [출력 구조](#출력-구조)

## Quick Start

### 자동화 스크립트 사용 (가장 쉬운 방법)

```bash
./quick_start.sh
```

**메뉴 옵션:**
1. Stage 1: Atomic Notes 생성
2. Stage 2: Entity & Relationship 추출
3. Stage 3: Neo4j Graph DB Import
4. 전체 파이프라인 실행 (Stage 1 + 2 + 3)
5. 종료

### 전체 파이프라인 자동 실행

```bash
# Option 4 선택
./quick_start.sh
```

자동으로 Stage 1 → 2 → 3이 순차 실행됩니다.

## Stage 1: Atomic Notes 생성

Obsidian 노트를 **단일 개념** 단위로 분해합니다.

### 실행 방법

**uv 사용:**
```bash
uv run python src/atomic_note_agent.py
```

**pip 사용:**
```bash
python src/atomic_note_agent.py
```

### 선택 옵션

#### 1. 단일 노트 테스트
자동으로 적당한 크기의 노트를 선택하여 테스트합니다.

#### 2. 특정 노트 선택
노트 목록이 표시되면 원하는 번호를 입력합니다.

**사용 예시:**
- 단일 선택: `3`
- 여러 개: `1,3,5`
- 범위: `1-5`
- 혼합: `1,3-5,7,10-12`

#### 3. 전체 Vault 분해
모든 노트를 처리합니다.

**Idempotency (중복 방지):**
- 이미 처리된 노트는 자동으로 스킵
- JSON 파일이 존재하면 재처리하지 않음
- 강제 재생성 옵션 제공

### 출력 결과

```
PKM/
├── atomic_notes/
│   └── note_name_atomic.json        # JSON 형식
└── atomic_notes_md/
    └── note_20231027_001_title.md   # Markdown 형식
```

### Atomic Note 예시

**JSON 출력 (`*_atomic.json`):**
```json
{
  "original_note_title": "AI and Machine Learning",
  "source_file": "~/Documents/Obsidian Vault/AI.md",
  "atomic_notes": [
    {
      "id": "note_20251216_001",
      "title": "인공지능의 정의",
      "content": "인공지능(AI)은 인간의 학습, 추론, 문제 해결 능력을 모방하는 컴퓨터 시스템입니다.",
      "detailed_content": "인공지능은 1956년 다트머스 회의에서 처음 제안된 개념으로...",
      "extracted_entities": ["AI", "머신러닝", "딥러닝"],
      "relationships": [
        {
          "from": "AI",
          "type": "is_parent_of",
          "to": "머신러닝",
          "confidence": 0.95
        }
      ],
      "domain": "technology",
      "confidence": "high"
    }
  ],
  "hierarchy": {
    "AI": ["머신러닝", "딥러닝"],
    "머신러닝": ["지도학습", "비지도학습"]
  },
  "summary": "인공지능의 개념과 하위 분야인 머신러닝에 대한 개괄적인 설명"
}
```

**Markdown 출력 (`note_YYYYMMDD_001_title.md`):**
```markdown
---
type: atomic_note
source: AI and Machine Learning
id: note_20251216_001
domain: technology
confidence: high
entities: ["AI", "머신러닝", "딥러닝"]
---

# 인공지능의 정의

## 핵심 개념
인공지능(AI)은 인간의 학습, 추론, 문제 해결 능력을 모방하는 컴퓨터 시스템입니다.

## 상세 내용
인공지능은 1956년 다트머스 회의에서 처음 제안된 개념으로...

## 추출된 엔티티
`AI`, `머신러닝`, `딥러닝`

## 관계
- `AI` --[is_parent_of]--> `머신러닝`
```

## Stage 2: Entity & Relationship 추출

Atomic Notes에서 엔티티와 관계를 추출하여 강화합니다.

### 실행 방법

**uv 사용:**
```bash
uv run python src/entity_extraction_simple.py
```

**pip 사용:**
```bash
python src/entity_extraction_simple.py
```

### 처리 과정

1. **`*_atomic.json` 파일 로드**
2. **Gemini 결과 개선**: 기존 엔티티 및 관계 검증
3. **Regex 패턴 매칭**: 추가 관계 추출
   - 한글 패턴: "A는 B이다", "A가 B를 하다"
   - 영문 패턴: "A is B", "A uses B"
4. **`*_atomic_enhanced.json` 저장**

### 출력 결과

```
PKM/
└── atomic_notes/
    ├── note_name_atomic.json              # Stage 1 출력
    └── note_name_atomic_enhanced.json     # Stage 2 출력 (강화됨)
```

### Enhanced JSON 예시

```json
{
  "original_note_title": "AI and Machine Learning",
  "atomic_notes": [
    {
      "id": "note_20251216_001",
      "extracted_entities": ["AI", "머신러닝", "딥러닝", "신경망"],
      "relationships": [
        {
          "from": "AI",
          "type": "is_parent_of",
          "to": "머신러닝",
          "confidence": 0.95,
          "method": "gemini"
        },
        {
          "from": "딥러닝",
          "type": "uses",
          "to": "신경망",
          "confidence": 0.85,
          "method": "regex"
        }
      ]
    }
  ]
}
```

## Stage 3: Neo4j Graph DB Import

Enhanced JSON을 Neo4j Graph Database로 가져옵니다.

### 1. Neo4j 시작 확인

```bash
# Neo4j 실행 확인
docker-compose ps

# 실행 중이 아니면 시작
docker-compose up -d

# 로그 확인 (Ready 메시지 확인)
docker-compose logs -f neo4j
```

### 2. Graph DB Import 실행

**uv 사용:**
```bash
uv run python tests/test_graph_import.py
```

**pip 사용:**
```bash
python tests/test_graph_import.py
```

### 3. Import 옵션 선택

**Option 1: 기존 데이터 유지하고 추가**
- 새로운 노트만 추가
- 기존 데이터는 그대로 유지
- `MERGE` 사용으로 중복 방지

**Option 2: 모든 데이터 삭제 후 새로 시작**
- 전체 Graph DB 초기화
- 모든 노드와 관계 삭제
- 처음부터 다시 Import

### 4. Neo4j Browser에서 확인

브라우저에서 http://localhost:7474 접속

**유용한 Cypher 쿼리:**

```cypher
// 1. 전체 통계
MATCH (n) RETURN labels(n) as label, count(*) as count

// 2. 모든 Atomic Notes 보기
MATCH (n:AtomicNote) RETURN n LIMIT 25

// 3. 특정 Entity 주변 그래프
MATCH (e:Entity {name: "AI"})-[r]-(related)
RETURN e, r, related

// 4. 가장 많이 연결된 Entity Top 10
MATCH (e:Entity)-[r]-()
RETURN e.name as name, count(r) as connections
ORDER BY connections DESC
LIMIT 10

// 5. Domain별 Entity 수
MATCH (e:Entity)
RETURN e.domain as domain, count(*) as count
ORDER BY count DESC

// 6. Entity 간 연결 경로 찾기
MATCH path = shortestPath(
  (start:Entity {name: "AI"})-[*..5]-(end:Entity {name: "딥러닝"})
)
RETURN path

// 7. 특정 노트가 언급하는 모든 Entity
MATCH (n:AtomicNote {title: "인공지능의 정의"})-[:MENTIONS]->(e:Entity)
RETURN n, e

// 8. 가장 많이 언급된 Entity
MATCH (n:AtomicNote)-[:MENTIONS]->(e:Entity)
RETURN e.name as entity, count(n) as mentions
ORDER BY mentions DESC
LIMIT 10
```

### Graph 시각화

Neo4j Browser의 **"Explore"** 탭에서:

1. 왼쪽 패널에서 Node Label 클릭 (`Entity`, `AtomicNote`)
2. 원하는 노드를 더블클릭하여 연결된 노드 확장
3. 관계 타입별 색상 자동 구분
4. 드래그로 노드 위치 조정

## MCP Server로 AI 도구에서 사용

Stage 1-3 완료 후, MCP Server를 통해 Claude Desktop, Cursor 등에서 Knowledge Graph를 활용할 수 있습니다.

### MCP Server 철학

**Raw Data만 제공, Reasoning은 LLM이 담당**

- ✅ MCP Server는 Neo4j에서 데이터만 가져옴
- ✅ Claude/Cursor가 raw data로 reasoning 수행
- ✅ 이중 LLM 비용 없음 (Gemini API 불필요)
- ✅ 투명성과 유연성 극대화

### MCP Server가 제공하는 도구 (6개)

1. **`search_entities`** - 개념(Entity) 검색
2. **`get_entity_graph`** - 특정 개념 주변 그래프 가져오기
3. **`find_related_notes`** - 관련 Atomic Notes 찾기
4. **`find_entity_path`** - 두 개념 간 연결 경로 찾기
5. **`get_graph_stats`** - Knowledge Graph 통계
6. **`run_cypher_query`** - 사용자 정의 Cypher 쿼리 실행

### MCP Server 설정

**1. MCP Server 테스트 실행:**

```bash
# uv 사용
uv run python mcp_server.py

# pip 사용
python mcp_server.py
```

**2. Claude Desktop 설정:**

`~/Library/Application Support/Claude/claude_desktop_config.json` 파일 편집:

```json
{
  "mcpServers": {
    "pkm-knowledge-graph": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/inyoungpark/Desktop/Projects/personal/PKM",
        "python",
        "mcp_server.py"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password"
      }
    }
  }
}
```

**3. Claude Desktop 재시작**

설정을 저장하고 Claude Desktop을 완전히 종료한 후 다시 시작합니다.

**4. 연결 확인**

Claude Desktop에서 🔌 아이콘을 클릭하면 "pkm-knowledge-graph" 서버가 나타나야 합니다.

### Claude Desktop 사용 예시

**예시 1: Entity 검색 및 관계 탐색**

```
👤 User: AI와 머신러닝이 어떻게 연결되어 있는지 알려줘

🤖 Claude: 
[search_entities("AI") 도구 사용]
[search_entities("머신러닝") 도구 사용]
[find_entity_path("AI", "머신러닝") 도구 사용]
[find_related_notes("AI") 도구 사용]

당신의 Knowledge Graph에 따르면, AI와 머신러닝은 다음과 같이 연결되어 있습니다:

**경로 1:** AI → is_parent_of → 머신러닝
**경로 2:** AI → includes → 딥러닝 → is_part_of → 머신러닝

당신의 노트 "인공지능의 정의"에서는...
[raw data를 기반으로 Claude가 직접 reasoning]
```

**예시 2: 관련 개념 찾기**

```
👤 User: 네트워킹과 관련된 스타트업 개념들 보여줘

🤖 Claude:
[search_entities("네트워킹") 도구 사용]
[get_entity_graph("네트워킹", depth=2) 도구 사용]

네트워킹과 관련된 개념들을 찾았습니다:

1. **직접 연결:**
   - 스타트업 (supports)
   - 투자자 관계 (related_to)
   - 멘토링 (includes)

2. **2단계 연결:**
   - 성장전략 (via 스타트업)
   - 파트너십 (via 투자자 관계)

당신의 노트에서...
```

**예시 3: 사용자 정의 쿼리**

```
👤 User: 가장 많이 언급된 개념 TOP 5를 보여줘

🤖 Claude:
[run_cypher_query("MATCH (n:AtomicNote)-[:MENTIONS]->(e:Entity) RETURN e.name as entity, count(n) as mentions ORDER BY mentions DESC LIMIT 5")]

가장 많이 언급된 개념 TOP 5:

1. AI - 12번 언급
2. 스타트업 - 8번 언급
3. 네트워킹 - 7번 언급
4. 머신러닝 - 6번 언급
5. 성장전략 - 5번 언급

이는 당신이...
```

### 장점

**MCP Server 방식의 장점:**

1. **비용 절감** - Gemini API 불필요, Claude만 사용
2. **투명성** - Claude가 어떤 데이터를 사용했는지 명확
3. **더 나은 Reasoning** - Claude가 raw data로 더 깊은 분석
4. **유연성** - 사용자가 원하는 도구 조합 가능
5. **확장성** - 새로운 Cypher 쿼리 자유롭게 실행

👉 **[MCP Server 설정 가이드](MCP_SERVER_SETUP.md)** - 상세한 설정 방법

## Python 코드로 직접 사용

### Stage 1 직접 실행

```python
import sys
from pathlib import Path

# src 폴더를 경로에 추가
sys.path.insert(0, str(Path('src')))

from atomic_note_agent import AtomicNoteAgent
from obsidian_loader import ObsidianVaultLoader

# Agent 초기화
agent = AtomicNoteAgent()

# Vault 로드
loader = ObsidianVaultLoader("~/Documents/Obsidian Vault")
notes = loader.load_vault()

# 단일 노트 분해
result = agent.decompose_note(notes[0])
print(f"생성된 Atomic Notes: {len(result['atomic_notes'])}개")

# 전체 Vault 분해
results = agent.decompose_vault(
    "~/Documents/Obsidian Vault",
    output_dir="./atomic_notes",
    skip_existing=True  # 이미 처리된 노트 스킵
)

# Markdown으로 저장
agent.save_as_markdown(result, "./atomic_notes_md")
```

### Stage 2 직접 실행

```python
from entity_extraction_simple import SimpleEntityExtractor

# Extractor 초기화
extractor = SimpleEntityExtractor()

# JSON 파일 로드 및 처리
import json
with open("atomic_notes/note_name_atomic.json", "r") as f:
    atomic_data = json.load(f)

# Entity 추출
enhanced_data = extractor.enhance_atomic_notes(atomic_data)

# 저장
with open("atomic_notes/note_name_atomic_enhanced.json", "w") as f:
    json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
```

### Stage 3 직접 실행

```python
from graph_db import GraphDBManager

# DB 초기화
db = GraphDBManager("bolt://localhost:7687", ("neo4j", "password"))

# 스키마 생성
db.create_schema()

# Atomic Note 추가
note_data = {
    "id": "note_001",
    "title": "인공지능의 정의",
    "content": "AI는...",
    "domain": "technology"
}
db.create_atomic_note_node(note_data)

# Entity 추가
entity_id = db.create_entity_node("AI", {
    "label": "CONCEPT",
    "domain": "technology",
    "confidence": 0.95
})

# 관계 추가
db.create_relationship("AI", "is_parent_of", "머신러닝", confidence=0.9)

# Note와 Entity 연결
db.link_note_to_entity("note_001", "AI")

# 통계 확인
stats = db.get_graph_stats()
print(stats)

# 정리
db.close()
```

## 출력 구조

```
PKM/
├── atomic_notes/                    # Stage 1-2 출력
│   ├── note_name_atomic.json              # Stage 1: Atomic Notes
│   └── note_name_atomic_enhanced.json     # Stage 2: Enhanced
│
├── atomic_notes_md/                 # Stage 1 Markdown 출력
│   └── note_YYYYMMDD_001_title.md
│
├── neo4j/                           # Stage 3: Graph DB
│   ├── data/                              # 데이터베이스 파일
│   ├── logs/                              # 로그
│   ├── import/                            # CSV import
│   └── plugins/                           # APOC 플러그인
│
└── src/                             # 소스 코드
    ├── obsidian_loader.py
    ├── atomic_note_agent.py
    ├── entity_extraction_simple.py
    └── graph_db.py
```

## 다음 단계

- 🔌 **[MCP Server 설정](MCP_SERVER_SETUP.md)** - Claude Desktop 연동
- 📦 **[설치 가이드](INSTALLATION.md)** - 처음부터 설치
- 🐳 **[Docker 가이드](DOCKER_SETUP.md)** - Neo4j Docker 관리
- ⚡ **[uv 가이드](UV_SETUP.md)** - uv 고급 사용법

## 문제 해결

일반적인 문제는 [설치 가이드의 문제 해결 섹션](INSTALLATION.md#문제-해결)을 참고하세요.
