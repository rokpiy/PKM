# Docker 설정 가이드

PKM 시스템을 Docker로 실행하는 방법에 대한 완전한 가이드입니다.

## 🐳 Docker를 사용하는 이유

### 장점
- ✅ **환경 일관성**: 모든 개발자가 동일한 Neo4j 버전 사용
- ✅ **간편한 설치**: 한 줄 명령으로 시작
- ✅ **격리된 환경**: 시스템에 영향 없음
- ✅ **쉬운 백업**: 데이터 폴더만 복사
- ✅ **버전 관리**: `docker-compose.yml`로 버전 고정
- ✅ **배포 용이**: 로컬 → 클라우드 쉽게 이동

## 📦 사전 준비

### 1. Docker Desktop 설치

**macOS:**
```bash
# Homebrew로 설치
brew install --cask docker

# 또는 공식 웹사이트에서 다운로드
# https://www.docker.com/products/docker-desktop
```

**Windows:**
- [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) 다운로드 및 설치

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
```

### 2. Docker 설치 확인

```bash
docker --version
docker-compose --version
```

예상 출력:
```
Docker version 24.0.0, build xyz
Docker Compose version v2.20.0
```

## 🚀 Neo4j 시작하기

### 방법 1: 헬퍼 스크립트 사용 (권장)

```bash
# Neo4j 시작
./scripts/start_neo4j.sh

# Neo4j 중지
./scripts/stop_neo4j.sh
```

### 방법 2: Docker Compose 직접 사용

```bash
# 시작 (백그라운드)
docker-compose up -d

# 로그 확인
docker-compose logs -f neo4j

# 중지
docker-compose down

# 재시작
docker-compose restart neo4j
```

### 방법 3: Docker 명령어 직접 사용

```bash
docker run -d \
  --name neo4j-pkm \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/dlsdud1059^^ \
  -v $(pwd)/neo4j/data:/data \
  -v $(pwd)/neo4j/logs:/logs \
  neo4j:5.14.0
```

## 🔧 docker-compose.yml 구조

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.14.0           # Neo4j 버전
    container_name: neo4j-pkm     # 컨테이너 이름
    ports:
      - "7474:7474"               # HTTP (Browser)
      - "7687:7687"               # Bolt (Python)
    environment:
      - NEO4J_AUTH=neo4j/password # 인증 정보
      - NEO4J_PLUGINS=["apoc"]    # APOC 플러그인
    volumes:
      - ./neo4j/data:/data        # 데이터 영구 저장
      - ./neo4j/logs:/logs        # 로그 저장
    restart: unless-stopped       # 자동 재시작
```

## 📊 Neo4j 접속

### Neo4j Browser (웹 UI)

1. 브라우저에서 http://localhost:7474 접속
2. 로그인:
   - URL: `bolt://localhost:7687` (자동 입력)
   - Username: `neo4j`
   - Password: `.env` 파일의 `NEO4J_PASSWORD` 참고

### Python 연결

```python
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "dlsdud1059^^"))

# 연결 테스트
with driver.session() as session:
    result = session.run("RETURN 'Hello, Neo4j!' AS message")
    print(result.single()["message"])

driver.close()
```

## 🗂️ 데이터 관리

### 데이터 위치

- **데이터베이스**: `./neo4j/data/`
- **로그**: `./neo4j/logs/`
- **Import용**: `./neo4j/import/`
- **플러그인**: `./neo4j/plugins/`

### 백업

```bash
# 데이터 폴더 전체 백업
tar -czf neo4j-backup-$(date +%Y%m%d).tar.gz neo4j/data/

# 복원
tar -xzf neo4j-backup-20231225.tar.gz
```

### 데이터 초기화

```bash
# Neo4j 중지
docker-compose down

# 데이터 삭제
rm -rf neo4j/data/*

# 재시작 (새로운 빈 데이터베이스)
docker-compose up -d
```

## 🔍 문제 해결

