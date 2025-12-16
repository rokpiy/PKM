#!/bin/bash

echo "🐳 Neo4j Docker 시작 중..."

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.." || exit 1

# Docker가 실행 중인지 확인
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker가 실행되고 있지 않습니다."
    echo "   Docker Desktop을 시작해주세요."
    exit 1
fi

# 이미 실행 중인지 확인
if docker ps | grep -q neo4j-pkm; then
    echo "✅ Neo4j가 이미 실행 중입니다."
    echo ""
    echo "접속 정보:"
    echo "  🌐 Neo4j Browser: http://localhost:7474"
    echo "  🔌 Bolt: bolt://localhost:7687"
    echo "  👤 Username: neo4j"
    echo "  🔑 Password: .env 파일 참고"
    exit 0
fi

# Neo4j 데이터 폴더 생성
mkdir -p neo4j/data neo4j/logs neo4j/import neo4j/plugins

# Docker Compose로 시작
echo "📦 컨테이너 시작 중..."
docker-compose up -d

# Health check 대기
echo "⏳ Neo4j 초기화 대기 중..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker exec neo4j-pkm cypher-shell -u neo4j -p dlsdud1059^^ "RETURN 1" > /dev/null 2>&1; then
        echo "✅ Neo4j가 준비되었습니다!"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   대기 중... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "⚠️  Neo4j 초기화 시간 초과"
    echo "   docker-compose logs neo4j 명령으로 로그를 확인하세요."
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Neo4j Docker 시작 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 접속 정보:"
echo "  🌐 Neo4j Browser: http://localhost:7474"
echo "  🔌 Bolt: bolt://localhost:7687"
echo "  👤 Username: neo4j"
echo "  🔑 Password: .env 파일의 NEO4J_PASSWORD 참고"
echo ""
echo "📝 유용한 명령어:"
echo "  • 로그 확인: docker-compose logs -f neo4j"
echo "  • 중지: docker-compose down"
echo "  • 재시작: docker-compose restart neo4j"
echo ""
