#!/bin/bash

echo "🛑 Neo4j Docker 중지 중..."

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.." || exit 1

# Neo4j가 실행 중인지 확인
if ! docker ps | grep -q neo4j-pkm; then
    echo "ℹ️  Neo4j가 실행되고 있지 않습니다."
    exit 0
fi

# Docker Compose로 중지
docker-compose down

echo "✅ Neo4j Docker 중지 완료!"
echo ""
echo "💡 팁:"
echo "  • 재시작: ./scripts/start_neo4j.sh"
echo "  • 데이터 유지됨: ./neo4j/data/"
echo ""