### 1. "Cannot connect to Docker daemon"

**문제**: Docker가 실행되고 있지 않음

**해결**:
```bash
# Docker Desktop 시작 확인
# macOS: Docker Desktop 아이콘 클릭
# Linux: 
sudo systemctl start docker
```

### 2. "Port 7474 is already in use"

**문제**: 포트가 이미 사용 중

**해결**:
```bash
# 포트를 사용하는 프로세스 찾기
lsof -i :7474
lsof -i :7687

# 프로세스 종료 후 재시작
docker-compose down
docker-compose up -d
```

### 3. "Neo4j가 시작되지 않음"

**해결**:
```bash
# 로그 확인
docker-compose logs neo4j

# 상태 확인
docker-compose ps

# 컨테이너 재생성
docker-compose down
docker-compose up -d --force-recreate
```

### 4. "Permission denied" 오류

**Linux에서 발생 시:**
```bash
# 데이터 폴더 권한 설정
sudo chown -R $USER:$USER neo4j/
```

### 5. 메모리 부족

**증상**: Neo4j가 느리거나 크래시

**해결**: `docker-compose.yml`에서 메모리 설정 조정
```yaml
environment:
  - NEO4J_server_memory_heap_max__size=4G  # 기본 2G → 4G
```

## 🎯 유용한 명령어

```bash
# 컨테이너 상태 확인
docker ps

# Neo4j 로그 실시간 확인
docker-compose logs -f neo4j

# Neo4j 컨테이너 내부 접속
docker exec -it neo4j-pkm bash

# Cypher Shell 실행
docker exec -it neo4j-pkm cypher-shell -u neo4j -p dlsdud1059^^

# 컨테이너 리소스 사용량 확인
docker stats neo4j-pkm

# 전체 정리 (데이터 유지)
docker-compose down

# 전체 정리 (데이터 삭제)
docker-compose down -v
```

## 📝 고급 설정

### APOC 플러그인 활성화

이미 `docker-compose.yml`에 포함되어 있습니다:
```yaml
environment:
  - NEO4J_PLUGINS=["apoc"]
```

### 메모리 튜닝

```yaml
environment:
  - NEO4J_server_memory_heap_initial__size=512m
  - NEO4J_server_memory_heap_max__size=2G
  - NEO4J_server_memory_pagecache_size=512m
```

### SSL/TLS 설정

프로덕션 환경에서 사용:
```yaml
environment:
  - NEO4J_server_bolt_tls__level=REQUIRED
volumes:
  - ./ssl/cert.pem:/var/lib/neo4j/certificates/bolt/public.crt
  - ./ssl/key.pem:/var/lib/neo4j/certificates/bolt/private.key
```

## 🚀 프로덕션 배포

### AWS ECS/Fargate

1. ECR에 이미지 푸시 (선택)
2. Task Definition 생성
3. EFS 볼륨 마운트 (데이터 영구화)
4. ALB로 로드 밸런싱

### Docker Swarm

```bash
docker stack deploy -c docker-compose.yml pkm
```

### Kubernetes (K8s)

```bash
kubectl apply -f k8s/neo4j-deployment.yaml
```

## 💡 Best Practices

1. **정기 백업**: 매일 `neo4j/data/` 백업
2. **버전 고정**: `docker-compose.yml`에서 정확한 버전 사용 (`neo4j:5.14.0`)
3. **로그 모니터링**: `docker-compose logs -f` 정기 확인
4. **Health Check**: 자동 헬스 체크 활성화
5. **Resource Limits**: CPU/메모리 제한 설정

## 📚 참고 자료

- [Neo4j Docker 공식 문서](https://neo4j.com/docs/operations-manual/current/docker/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [Neo4j APOC 라이브러리](https://neo4j.com/labs/apoc/)

---

문제가 발생하면 `docker-compose logs neo4j` 로그를 확인하거나 GitHub Issues를 통해 문의하세요!
