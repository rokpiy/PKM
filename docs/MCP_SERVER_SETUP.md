# PKM Knowledge Graph MCP Server 설정 가이드

이 가이드는 PKM 시스템을 MCP (Model Context Protocol) 서버로 설정하여 **Gemini CLI**, Claude Desktop, Cursor 등 다른 AI 도구에서 사용할 수 있도록 합니다.

## 🚀 FastMCP 프레임워크

이 프로젝트는 **FastMCP** 프레임워크를 사용하여 MCP 서버를 구현합니다. FastMCP는 데코레이터 기반의 간결한 API를 제공하여 MCP 도구를 쉽게 정의할 수 있습니다.

**FastMCP의 장점:**
- ✅ 간결한 코드 (200줄 → 기존 대비 50% 감소)
- ✅ 데코레이터 기반 API (`@mcp.tool()`)
- ✅ 자동 타입 검증
- ✅ 빠른 개발 속도

## 🎯 MCP Server란?

MCP (Model Context Protocol)은 AI 애플리케이션이 외부 데이터와 도구에 안전하게 접근할 수 있게 해주는 프로토콜입니다. PKM MCP 서버를 통해:

- ✅ Claude Desktop에서 당신의 Knowledge Graph에 질문할 수 있습니다
- ✅ 다른 AI 도구에서도 일관된 개인화된 답변을 받을 수 있습니다
- ✅ 모든 답변이 당신의 Obsidian 노트 기반입니다

## 📦 설치

### 1. 의존성 설치

**방법 1: `uv` 사용 (권장)**

```bash
cd /Users/inyoungpark/Desktop/Projects/personal/PKM
uv sync
```

**방법 2: pip 사용**

```bash
cd /Users/inyoungpark/Desktop/Projects/personal/PKM
source venv/bin/activate
pip install fastmcp
```

FastMCP는 모든 필요한 MCP 의존성을 자동으로 설치합니다.

### 2. Neo4j 실행 확인

MCP 서버는 Neo4j가 실행 중이어야 합니다:

```bash
# Docker Compose로 Neo4j 시작 (권장)
docker-compose up -d

# 상태 확인
docker-compose ps

# Neo4j Browser: http://localhost:7474
```

### 3. 환경 변수 설정

`.env` 파일에 필요한 설정이 있는지 확인:

```bash
GEMINI_API_KEY=your-api-key-here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## 🔧 Gemini CLI 설정 (권장)

### 1. 전역 설정 파일 수정

Gemini CLI는 전역 설정 파일(`~/.gemini/settings.json`)을 사용합니다.

**macOS:**
```bash
code ~/.gemini/settings.json
```

### 2. MCP Server 추가

전역 설정 파일의 `mcpServers` 섹션에 다음을 추가:

```json
{
  "mcpServers": {
    "pkm-knowledge-graph": {
      "command": "/opt/homebrew/bin/uv",
      "args": [
        "run",
        "python",
        "mcp_server.py"
      ],
      "cwd": "/Users/inyoungpark/Desktop/Projects/personal/PKM",
      "env": {
        "GEMINI_API_KEY": "your-gemini-api-key-here",
        "GEMINI_MODEL": "gemini-2.5-flash",
        "NEO4J_URI": "neo4j://127.0.0.1:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password"
      },
      "timeout": 60000,
      "trust": true
    }
  }
}
```

**⚠️ 중요:**
- `cwd` 경로를 실제 프로젝트 경로로 변경하세요
- `GEMINI_API_KEY`를 실제 API 키로 변경하세요
- Neo4j 비밀번호를 실제 비밀번호로 변경하세요

### 3. Gemini CLI 실행

터미널에서 어느 디렉토리에서든 Gemini CLI를 실행하면 PKM MCP 서버가 자동으로 연결됩니다:

```bash
gemini
```

### 4. MCP 도구 사용 확인

Gemini CLI에서 "AI 관련 노트 찾아줘"와 같이 요청하면, MCP 서버의 도구들이 자동으로 호출됩니다.

## 🔧 Claude Desktop 설정

### 1. Claude Desktop 설정 파일 열기

**macOS:**
```bash
# Claude Desktop 설정 파일 위치
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 2. MCP Server 추가

설정 파일에 다음 내용을 추가:

