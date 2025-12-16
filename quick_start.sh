#!/bin/bash

# Quick Start Script for PKM System (Obsidian → Graph DB)

echo "🤖 PKM System - Quick Start"
echo "=========================================="
echo ""

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 없습니다. 다음 명령어를 실행하세요:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# 가상환경 활성화
source venv/bin/activate

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다."
    echo ""
    echo ".env 파일을 생성하세요:"
    echo "   echo 'GEMINI_API_KEY=your-api-key-here' > .env"
    echo ""
    echo "또는 환경변수로 설정:"
    echo "   export GEMINI_API_KEY='your-api-key-here'"
    echo ""
    echo "API 키는 https://makersuite.google.com/app/apikey 에서 발급받을 수 있습니다."
    exit 1
fi

echo "✅ .env 파일 발견됨"
echo "✅ 환경 설정 완료"
echo ""

# 메뉴 표시
echo "📋 PKM System Stages:"
echo "=========================================="
echo "1. Stage 1: Atomic Notes 생성"
echo "2. Stage 2: Entity & Relationship 추출"
echo "3. Stage 3: Neo4j Graph DB Import"
echo "4. Stage 4: Knowledge Graph Reasoning"
echo "5. 전체 파이프라인 실행 (Stage 1 + 2 + 3)"
echo "6. 종료"
echo ""

read -p "선택 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Stage 1: Atomic Notes 생성"
        echo "=========================================="
        python tests/test_atomic_agent.py
        ;;
    2)
        echo ""
        echo "🚀 Stage 2: Entity & Relationship 추출"
        echo "=========================================="
        if [ ! -d "atomic_notes" ] || [ -z "$(ls -A atomic_notes 2>/dev/null)" ]; then
            echo "❌ atomic_notes 폴더가 비어있습니다."
            echo "   먼저 Stage 1을 실행하세요."
            exit 1
        fi
        python tests/test_entity_extraction.py
        ;;
    3)
        echo ""
        echo "🚀 Stage 3: Neo4j Graph DB Import"
        echo "=========================================="
        if [ ! -d "atomic_notes" ] || [ -z "$(ls -A atomic_notes 2>/dev/null)" ]; then
            echo "❌ atomic_notes 폴더가 비어있습니다."
            echo "   먼저 Stage 1과 2를 실행하세요."
            exit 1
        fi
        python tests/test_graph_import.py
        ;;
    4)
        echo ""
        echo "🚀 Stage 4: Knowledge Graph Reasoning"
        echo "=========================================="
        python tests/test_kg_reasoning.py
        ;;
    5)
        echo ""
        echo "🚀 전체 파이프라인 실행"
        echo "=========================================="
        echo ""
        echo "📍 Stage 1: Atomic Notes 생성"
        echo "----------------------------------------"
        python tests/test_atomic_agent.py
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "📍 Stage 2: Entity & Relationship 추출"
            echo "----------------------------------------"
            python tests/test_entity_extraction.py
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "📍 Stage 3: Neo4j Graph DB Import"
                echo "----------------------------------------"
                python tests/test_graph_import.py
                
                if [ $? -eq 0 ]; then
                    echo ""
                    echo "✅ Stage 1-3 완료!"
                    echo ""
                    echo "💡 Stage 4 (Knowledge Graph Reasoning)는 대화형 모드로 별도 실행하세요:"
                    echo "   python tests/test_kg_reasoning.py"
                fi
            fi
        fi
        ;;
    6)
        echo "종료"
        exit 0
        ;;
    *)
        echo "잘못된 선택입니다."
        exit 1
        ;;
esac
