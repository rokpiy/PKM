#!/usr/bin/env python3
"""
PKM Knowledge Graph MCP Server (FastMCP)

MCP 철학에 맞게 간소화: Raw Data만 제공, Reasoning은 LLM이 담당
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any

# src 폴더를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
from fastmcp import FastMCP

# PKM 시스템 import (GraphDBManager만 사용)
from graph_db import GraphDBManager

# .env 파일 로드
load_dotenv()

# Neo4j 설정
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# 전역 인스턴스 (lazy initialization)
_graph_db = None


def get_graph_db() -> GraphDBManager:
    """GraphDB 인스턴스를 가져오거나 생성"""
    global _graph_db
    if _graph_db is None:
        _graph_db = GraphDBManager(NEO4J_URI, (NEO4J_USER, NEO4J_PASSWORD))
    return _graph_db


# FastMCP 서버 생성
mcp = FastMCP("PKM Knowledge Graph")


@mcp.tool()
def search_entities(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Knowledge Graph에서 개념(Entity)을 검색합니다.
    
    Args:
        query: 검색할 개념 이름
        limit: 반환할 최대 결과 수 (기본값: 10)
    
    Returns:
        검색된 개념 목록 (raw data)
    """
    db = get_graph_db()
    entities = db.search_entities(query, limit=limit)
    
    return {
        "query": query,
        "count": len(entities),
        "entities": entities
    }


@mcp.tool()
def get_entity_graph(entity_name: str, depth: int = 2) -> Dict[str, Any]:
    """
    특정 개념(Entity) 주변의 그래프를 가져옵니다.
    
    Args:
        entity_name: 조회할 개념의 이름
        depth: 탐색할 이웃 노드의 깊이 (기본값: 2)
    
    Returns:
        노드와 관계 정보 (raw data)
    """
    db = get_graph_db()
    graph = db.get_entity_graph(entity_name, depth=depth)
    
    return {
        "entity": entity_name,
        "depth": depth,
        "nodes": graph.get("nodes", []),
        "relationships": graph.get("relationships", [])
    }


@mcp.tool()
def find_related_notes(entity_name: str, limit: int = 5) -> Dict[str, Any]:
    """
    특정 개념과 관련된 Atomic Notes를 찾습니다.
    
    Args:
        entity_name: 검색할 개념의 이름
        limit: 반환할 최대 노트 수 (기본값: 5)
    
    Returns:
        관련된 노트 목록 (raw data)
    """
    db = get_graph_db()
    
    # Cypher 쿼리로 관련 노트 찾기
    with db.driver.session() as session:
        query = """
        MATCH (n:AtomicNote)-[:MENTIONS]->(e:Entity {name: $entity_name})
        RETURN n.id as id, n.title as title, n.content as content, 
               n.domain as domain, n.confidence as confidence
        ORDER BY n.created_at DESC
        LIMIT $limit
        """
        
        result = session.run(query, entity_name=entity_name, limit=limit)
        notes = [dict(record) for record in result]
    
    return {
        "entity": entity_name,
        "count": len(notes),
        "notes": notes
    }


@mcp.tool()
def find_entity_path(start_entity: str, end_entity: str, max_depth: int = 5) -> Dict[str, Any]:
    """
    두 개념 사이의 연결 경로를 찾습니다.
    
    Args:
        start_entity: 시작 개념
        end_entity: 끝 개념
        max_depth: 최대 탐색 깊이 (기본값: 5)
    
    Returns:
        두 개념을 연결하는 경로들 (raw data)
    """
    db = get_graph_db()
    
    # Cypher 쿼리로 최단 경로 찾기
    with db.driver.session() as session:
        query = f"""
        MATCH path = shortestPath(
            (start:Entity {{name: $start_entity}})-[*1..{max_depth}]-(end:Entity {{name: $end_entity}})
        )
        WITH path, [node in nodes(path) | node.name] as entity_names,
             [rel in relationships(path) | type(rel)] as rel_types,
             length(path) as path_length
        RETURN entity_names, rel_types, path_length
        ORDER BY path_length
        LIMIT 5
        """
        
        result = session.run(query, start_entity=start_entity, end_entity=end_entity)
        paths = []
        
        for record in result:
            paths.append({
                "entities": record["entity_names"],
                "relationships": record["rel_types"],
                "length": record["path_length"]
            })
    
    return {
        "start": start_entity,
        "end": end_entity,
        "count": len(paths),
        "paths": paths
    }


@mcp.tool()
def get_graph_stats() -> Dict[str, Any]:
    """
    Knowledge Graph의 전체 통계를 가져옵니다.
    
    Returns:
        노드 수, 관계 수, 도메인 분포 등 통계 정보 (raw data)
    """
    db = get_graph_db()
    stats = db.get_graph_stats()
    
    return {
        "total_nodes": stats.get("total_nodes", 0),
        "total_relationships": stats.get("total_relationships", 0),
        "nodes_by_label": stats.get("nodes", {}),
        "relationships_by_type": stats.get("relationships", {})
    }


@mcp.tool()
def run_cypher_query(query: str, limit: int = 100) -> Dict[str, Any]:
    """
    사용자 정의 Cypher 쿼리를 실행합니다.
    
    Args:
        query: 실행할 Cypher 쿼리
        limit: 반환할 최대 결과 수 (기본값: 100)
    
    Returns:
        쿼리 실행 결과 (raw data)
    
    주의: 읽기 전용 쿼리만 허용됩니다 (MATCH, RETURN 등).
    """
    db = get_graph_db()
    
    # 보안: 쓰기 쿼리 차단
    query_upper = query.upper().strip()
    write_keywords = ["CREATE", "DELETE", "REMOVE", "SET", "MERGE", "DROP"]
    
    for keyword in write_keywords:
        if keyword in query_upper:
            return {
                "error": f"쓰기 작업은 허용되지 않습니다: {keyword}",
                "query": query
            }
    
    try:
        with db.driver.session() as session:
            result = session.run(query)
            records = []
            
            for record in result:
                # Record를 딕셔너리로 변환
                record_dict = {}
                for key in record.keys():
                    value = record[key]
                    # Neo4j Node를 딕셔너리로 변환
                    if hasattr(value, '__dict__'):
                        record_dict[key] = dict(value)
                    else:
                        record_dict[key] = value
                records.append(record_dict)
                
                # limit 적용
                if len(records) >= limit:
                    break
            
            return {
                "query": query,
                "count": len(records),
                "records": records
            }
    
    except Exception as e:
        return {
            "error": str(e),
            "query": query
        }


if __name__ == "__main__":
    print("🚀 PKM Knowledge Graph MCP Server (FastMCP) 시작...", file=sys.stderr)
    print(f"   Neo4j: {NEO4J_URI}", file=sys.stderr)
    print("   철학: Raw Data만 제공, Reasoning은 LLM이 담당", file=sys.stderr)
    print("   준비 완료! MCP 클라이언트 연결을 기다리는 중...", file=sys.stderr)
    
    # FastMCP 서버 실행
    mcp.run()
