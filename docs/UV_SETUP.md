# 🚀 uv를 사용한 빠른 설정 가이드

`uv`는 Rust로 작성된 초고속 Python 패키지 관리자입니다. `pip`보다 **10-100배 빠르고**, 가상환경 없이도 격리된 환경을 제공합니다.

## ✨ uv의 장점

- ⚡ **초고속**: pip보다 10-100배 빠른 패키지 설치
- 🔒 **격리된 환경**: 가상환경 없이도 프로젝트별 의존성 격리
- 📦 **단순한 관리**: `pyproject.toml` 기반 의존성 관리
- 🎯 **일관성**: 모든 환경에서 동일한 패키지 버전 보장

## 📦 설치

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Homebrew (macOS)

```bash
brew install uv
```

## 🏃 프로젝트 설정

### 1. 의존성 설치

```bash
cd /Users/inyoungpark/Desktop/Projects/personal/PKM
uv sync
```

이 명령어는 `pyproject.toml`에 정의된 모든 의존성을 자동으로 설치하고 `.venv` 가상환경을 생성합니다.

### 2. Neo4j Docker 시작

```bash
docker-compose up -d
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 필요한 설정을 추가합니다:

```bash
cp .env.example .env
```

`.env` 파일 내용:

```bash
# Google Gemini API Key
GEMINI_API_KEY=your-api-key-here

# Neo4j Graph Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## 🔧 uv 명령어

### 의존성 관리

```bash
# 의존성 설치 (pyproject.toml 기반)
uv sync

# 패키지 추가
uv add package-name

# 패키지 제거
uv remove package-name

# 개발 의존성 추가
uv add --dev package-name
```

### 스크립트 실행

```bash
# Python 스크립트 실행
uv run python mcp_server.py

# 특정 디렉토리에서 실행
uv run --directory /path/to/project python script.py
```

### 가상환경 관리

```bash
# 가상환경 생성 (자동)
uv sync

# 가상환경 활성화
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 가상환경 비활성화
deactivate
```

## 🔌 MCP Server 설정 (Claude Desktop)

`uv`를 사용하여 MCP 서버를 실행하려면, Claude Desktop 설정 파일을 다음과 같이 수정합니다:

**macOS 설정 파일 위치:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**설정 내용:**

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
- `--directory` 경로를 실제 프로젝트 경로로 변경하세요
- 환경 변수를 실제 값으로 변경하세요

## 🧪 테스트

### MCP 서버 수동 실행 테스트

```bash
cd /Users/inyoungpark/Desktop/Projects/personal/PKM
uv run python mcp_server.py
```

서버가 정상적으로 시작되면 다음과 같은 메시지가 나타납니다:

```
🚀 PKM Knowledge Graph MCP Server 시작 중...
   Neo4j: bolt://localhost:7687
   Agent 초기화 완료.
✅ 준비 완료! MCP 클라이언트 연결을 기다리는 중...
```

## 💡 uv vs pip 비교

| 기능 | uv | pip |
|------|----|----|
| 설치 속도 | ⚡ 10-100배 빠름 | 느림 |
| 의존성 해결 | ✅ 자동 | 수동 |
| 가상환경 | 자동 생성 | 수동 생성 필요 |
| 프로젝트 관리 | `pyproject.toml` | `requirements.txt` |
| Lock 파일 | `uv.lock` (자동) | 없음 |

## 🔄 pip에서 uv로 마이그레이션

기존 `venv` 기반 프로젝트를 `uv`로 전환하는 방법:

### 1. 기존 가상환경 삭제 (선택 사항)

```bash
rm -rf venv
```

### 2. uv로 의존성 설치

```bash
uv sync
```

`uv`는 `requirements.txt` 또는 `pyproject.toml`을 자동으로 감지하여 의존성을 설치합니다.

### 3. 기존 스크립트 업데이트

**Before (pip):**
```bash
source venv/bin/activate
python mcp_server.py
```

**After (uv):**
```bash
uv run python mcp_server.py
```

## 📚 추가 자료

- [uv 공식 문서](https://docs.astral.sh/uv/)
- [uv GitHub](https://github.com/astral-sh/uv)
- [pyproject.toml 가이드](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

## ❓ 문제 해결

### `uv: command not found`

`uv`가 PATH에 추가되지 않은 경우:

```bash
# ~/.zshrc 또는 ~/.bashrc에 추가
export PATH="$HOME/.cargo/bin:$PATH"

# 재로드
source ~/.zshrc  # or source ~/.bashrc
```

### `No solution found when resolving dependencies`

Python 버전 요구사항이 맞지 않는 경우, `pyproject.toml`의 `requires-python`을 확인하세요:

```toml
[project]
requires-python = ">=3.10"  # FastMCP는 3.10 이상 필요
```

### `ModuleNotFoundError`

의존성이 제대로 설치되지 않은 경우:

```bash
# 캐시 삭제 후 재설치
uv cache clean
uv sync
```

