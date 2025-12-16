"""
Neo4j Graph Database Manager
Atomic Notes와 Entity를 Knowledge Graph로 변환
"""

from neo4j import GraphDatabase
from typing import Dict, List, Optional
import json
import uuid
from datetime import datetime


class GraphDBManager:
    """Neo4j Graph Database 관리 클래스"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", 
                 auth: tuple = ("neo4j", "password")):
        """
        Args:
            uri: Neo4j 서버 주소
            auth: (username, password) 튜플
        """
        try:
            self.driver = GraphDatabase.driver(uri, auth=auth)
            # 연결 테스트
            self.driver.verify_connectivity()
            print(f"✅ Neo4j 연결 성공: {uri}")
        except Exception as e:
            print(f"❌ Neo4j 연결 실패: {e}")
            print("   Neo4j가 실행 중인지 확인하세요:")
            print("   docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")
            raise
    
    def close(self):
        """연결 종료"""
        if self.driver:
            self.driver.close()
            print("✅ Neo4j 연결 종료")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def create_schema(self):
        """Graph DB 스키마 생성 (인덱스 및 제약조건)"""
        print("🔧 스키마 생성 중...")
        
        with self.driver.session() as session:
            # Neo4j 5.x 구문 (FOR ... REQUIRE)
            constraints = [
                # Entity 노드 유니크 제약조건
                "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
                # AtomicNote 노드 유니크 제약조건
                "CREATE CONSTRAINT note_id_unique IF NOT EXISTS FOR (n:AtomicNote) REQUIRE n.id IS UNIQUE",
            ]
            
            indexes = [
                # Entity 이름 인덱스 (검색 최적화)
                "CREATE INDEX entity_name_idx IF NOT EXISTS FOR (e:Entity) ON (e.name)",
                # AtomicNote 제목 인덱스
                "CREATE INDEX note_title_idx IF NOT EXISTS FOR (n:AtomicNote) ON (n.title)",
                # 도메인 인덱스
                "CREATE INDEX entity_domain_idx IF NOT EXISTS FOR (e:Entity) ON (e.domain)",
            ]
            
            # 제약조건 생성
            for query in constraints:
                try:
                    session.run(query)
                except Exception as e:
                    error_msg = str(e).lower()
                    # 이미 존재하거나, 구문이 지원되지 않는 경우 무시
                    if "already exists" not in error_msg and "equivalent" not in error_msg:
                        print(f"⚠️  제약조건 생성 스킵: {e}")
            
            # 인덱스 생성
            for query in indexes:
                try:
                    session.run(query)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "already exists" not in error_msg and "equivalent" not in error_msg:
                        print(f"⚠️  인덱스 생성 스킵: {e}")
        
        print("✅ 스키마 생성 완료")
    
    def clear_all(self):
        """모든 노드와 관계 삭제 (주의!)"""
        print("⚠️  모든 데이터 삭제 중...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✅ 데이터 삭제 완료")
    
    def create_atomic_note_node(self, note_data: Dict) -> str:
        """
        Atomic Note 노드 생성
        
        Args:
            note_data: Atomic Note 데이터
            
        Returns:
            생성된 노드 ID
        """
        with self.driver.session() as session:
            note_id = note_data.get("id", str(uuid.uuid4()))
            
            # 먼저 존재하는지 확인
            check_query = "MATCH (n:AtomicNote {id: $id}) RETURN n.id as id"
            existing = session.run(check_query, id=note_id).single()
            
            if existing:
                # 기존 노트 업데이트
                update_query = """
                MATCH (n:AtomicNote {id: $id})
                SET n.title = $title,
                    n.content = $content,
                    n.detailed_content = $detailed_content,
                    n.domain = $domain,
                    n.confidence = $confidence,
                    n.source_note = $source_note,
                    n.updated_at = timestamp()
                RETURN n.id as id
                """
                result = session.run(
                    update_query,
                    id=note_id,
                    title=note_data.get("title", ""),
                    content=note_data.get("content", ""),
                    detailed_content=note_data.get("detailed_content", ""),
                    domain=note_data.get("domain", "general"),
                    confidence=note_data.get("confidence", "medium"),
                    source_note=note_data.get("source_note", "")
                )
            else:
                # 새 노트 생성
                create_query = """
                CREATE (n:AtomicNote {
                    id: $id,
                    title: $title,
                    content: $content,
                    detailed_content: $detailed_content,
                    domain: $domain,
                    confidence: $confidence,
                    source_note: $source_note,
                    created_at: timestamp(),
                    updated_at: timestamp()
                })
                RETURN n.id as id
                """
                result = session.run(
                    create_query,
                    id=note_id,
                    title=note_data.get("title", ""),
                    content=note_data.get("content", ""),
                    detailed_content=note_data.get("detailed_content", ""),
                    domain=note_data.get("domain", "general"),
                    confidence=note_data.get("confidence", "medium"),
                    source_note=note_data.get("source_note", "")
                )
            
            return result.single()["id"]
    
    def create_entity_node(self, entity: str, entity_data: Optional[Dict] = None) -> str:
        """
        Entity 노드 생성 또는 업데이트
        
        Args:
            entity: 엔티티 이름
            entity_data: 추가 메타데이터
            
        Returns:
            생성된 노드 ID
        """
        if entity_data is None:
            entity_data = {}
        
        with self.driver.session() as session:
            # Python에서 UUID 생성 (Neo4j 구버전 호환)
            entity_id = str(uuid.uuid4())
            
            # 먼저 존재하는지 확인
            check_query = "MATCH (e:Entity {name: $name}) RETURN e.id as id"
            existing = session.run(check_query, name=entity).single()
            
            if existing:
                # 기존 엔티티 업데이트
                update_query = """
                MATCH (e:Entity {name: $name})
                SET e.label = $label,
                    e.domain = $domain,
                    e.confidence = $confidence,
                    e.updated_at = timestamp()
                RETURN e.id as id
                """
                result = session.run(
                    update_query,
                    name=entity,
                    label=entity_data.get("label", "CONCEPT"),
                    domain=entity_data.get("domain", "general"),
                    confidence=entity_data.get("confidence", 1.0)
                )
                return result.single()["id"]
            else:
                # 새 엔티티 생성
                create_query = """
                CREATE (e:Entity {
                    id: $id,
                    name: $name,
                    label: $label,
                    domain: $domain,
                    confidence: $confidence,
                    created_at: timestamp(),
                    updated_at: timestamp()
                })
                RETURN e.id as id
                """
                result = session.run(
                    create_query,
                    id=entity_id,
                    name=entity,
                    label=entity_data.get("label", "CONCEPT"),
                    domain=entity_data.get("domain", "general"),
                    confidence=entity_data.get("confidence", 1.0)
                )
                return result.single()["id"]
    
    def create_relationship(self, from_entity: str, rel_type: str, 
                          to_entity: str, confidence: float = 0.7,
                          metadata: Optional[Dict] = None):
        """
        엔티티 간 관계 생성
        
        Args:
            from_entity: 시작 엔티티 이름
            rel_type: 관계 타입 (relates_to, is_example_of, 등)
            to_entity: 목표 엔티티 이름
            confidence: 신뢰도
            metadata: 추가 메타데이터
        """
        if metadata is None:
            metadata = {}
        
        # 관계 타입을 대문자로 변환 (Neo4j 관례)
        rel_type_upper = rel_type.upper().replace(" ", "_")
        
        with self.driver.session() as session:
            # 먼저 관계가 존재하는지 확인
            check_query = f"""
            MATCH (from:Entity {{name: $from_entity}})-[r:{rel_type_upper}]->(to:Entity {{name: $to_entity}})
            RETURN r
            """
            existing = session.run(check_query, from_entity=from_entity, to_entity=to_entity).single()
            
            if existing:
                # 기존 관계 업데이트
                update_query = f"""
                MATCH (from:Entity {{name: $from_entity}})-[r:{rel_type_upper}]->(to:Entity {{name: $to_entity}})
                SET r.confidence = $confidence,
                    r.method = $method,
                    r.updated_at = timestamp()
                RETURN r
                """
                session.run(
                    update_query,
                    from_entity=from_entity,
                    to_entity=to_entity,
                    confidence=confidence,
                    method=metadata.get("method", "extracted")
                )
            else:
                # 새 관계 생성
                create_query = f"""
                MATCH (from:Entity {{name: $from_entity}})
                MATCH (to:Entity {{name: $to_entity}})
                CREATE (from)-[r:{rel_type_upper} {{
                    confidence: $confidence,
                    method: $method,
                    created_at: timestamp(),
                    updated_at: timestamp()
                }}]->(to)
                RETURN r
                """
                session.run(
                    create_query,
                    from_entity=from_entity,
                    to_entity=to_entity,
                    confidence=confidence,
                    method=metadata.get("method", "extracted")
                )
    
    def link_note_to_entity(self, note_id: str, entity: str):
        """Atomic Note와 Entity를 연결"""
        with self.driver.session() as session:
            # 먼저 관계가 존재하는지 확인
            check_query = """
            MATCH (n:AtomicNote {id: $note_id})-[r:MENTIONS]->(e:Entity {name: $entity})
            RETURN r
            """
            existing = session.run(check_query, note_id=note_id, entity=entity).single()
            
            if not existing:
                # 관계가 없으면 생성
                create_query = """
                MATCH (n:AtomicNote {id: $note_id})
                MATCH (e:Entity {name: $entity})
                CREATE (n)-[r:MENTIONS {created_at: timestamp()}]->(e)
                RETURN r
                """
                session.run(create_query, note_id=note_id, entity=entity)
    
    def get_entity_graph(self, entity: str, depth: int = 2) -> Dict:
        """
        특정 엔티티 주변의 그래프 가져오기
        
        Args:
            entity: 엔티티 이름
            depth: 탐색 깊이
            
        Returns:
            노드와 관계 정보
        """
        with self.driver.session() as session:
            query = f"""
            MATCH path = (e:Entity {{name: $entity}})-[*1..{depth}]-(related)
            RETURN e, related, relationships(path) as rels
            LIMIT 100
            """
            
            result = session.run(query, entity=entity)
            
            nodes = []
            relationships = []
            
            for record in result:
                # 노드 정보 추출
                if record["e"]:
                    nodes.append(dict(record["e"]))
                if record["related"]:
                    nodes.append(dict(record["related"]))
                
                # 관계 정보 추출
                if record["rels"]:
                    for rel in record["rels"]:
                        relationships.append({
                            "type": rel.type,
                            "properties": dict(rel)
                        })
            
            return {
                "nodes": nodes,
                "relationships": relationships
            }
    
    def search_entities(self, query: str, limit: int = 10) -> List[Dict]:
        """엔티티 검색"""
        with self.driver.session() as session:
            cypher_query = """
            MATCH (e:Entity)
            WHERE e.name CONTAINS $query
            RETURN e
            ORDER BY e.name
            LIMIT $limit
            """
            
            result = session.run(cypher_query, query=query, limit=limit)
            return [dict(record["e"]) for record in result]
    
    def get_statistics(self) -> Dict:
        """Graph DB 통계"""
        with self.driver.session() as session:
            stats_query = """
            MATCH (n)
            WITH labels(n) as labels
            UNWIND labels as label
            RETURN label, count(*) as count
            ORDER BY count DESC
            """
            
            result = session.run(stats_query)
            node_counts = {record["label"]: record["count"] for record in result}
            
            # 관계 통계
            rel_query = """
            MATCH ()-[r]->()
            RETURN type(r) as type, count(*) as count
            ORDER BY count DESC
            """
            
            result = session.run(rel_query)
            rel_counts = {record["type"]: record["count"] for record in result}
            
            return {
                "nodes": node_counts,
                "relationships": rel_counts,
                "total_nodes": sum(node_counts.values()),
                "total_relationships": sum(rel_counts.values())
            }


# CLI 인터페이스
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # 환경변수에서 Neo4j 설정 가져오기
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    
    print("🔧 Neo4j Graph DB Manager 테스트")
    print("=" * 60)
    
    try:
        with GraphDBManager(NEO4J_URI, (NEO4J_USER, NEO4J_PASSWORD)) as graph:
            # 스키마 생성
            graph.create_schema()
            
            # 테스트 데이터 생성
            print("\n📝 테스트 데이터 생성...")
            
            # Entity 생성
            graph.create_entity_node("AI", {"label": "CONCEPT", "domain": "technology"})
            graph.create_entity_node("머신러닝", {"label": "CONCEPT", "domain": "technology"})
            graph.create_entity_node("딥러닝", {"label": "CONCEPT", "domain": "technology"})
            
            # 관계 생성
            graph.create_relationship("딥러닝", "is_example_of", "머신러닝", 0.9)
            graph.create_relationship("머신러닝", "is_example_of", "AI", 0.9)
            
            # 통계 출력
            print("\n📊 Graph DB 통계:")
            stats = graph.get_statistics()
            print(f"  총 노드: {stats['total_nodes']}개")
            print(f"  총 관계: {stats['total_relationships']}개")
            print(f"  노드 타입: {stats['nodes']}")
            print(f"  관계 타입: {stats['relationships']}")
            
            print("\n✅ 테스트 완료!")
    
    except Exception as e:
        print(f"\n❌ 에러: {e}")
        print("\nNeo4j 서버가 실행 중인지 확인하세요:")
        print("docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest")