**방법 1: `uv` 사용 (권장)**

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
        "GEMINI_API_KEY": "your-gemini-api-key-here",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password"
      }
    }
  }
}
```

**방법 2: 가상환경 Python 직접 사용**

```json
{
  "mcpServers": {
    "pkm-knowledge-graph": {
      "command": "/Users/inyoungpark/Desktop/Projects/personal/PKM/venv/bin/python",
      "args": [
        "/Users/inyoungpark/Desktop/Projects/personal/PKM/mcp_server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "your-gemini-api-key-here",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password"
      }
    }
  }
}
```

**⚠️ 중요:**
- `--directory` 경로 (방법 1) 또는 `args` 경로 (방법 2)를 실제 프로젝트 경로로 변경하세요
- `GEMINI_API_KEY`를 실제 API 키로 변경하세요
- Neo4j 비밀번호를 실제 비밀번호로 변경하세요

### 3. Claude Desktop 재시작

설정을 저장하고 Claude Desktop을 완전히 종료한 후 다시 시작합니다.

### 4. MCP Server 연결 확인

Claude Desktop에서 새 대화를 시작하고 🔌 아이콘을 클릭하면 "pkm-knowledge-graph" 서버가 나타나야 합니다.

## 🎨 Cursor 설정

Cursor에서도 동일한 방식으로 MCP 서버를 설정할 수 있습니다.

Cursor에서도 동일한 방식으로 MCP 서버를 설정할 수 있습니다.

### Cursor 설정 파일 위치

**macOS:**
```bash
~/.cursor/mcp_config.json
```

위와 동일한 JSON 설정을 추가하고 Cursor를 재시작합니다.

## 🛠️ 사용 가능한 도구

MCP 서버는 다음 6개의 도구를 제공합니다:

### 1. `ask_pkm`
Knowledge Graph에 질문하고 AI Agent로부터 답변을 받습니다.

**예시:**
```
Claude에서: "ask_pkm 도구를 사용해서 PKM 시스템이 무엇인지 설명해줘"
```

**파라미터:**
- `question` (필수): 질문 내용
- `depth` (선택, 기본값 2): 그래프 탐색 깊이

### 2. `search_entities`
특정 개념을 Knowledge Graph에서 검색합니다.

**예시:**
```
Claude에서: "search_entities로 'AI' 관련 개념들을 찾아줘"
```

**파라미터:**
- `query` (필수): 검색어
- `limit` (선택, 기본값 10): 반환할 최대 결과 수

### 3. `get_entity_details`
특정 개념의 상세 정보, 연결된 개념, 관련 노트를 가져옵니다.

**예시:**
```
Claude에서: "get_entity_details로 'PKM 시스템'의 상세 정보를 보여줘"
```

**파라미터:**
- `entity_name` (필수): 개념 이름
- `hops` (선택, 기본값 2): 탐색 깊이

### 4. `find_related_notes`
특정 개념과 관련된 Atomic Notes를 찾습니다.

**예시:**
```
Claude에서: "find_related_notes로 'AI'와 관련된 내 노트들을 찾아줘"
```

**파라미터:**
- `entity_name` (필수): 개념 이름
- `limit` (선택, 기본값 5): 반환할 최대 노트 수

### 5. `find_entity_path`
두 개념 사이의 연결 경로를 찾습니다.

**예시:**
```
Claude에서: "find_entity_path로 'AI'와 '스타트업' 사이의 연결을 보여줘"
```

**파라미터:**
- `start_entity` (필수): 시작 개념
- `end_entity` (필수): 끝 개념
- `max_depth` (선택, 기본값 5): 최대 탐색 깊이

### 6. `get_graph_stats`
Knowledge Graph의 전체 통계를 가져옵니다.

**예시:**
```
Claude에서: "get_graph_stats로 내 Knowledge Graph의 통계를 보여줘"
```

## 💡 사용 예시

### Claude Desktop에서 사용:

```
👤 User: PKM 시스템에 대해 설명해줘

🤖 Claude: [ask_pkm 도구를 사용하여 당신의 Knowledge Graph에서 정보를 가져옴]

PKM 시스템은 개인 지식 관리(Personal Knowledge Management)를 위한 시스템입니다...
[당신의 노트 기반 답변]

