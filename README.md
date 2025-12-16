# PKM (Personal Knowledge Management) System

> Obsidian → Atomic Notes → Knowledge Graph → MCP Server

**개인 지식을 Knowledge Graph로 변환하고 AI 도구에서 활용**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.14.0-green)](https://neo4j.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5--flash-orange)](https://ai.google.dev/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.14.1-purple)](https://github.com/jlowin/fastmcp)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

## 🎯 주요 기능

- ✅ **Obsidian 노트 자동 분해** - 단일 개념 단위로 Atomic Notes 생성 (Gemini AI)
- ✅ **Entity & Relationship 추출** - AI + Regex 기반 지식 그래프 구성
- ✅ **Neo4j Knowledge Graph** - 강력한 그래프 쿼리 및 시각화
- ✅ **MCP Server** - Claude Desktop, Cursor 등 AI 도구와 연동
- ✅ **Raw Data 제공** - Reasoning은 Claude/Cursor가 직접 수행

## ⚡ Quick Start

### 방법 1: uv 사용 (권장 - 10-100배 빠름)

```bash
# 1. uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 의존성 설치
cd PKM
uv sync

# 3. Neo4j 시작
docker-compose up -d

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일에 GEMINI_API_KEY 입력

# 5. Knowledge Graph 구축 (Stage 1-3)
./quick_start.sh
# → 옵션 4 선택 (전체 파이프라인)

# 6. MCP Server 설정
# Claude Desktop에서 사용 (docs/MCP_SERVER_SETUP.md 참고)
```

👉 **[uv 빠른 시작 가이드](docs/QUICKSTART_UV.md)** - 5분 만에 완료!

### 방법 2: Docker + pip

```bash
# 1. 가상환경 및 의존성 설치
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Neo4j 시작
docker-compose up -d

# 3. 환경 변수 설정
cp .env.example .env

# 4. Knowledge Graph 구축
./quick_start.sh
```

## 🏛️ 시스템 아키텍처

```
📝 Obsidian Vault (Your Notes)
    │
    ├─ Markdown files with frontmatter, links, tags
    │
    ▼
┌─────────────────────┐
│  Stage 1: Atomic    │  ← Gemini 2.5-flash
│  Note Agent         │     (LLM 기반 분해)
└─────────────────────┘
    │
    ├─ atomic_notes/*.json
    │
    ▼
┌─────────────────────┐
│  Stage 2: Entity &  │  ← Regex + Gemini
│  Relationship       │     Enhancement
└─────────────────────┘
    │
    ├─ *_enhanced.json
    │
    ▼
┌─────────────────────┐
│  Stage 3: Neo4j     │  ← Neo4j 5.14.0
│  Graph DB Import    │     (Docker)
└─────────────────────┘
    │
    │  Cypher Queries (Raw Data)
    ▼
┌──────────────────────────────────────┐
│     Neo4j Knowledge Graph            │
│                                      │
│  Nodes: AtomicNote, Entity           │
│  Relationships: MENTIONS, SUPPORTS   │
│                 USES, CAUSES, etc.   │
└──────────────────────────────────────┘
    │
    │  Raw Data (JSON)
    ▼
┌─────────────────────────────────────┐
│   MCP Server (FastMCP)              │
│                                     │
│   6 Tools:                          │
│   • search_entities                 │
│   • get_entity_graph                │
│   • find_related_notes              │
│   • find_entity_path                │
│   • get_graph_stats                 │
│   • run_cypher_query                │
└─────────────────────────────────────┘
    │
    ├─────────────┬──────────────┐
    │             │              │
    ▼             ▼              ▼
Claude       Cursor        VS Code
Desktop                  + Continue
    │             │              │
    └─────────────┴──────────────┘
           Reasoning은 LLM이 직접!
```

## 📊 구현 단계

| Stage | 기능 | 상태 | 설명 |
|-------|------|------|------|
| **1** | Atomic Notes 생성 | ✅ 완료 | Obsidian 노트를 단일 개념으로 분해 |
| **2** | Entity & Relationship 추출 | ✅ 완료 | AI 기반 엔티티 및 관계 추출 |
| **3** | Neo4j Graph DB 구축 | ✅ 완료 | Knowledge Graph로 변환 |
| **MCP** | MCP Server | ✅ 완료 | Raw Data 제공, Reasoning은 LLM |

## 🔑 핵심 철학

### MCP = Raw Data Provider

**기존 (잘못된 접근):**
```
User → Claude → MCP → Gemini API (Reasoning) → Raw Data → Claude
                         ❌ 이중 LLM 비용, 투명성 부족
```

**현재 (올바른 접근):**
```
User → Claude → MCP → Raw Data from Neo4j → Claude (Reasoning)
                ✅ 비용 절감, 투명성, Claude 능력 최대 활용
```

**장점:**
- 💰 **비용 절감**: Gemini API 불필요, Claude만 사용
- 🔍 **투명성**: Claude가 어떤 데이터를 사용했는지 명확
- 🧠 **더 나은 Reasoning**: Claude가 raw data로 더 깊은 분석
- 📊 **유연성**: 사용자가 원하는 도구 조합 가능

## 🛠️ 기술 스택

| 계층 | 기술 | 용도 |
|-----|------|------|
| **Input** | Obsidian, Markdown | 노트 작성 및 관리 |
| **LLM** | Google Gemini 2.5-flash | Atomic 분해, Entity 추출만 |
| **Database** | Neo4j 5.14.0 (Docker) | Knowledge Graph 저장 |
| **Backend** | Python 3.10+ | 데이터 처리 |
| **Graph Query** | Cypher | Graph 탐색 및 쿼리 |
| **MCP Framework** | FastMCP | MCP 서버 구현 |
| **Reasoning** | Claude / Cursor / etc. | **LLM이 직접 Reasoning** |
| **Container** | Docker Compose | Neo4j 격리 및 배포 |
| **Package Manager** | uv (권장) / pip | Python 의존성 관리 |

## 🎯 Atomic Note 원칙

PKM 시스템은 **Zettelkasten** 방법론을 따릅니다:

1. **단일 책임** (Single Responsibility) - 하나의 개념/아이디어만 포함
2. **독립성** (Independence) - 독립적으로 이해 가능
3. **연결성** (Connectivity) - 다른 노트와 링크 가능
4. **구조화** (Structure) - 명확한 메타데이터 포함

## 🔧 프로젝트 구조

```
PKM/
├── src/                           # 핵심 소스 코드
│   ├── obsidian_loader.py              # Obsidian Vault 로더
│   ├── atomic_note_agent.py            # Stage 1: Atomic Notes
│   ├── entity_extraction_simple.py     # Stage 2: Entity Extraction
│   └── graph_db.py                     # Stage 3: Neo4j Manager
│
├── tests/                         # 테스트 스크립트
│   ├── test_atomic_agent.py            # Stage 1 테스트
│   ├── test_entity_extraction.py       # Stage 2 테스트
│   ├── test_graph_import.py            # Stage 3 테스트
│   └── regenerate_markdown.py          # Markdown 재생성
│
├── docs/                          # 문서
│   ├── INSTALLATION.md                 # 설치 가이드
│   ├── USAGE_GUIDE.md                  # 사용 가이드
│   ├── QUICKSTART_UV.md                # uv 빠른 시작
│   ├── QUICKSTART_DOCKER.md            # Docker 빠른 시작
│   ├── MCP_SERVER_SETUP.md             # MCP 서버 설정
│   ├── DOCKER_SETUP.md                 # Docker 상세 가이드
│   ├── UV_SETUP.md                     # uv 상세 가이드
│   └── Obsidian-to-GraphDB-Implementation.md  # 구현 가이드
│
├── scripts/                       # 유틸리티 스크립트
│   ├── start_neo4j.sh                  # Neo4j 시작
│   └── stop_neo4j.sh                   # Neo4j 중지
│
├── mcp_server.py                  # MCP Server (FastMCP)
├── quick_start.sh                 # Quick Start 스크립트
├── docker-compose.yml             # Neo4j Docker 설정
├── pyproject.toml                 # uv 프로젝트 설정
├── requirements.txt               # pip 의존성
├── .env.example                   # 환경 변수 예시
└── README.md                      # 이 파일
```

## 📚 문서

### 빠른 시작
- 📖 **[설치 가이드](docs/INSTALLATION.md)** - 처음부터 설치하기
- 📖 **[사용 가이드](docs/USAGE_GUIDE.md)** - Stage 1-3 상세 사용법
- ⚡ **[uv 빠른 시작](docs/QUICKSTART_UV.md)** - 5분 만에 시작하기
- 🐳 **[Docker 빠른 시작](docs/QUICKSTART_DOCKER.md)** - Docker로 3분 만에 시작하기

### 고급 가이드
- 🔌 **[MCP Server 설정](docs/MCP_SERVER_SETUP.md)** - Claude Desktop / Cursor 연동
- 🐳 **[Docker 가이드](docs/DOCKER_SETUP.md)** - Neo4j Docker 관리
- ⚡ **[uv 가이드](docs/UV_SETUP.md)** - uv 고급 사용법

### 프로젝트 문서
- 📋 **[전체 구현 가이드](docs/Obsidian-to-GraphDB-Implementation.md)** - 프로젝트 설계 및 구현 세부사항

## 💰 비용 안내

### Google Gemini 2.5-flash (Stage 1-2에서만 사용)

**무료 티어:**
- 15 RPM (분당 요청)
- 1,500 RPD (일일 요청)
- 1 Million TPM (분당 토큰)

**예상 비용 (무료 티어 초과 시):**
- 짧은 노트 (1000자): ~$0.001-0.002
- 긴 노트 (5000자): ~$0.005-0.01
- 전체 Vault (10개 노트): ~$0.05-0.10

### Claude Desktop (Reasoning에 사용)

**무료 티어:**
- 충분한 사용량 제공

**장점:**
- ✅ MCP 서버는 **Gemini API 불필요** (Graph DB에서 raw data만 제공)
- ✅ Reasoning은 Claude가 무료로 처리
- ✅ 전체 비용 = Stage 1-2 처리 비용만

### Neo4j (Docker)

- 💾 **무료**: Community Edition 사용
- 📦 **로컬 실행**: 클라우드 비용 없음
- 🔒 **데이터 소유권**: 모든 데이터가 로컬에 저장

## 🔌 MCP Server로 AI 도구와 연동

PKM 시스템을 **Claude Desktop, Cursor** 등에서 사용할 수 있습니다!

### MCP Server가 제공하는 도구 (6개)

1. **`search_entities`** - 개념(Entity) 검색
2. **`get_entity_graph`** - 특정 개념 주변 그래프
3. **`find_related_notes`** - 관련 Atomic Notes 찾기
4. **`find_entity_path`** - 두 개념 간 연결 경로
5. **`get_graph_stats`** - Knowledge Graph 통계
6. **`run_cypher_query`** - 사용자 정의 Cypher 쿼리

### 빠른 설정

```bash
# 1. Knowledge Graph 구축 (Stage 1-3)
./quick_start.sh

# 2. MCP Server 테스트
uv run python mcp_server.py

# 3. Claude Desktop 설정
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**설정 예시 (uv 사용):**

```json
{
  "mcpServers": {
    "pkm-knowledge-graph": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/PKM", "python", "mcp_server.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password"
      }
    }
  }
}
```

👉 **[MCP Server 설정 가이드](docs/MCP_SERVER_SETUP.md)** - 자세한 설정 방법

### Claude Desktop 사용 예시

```
👤 User: AI와 머신러닝이 어떻게 연결되어 있는지 알려줘

