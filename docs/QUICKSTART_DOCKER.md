# 🚀 Docker 빠른 시작 (3분)

PKM 시스템을 Docker로 가장 빠르게 시작하는 방법입니다.

## ✅ 1단계: Docker Desktop 시작

**macOS/Windows:**
- Docker Desktop 애플리케이션 실행
- 상단 메뉴바에서 고래 아이콘 확인

**Linux:**
```bash
sudo systemctl start docker
```

**확인:**
```bash
docker ps
```

## ✅ 2단계: 프로젝트 클론 및 설정

```bash
# 프로젝트 클론
git clone https://github.com/your-username/PKM.git
cd PKM

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# .env 파일 생성
cp .env.example .env
# .env 파일을 열어서 GEMINI_API_KEY 입력
```

## ✅ 3단계: Neo4j Docker 시작

```bash
# 간단한 방법
./scripts/start_neo4j.sh

# 또는
docker-compose up -d
```

**확인:**
- 🌐 http://localhost:7474 접속
- Username: `neo4j`
- Password: `.env` 파일의 `NEO4J_PASSWORD`

## ✅ 4단계: PKM 시스템 실행

```bash
# Quick Start 스크립트 실행
./quick_start.sh

# 메뉴에서 선택:
# 1 - Atomic Notes 생성
# 2 - Entity 추출
# 3 - Graph DB Import
# 4 - Knowledge Graph Reasoning
# 5 - Agentic Reasoning
```

## 🎯 전체 파이프라인 실행

```bash
# Option 6 선택: 전체 파이프라인 (Stage 1 + 2 + 3)
./quick_start.sh
```

## 🐛 문제 해결

### "Docker가 실행되고 있지 않습니다"
→ Docker Desktop 실행 확인

### "Port 7474 is already in use"
```bash
docker-compose down
docker-compose up -d
```

### "Neo4j 연결 실패"
```bash
# 로그 확인
docker-compose logs neo4j

# 재시작
docker-compose restart neo4j
```

## 📚 다음 단계

- [전체 문서 읽기](README.md)
- [Docker 상세 가이드](docs/DOCKER_SETUP.md)
- [MCP Server 설정](docs/MCP_SERVER_SETUP.md)

---

**완료!** 🎉 이제 당신의 Obsidian 노트를 Knowledge Graph로 변환할 수 있습니다!