📌 참고한 개념: PKM, Obsidian, Atomic Notes
📚 참고한 노트: 3개
```

```
👤 User: AI와 머신러닝이 어떻게 연결되어 있는지 보여줘

🤖 Claude: [find_entity_path 도구를 사용]

AI와 머신러닝 사이에 2개의 연결 경로를 찾았습니다:

경로 1: AI → 딥러닝 → 머신러닝
경로 2: AI → 데이터 사이언스 → 머신러닝
```

### Gemini CLI 사용 예시:

```
👤 User: AI 관련 노트 찾아줘

🤖 Gemini: [search_entities("AI") 도구 사용]
          [find_related_notes("AI") 도구 사용]

AI와 관련된 노트를 찾았습니다:

발견된 개념:
- AI
- Machine Learning
- Deep Learning
- Neural Network

관련 노트 3개:
1. "AI 기초 개념"
   - 내용: 인공지능은...
2. "머신러닝 개요"
   - 내용: ...

이 정보들은 모두 당신의 Obsidian 노트에서 가져온 것입니다.
```

### Claude Desktop 사용 예시:

```
👤 User: 내가 지금까지 스타트업에 대해 어떤 내용을 정리했는지 알려줘

🤖 Claude: [search_entities("스타트업")을 먼저 실행]
          [그 다음 find_related_notes로 관련 노트 검색]

당신의 Knowledge Graph에서 '스타트업'과 관련된 내용을 찾았습니다:

발견된 개념:
- 스타트업
- Y Combinator
- MVP
- 네트워킹
- 투자 유치

관련 노트 3개:
1. "스타트업 초기 단계 전략"
   - 내용: MVP 개발이 최우선...
2. "Y Combinator 지원 방법"
   - 내용: ...

이 정보들은 모두 당신의 Obsidian 노트에서 가져온 것입니다.
```

## 🔍 테스트

MCP 서버를 로컬에서 직접 테스트할 수 있습니다:

```bash
cd /Users/inyoungpark/Desktop/Projects/personal/PKM
python mcp_server.py
```

서버가 정상적으로 시작되면:
```
🚀 PKM Knowledge Graph MCP Server 시작...
   Neo4j: bolt://localhost:7687
   준비 완료! MCP 클라이언트 연결을 기다리는 중...
```

## 🐛 문제 해결

### 1. "MCP SDK가 설치되어 있지 않습니다"

```bash
pip install mcp
```

### 2. "Neo4j 연결 실패"

- Neo4j Docker 컨테이너가 실행 중인지 확인: `docker-compose ps`
- Neo4j가 시작되었는지 확인: `docker-compose logs neo4j`
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` 확인

### 3. "GEMINI_API_KEY가 설정되어 있지 않습니다"

`.env` 파일 또는 MCP 설정의 `env` 섹션에 API 키 추가

### 4. Claude Desktop에서 MCP Server가 안 보임

- 설정 파일 경로가 올바른지 확인
- `args`의 Python 스크립트 경로가 절대 경로인지 확인
- Claude Desktop을 완전히 종료 후 재시작
- 설정 파일의 JSON 문법 오류 확인

## 🔐 보안 주의사항

- ⚠️ `claude_desktop_config.json`에 API 키와 비밀번호가 포함되므로 이 파일을 공유하지 마세요
- ✅ Neo4j는 로컬에서만 실행하거나, 외부 접근 시 방화벽 설정 확인
- ✅ `.env` 파일은 Git에 커밋하지 마세요 (이미 `.gitignore`에 포함됨)

## 🎉 완료!

이제 **Gemini CLI**, Claude Desktop, Cursor에서 당신의 개인 Knowledge Graph를 활용할 수 있습니다!

**다음 단계:**

**Gemini CLI 사용:**
1. 터미널에서 `gemini` 실행
2. "AI 관련 노트 찾아줘"와 같이 자연스럽게 요청
3. MCP 도구가 자동으로 호출되어 답변 제공

**Claude Desktop 사용:**
1. Claude Desktop을 열고 새 대화 시작
2. 🔌 아이콘을 클릭하여 MCP 서버 확인
3. "search_entities 도구로 'AI' 찾아줘"와 같이 요청

모든 답변이 당신의 Obsidian 노트를 기반으로 제공됩니다! 🚀

