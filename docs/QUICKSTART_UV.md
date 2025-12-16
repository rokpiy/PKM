# 🚀 PKM Knowledge Graph - uv 빠른 시작 가이드

`uv`를 사용하면 **10-100배 빠른 설치 속도**로 PKM 시스템을 설정할 수 있습니다!

## ⚡ 5분 만에 시작하기

### 1️⃣ uv 설치 (아직 없다면)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Homebrew (macOS)
brew install uv
```

### 2️⃣ 프로젝트 클론 & 의존성 설치

```bash
# 프로젝트 디렉토리로 이동
cd /Users/inyoungpark/Desktop/Projects/personal/PKM

# 의존성 설치 (pip보다 10-100배 빠름!)
uv sync
```

### 3️⃣ Neo4j Docker 시작

```bash
# Neo4j 컨테이너 시작
docker-compose up -d

# 상태 확인
docker-compose ps
```

### 4️⃣ 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 열어 API 키와 비밀번호 입력
# GEMINI_API_KEY=your-api-key-here
# NEO4J_PASSWORD=password
```

### 5️⃣ MCP 서버 실행 (Claude Desktop)

**Claude Desktop 설정 파일 열기:**

```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**다음 내용 추가:**

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

**⚠️ 중요:**
- `--directory` 경로를 실제 프로젝트 경로로 변경
- 환경 변수를 실제 값으로 변경

### 6️⃣ Claude Desktop 재시작

설정을 저장하고 Claude Desktop을 완전히 종료한 후 다시 시작합니다.

## ✅ 완료!

이제 Claude Desktop에서 🔌 아이콘을 클릭하면 "pkm-knowledge-graph" 서버가 나타납니다.

**사용 예시:**
```
👤 User: PKM 시스템에 대해 설명해줘

🤖 Claude: [ask_pkm 도구를 사용하여 Knowledge Graph에서 정보 검색]

PKM 시스템은 개인 지식 관리(Personal Knowledge Management)를 위한 
시스템입니다...
```

## 🎯 다음 단계

### Obsidian 노트 처리

```bash
# Stage 1: Atomic Notes 생성
uv run python src/atomic_note_agent.py

# Stage 2: Entity & Relationship 추출
uv run python src/entity_extraction_simple.py

# Stage 3: Neo4j Graph DB Import
uv run python src/graph_db_importer.py
```

### 또는 전체 파이프라인 실행

```bash
./quick_start.sh
```

## 📚 추가 문서

- **[전체 README](README.md)** - 프로젝트 전체 가이드
- **[uv 사용 가이드](docs/UV_SETUP.md)** - uv 상세 사용법
- **[MCP Server 설정](docs/MCP_SERVER_SETUP.md)** - MCP 서버 상세 설정
- **[Docker 설정](docs/DOCKER_SETUP.md)** - Neo4j Docker 설정

## ❓ 문제 해결

### uv 명령어를 찾을 수 없음

```bash
# PATH에 추가
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Neo4j 연결 오류

```bash
# Neo4j 컨테이너 재시작
docker-compose restart neo4j

# 로그 확인
docker-compose logs neo4j
```

### MCP 서버 연결 오류

Claude Desktop의 개발자 도구 (Cmd+Option+I)에서 로그를 확인하세요.

## 🚀 uv의 장점

- ⚡ **10-100배 빠른 설치**: pip보다 훨씬 빠름
- 🔒 **격리된 환경**: 프로젝트별 의존성 자동 관리
- 📦 **간단한 명령어**: `uv sync` 하나로 모든 설정 완료
- 🎯 **일관성**: 모든 환경에서 동일한 패키지 버전 보장