🤖 Claude: 
[search_entities 도구 사용]
[find_entity_path 도구 사용]
[find_related_notes 도구 사용]

AI와 머신러닝은 다음과 같이 연결되어 있습니다:

경로 1: AI → is_parent_of → 머신러닝
경로 2: AI → includes → 딥러닝 → is_part_of → 머신러닝

당신의 노트에 따르면...
[raw data를 기반으로 Claude가 직접 reasoning]
```

## 🐛 문제 해결

### 자주 묻는 질문

**Q: Neo4j 연결 실패**
```bash
# Docker 상태 확인
docker-compose ps

# Neo4j 재시작
docker-compose restart neo4j

# 로그 확인
docker-compose logs neo4j
```

**Q: `uv: command not found`**
```bash
# PATH 추가
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Q: MCP Server가 Claude에서 보이지 않음**
```bash
# 1. Neo4j 실행 확인
docker-compose ps

# 2. MCP 서버 수동 테스트
uv run python mcp_server.py

# 3. Claude Desktop 로그 확인 (Cmd+Option+I)
```

더 많은 문제 해결 방법은 **[설치 가이드](docs/INSTALLATION.md#문제-해결)**를 참고하세요.

## 🔐 개인정보 보호

`.gitignore`에 다음이 자동으로 제외됩니다:
- `.env` - API 키
- `atomic_notes/` - 생성된 Atomic Notes
- `atomic_notes_md/` - 생성된 Markdown
- `.venv/`, `venv/` - Python 가상환경
- `neo4j/data/` - Neo4j 데이터베이스
- `mcp_config.json` - 로컬 MCP 설정

## 🚀 다음 단계

**현재 완료:**
- ✅ Stage 1-3: Knowledge Graph 구축
- ✅ MCP Server: Raw Data 제공
- ✅ Claude/Cursor 연동

**향후 계획:**
- 🔜 **Vector Search 통합** - Semantic Search 강화
- 🔜 **Web Interface** - 시각적 Graph 탐색
- 🔜 **Real-time Sync** - Obsidian ↔ Neo4j 양방향 동기화
- 🔜 **Multi-Vault 지원** - 여러 Obsidian Vault 통합

## 📝 라이센스

MIT License

## 🙏 감사의 말

- [Obsidian](https://obsidian.md/) - 강력한 노트 작성 도구
- [Neo4j](https://neo4j.com/) - 뛰어난 Graph Database
- [Google Gemini](https://ai.google.dev/) - 고품질 LLM API
- [FastMCP](https://github.com/jlowin/fastmcp) - 간편한 MCP 서버 프레임워크
- [uv](https://github.com/astral-sh/uv) - 초고속 Python 패키지 관리자
- [Anthropic Claude](https://www.anthropic.com/) - MCP와 함께하는 최고의 AI Assistant

---

**Made with ❤️ for Personal Knowledge Management**

**MCP 철학: Raw Data Provider, Reasoning은 LLM에게**
