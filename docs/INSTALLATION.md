# 📦 PKM 시스템 설치 가이드

이 문서는 PKM 시스템을 처음부터 설치하는 방법을 안내합니다.

## 📋 목차

- [사전 준비](#사전-준비)
- [방법 1: uv 사용 (권장)](#방법-1-uv-사용-권장)
- [방법 2: Docker + pip](#방법-2-docker--pip)
- [환경 변수 설정](#환경-변수-설정)
- [Neo4j 설정](#neo4j-설정)
- [문제 해결](#문제-해결)

## 사전 준비

### 필수 소프트웨어

| 소프트웨어 | 최소 버전 | 설치 확인 |
|----------|---------|---------|
| Python | 3.10+ | `python --version` |
| Docker | 최신 | `docker --version` |
| Docker Compose | 최신 | `docker-compose --version` |
| Git | 최신 | `git --version` |

### 시스템 요구사항

- **메모리**: 최소 4GB RAM (8GB 권장)
- **저장공간**: 최소 2GB 여유 공간
- **OS**: macOS, Linux, Windows (WSL2)

## 방법 1: uv 사용 (권장)

`uv`는 pip보다 **10-100배 빠른** Python 패키지 관리자입니다.

### 1. uv 설치

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Homebrew (macOS):**
```bash
brew install uv
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 프로젝트 클론

```bash
git clone https://github.com/your-username/PKM.git
cd PKM
```

### 3. 의존성 설치

```bash
# 한 번의 명령으로 가상환경 생성 + 의존성 설치
uv sync
```

이 명령어는 자동으로:
- `.venv` 가상환경 생성
- `pyproject.toml`의 모든 의존성 설치
- `uv.lock` 파일 생성 (버전 고정)

### 4. Neo4j Docker 시작

```bash
# Docker Compose로 Neo4j 시작
docker-compose up -d

# 상태 확인
docker-compose ps

# 로그 확인 (선택사항)
docker-compose logs -f neo4j
```

### 5. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env  # 또는 code .env
```

`.env` 파일 내용:
```bash
# Google Gemini API Key
# Get your key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-api-key-here

# Neo4j Graph Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-password-here
```

### 6. 설치 확인

```bash
# Python 의존성 확인
uv run python -c "import fastmcp; import google.generativeai; import neo4j; print('✅ 모든 의존성 정상')"

# Neo4j 연결 확인
uv run python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password')); driver.verify_connectivity(); print('✅ Neo4j 연결 성공'); driver.close()"
```

## 방법 2: Docker + pip

`uv` 없이 전통적인 방법으로 설치합니다.

### 1. 프로젝트 클론

```bash
git clone https://github.com/your-username/PKM.git
cd PKM
```

### 2. Python 가상환경 생성

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
.\venv\Scripts\activate   # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. Neo4j Docker 시작

```bash
docker-compose up -d
```

### 5. 환경 변수 설정

방법 1의 5단계와 동일합니다.

### 6. 설치 확인

```bash
# Python 의존성 확인
python -c "import fastmcp; import google.generativeai; import neo4j; print('✅ 모든 의존성 정상')"
```

## 환경 변수 설정

### Gemini API 키 발급

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Create API Key" 클릭
3. 프로젝트 선택 또는 새로 생성
4. 생성된 API 키 복사
5. `.env` 파일의 `GEMINI_API_KEY`에 붙여넣기

### Neo4j 비밀번호 설정

**초기 비밀번호:**
- Docker Compose가 자동으로 설정
- `docker-compose.yml`의 `NEO4J_AUTH` 환경 변수 확인

**비밀번호 변경 (선택사항):**

1. Neo4j Browser 접속: http://localhost:7474
2. 초기 비밀번호로 로그인
3. 프로필 → "Change Password"
4. 새 비밀번호 입력
5. `.env` 파일의 `NEO4J_PASSWORD` 업데이트

## Neo4j 설정

### 데이터 저장 위치

```
PKM/
└── neo4j/
    ├── data/        # 데이터베이스 파일 (영구 보관)
    ├── logs/        # 로그 파일
    ├── import/      # CSV import용
    └── plugins/     # APOC 플러그인
```

### Neo4j Browser 접속

- **URL**: http://localhost:7474
- **Bolt**: bolt://localhost:7687
- **Username**: `neo4j`
- **Password**: `.env` 파일 참고

### 유용한 명령어

```bash
# Neo4j 시작
docker-compose up -d

# Neo4j 중지
docker-compose down

# Neo4j 재시작
docker-compose restart neo4j

# 로그 확인
docker-compose logs -f neo4j

# 데이터 백업 (컨테이너 중지 필요)
docker-compose down
tar -czf neo4j-backup-$(date +%Y%m%d).tar.gz neo4j/data

# 데이터 복원
tar -xzf neo4j-backup-YYYYMMDD.tar.gz
```

## MCP Server 설정 (선택사항)

Claude Desktop, Cursor 등에서 PKM을 사용하려면:

👉 **[MCP Server 설정 가이드](MCP_SERVER_SETUP.md)**

## 문제 해결

### `uv: command not found`

**원인**: `uv`가 PATH에 추가되지 않음

**해결:**
```bash
# zsh (macOS 기본)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# bash
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### `error: externally-managed-environment`

**원인**: 시스템 Python에 직접 패키지 설치 시도

**해결:**
```bash
# 가상환경 사용
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 또는 uv 사용
uv sync
```

### `Neo4j connection failed`

**원인**: Neo4j 컨테이너가 실행 중이 아니거나 준비되지 않음

**해결:**
```bash
# 컨테이너 상태 확인
docker-compose ps

# 컨테이너가 없으면 시작
docker-compose up -d

# 로그 확인 (5-10초 대기 후 Ready 확인)
docker-compose logs neo4j | grep "Started"

# 재시작
docker-compose restart neo4j
```

### `GEMINI_API_KEY` 오류

**원인**: API 키가 설정되지 않음

**해결:**
```bash
# .env 파일 확인
cat .env | grep GEMINI_API_KEY

# .env 파일이 없으면 생성
cp .env.example .env
nano .env  # API 키 입력
```

### Docker Desktop이 실행되지 않음

**원인**: Docker Desktop이 설치되지 않았거나 실행 중이 아님

**해결:**
```bash
# macOS
open -a Docker

# Docker 설치 확인
docker --version

# Docker 설치 (Homebrew - macOS)
brew install --cask docker
```

### `ModuleNotFoundError: No module named 'xxx'`

**원인**: 의존성이 제대로 설치되지 않음

**해결:**
```bash
# uv 사용 시
uv cache clean
uv sync

# pip 사용 시
pip install --upgrade pip
pip install -r requirements.txt
```

### Neo4j 메모리 부족

**원인**: 시스템 메모리가 부족

**해결:**

`docker-compose.yml` 파일 수정:
```yaml
services:
  neo4j:
    environment:
      - NEO4J_dbms_memory_heap_initial__size=512m
      - NEO4J_dbms_memory_heap_max__size=1G
      - NEO4J_dbms_memory_pagecache_size=512m
```

## 다음 단계

설치가 완료되었다면:

1. 📚 **[사용 가이드](USAGE_GUIDE.md)** - Stage 1-5 실행 방법
2. 🔌 **[MCP Server 설정](MCP_SERVER_SETUP.md)** - Claude Desktop 연동
3. 🐳 **[Docker 상세 가이드](DOCKER_SETUP.md)** - Neo4j Docker 관리
4. ⚡ **[uv 사용 가이드](UV_SETUP.md)** - uv 고급 사용법

## 추가 자료

- [전체 프로젝트 가이드](../README.md)
- [Neo4j 공식 문서](https://neo4j.com/docs/)
- [Google Gemini API 문서](https://ai.google.dev/docs)
- [FastMCP 문서](https://github.com/jlowin/fastmcp)
- [uv 공식 문서](https://docs.astral.sh/uv/)

