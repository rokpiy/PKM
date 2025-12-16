"""
Atomic Note Agent
복잡한 문서를 원자적 단위(Atomic Notes)로 분해하는 AI Agent
Google Gemini API 사용 (신형 SDK)
"""

from google import genai
from google.genai import types
import json
import os
import time
import re
from typing import List, Dict
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# src 폴더 내 import
try:
    from obsidian_loader import ObsidianNote, ObsidianVaultLoader
except ImportError:
    from src.obsidian_loader import ObsidianNote, ObsidianVaultLoader

# .env 파일 로드 (프로젝트 루트, 환경변수 덮어쓰기)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)


class AtomicNoteAgent:
    """Gemini를 사용하여 문서를 Atomic Notes로 분해하는 Agent"""
    
    SYSTEM_PROMPT = """당신은 복잡한 문서를 원자적 단위의 노트로 분해하는 전문가입니다.

역할:
1. 입력 문서를 논리적 단위로 분리
2. 각 단위에서 핵심 개념 추출
3. 구조화된 Atomic Note 생성

Atomic Note 원칙:
- 단 하나의 개념/아이디어만 포함
- 독립적으로 이해 가능한 단위
- 다른 노트와 연결 가능한 형태
- 명확한 메타데이터 포함

출력 형식 (JSON):
{
  "atomic_notes": [
    {
      "id": "note_YYYYMMDD_001",
      "title": "핵심 개념",
      "content": "1-2문장 핵심 설명",
      "detailed_content": "상세 내용",
      "extracted_entities": ["entity1", "entity2"],
      "relationships": [
        {"from": "entity1", "type": "relates_to", "to": "entity2"},
        {"from": "entity2", "type": "is_example_of", "to": "concept"}
      ],
      "domain": "domain_name",
      "related_notes": [],
      "confidence": "high|medium|low"
    }
  ],
  "hierarchy": {
    "parent_concept": ["child_concept1", "child_concept2"]
  },
  "summary": "전체 문서 요약"
}

관계 타입:
- "relates_to": 관련됨
- "is_example_of": ~의 예시
- "causes": ~를 야기함
- "supports": ~를 지지함
- "contradicts": ~와 모순됨
- "implements": ~를 구현함
- "derived_from": ~에서 파생됨

반드시 유효한 JSON 형식으로만 응답해주세요."""

    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        """
        Args:
            api_key: Google Gemini API 키 (없으면 환경변수에서 가져옴)
            model: 사용할 Gemini 모델
                - gemini-2.5-flash: 빠른 2.5 모델 (기본값, 무료)
                - gemini-2.5-pro: 가장 강력한 2.5 모델 (유료)
                - gemini-1.5-pro: 이전 Pro 모델
                - gemini-1.5-flash: 이전 Flash 모델
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 필요합니다. 환경변수에 설정하거나 직접 전달하세요.")
        
        # Gemini 클라이언트 생성 (신형 SDK)
        self.client = genai.Client(api_key=self.api_key)
        
        # Gemini 2.5 모델은 최대 65536 토큰 지원
        max_tokens = 65536 if "2.5" in model else 8192
        
        # Generation Config
        self.generation_config = types.GenerateContentConfig(
            temperature=0.2,  # 더 일관된 출력
            top_p=0.95,
            top_k=64,  # 더 넓은 선택지
            max_output_tokens=max_tokens,
            response_mime_type="application/json",  # JSON 응답 강제
        )
        self.model_name = model
    
    def decompose_note(self, note: ObsidianNote) -> Dict:
        """
        단일 노트를 Atomic Notes로 분해
        
        Args:
            note: ObsidianNote 객체
            
        Returns:
            분해된 Atomic Notes (JSON 형식)
        """
        print(f"🔍 분석 중: {note.title}")
        
        # User prompt 구성
        user_prompt = f"""{self.SYSTEM_PROMPT}

---

다음 문서를 원자적 단위로 분해해주세요:

# 문서 제목: {note.title}

## 메타데이터:
- 태그: {note.tags}
- 링크: {note.links}
- Frontmatter: {note.frontmatter}

## 본문:
{note.content}

---

위 문서를 분석하여 Atomic Notes로 분해하고, 반드시 유효한 JSON 형식으로만 출력해주세요.
각 Atomic Note는 독립적으로 이해 가능해야 하며, 핵심 개념만 포함해야 합니다.
JSON만 출력하고 다른 설명은 포함하지 마세요."""

        max_retries = 3
        retry_delay = 10  # 초
        
        for attempt in range(max_retries):
            try:
                # Gemini API 호출 (신형 SDK)
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=self.generation_config
                )
                response_text = response.text.strip()
                
                # JSON 추출 (코드 블록이 있는 경우 제거)
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    if json_end > json_start:
                        response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    if json_end > json_start:
                        response_text = response_text[json_start:json_end].strip()
                
                # JSON 파싱
                result = json.loads(response_text)
                
                # 원본 노트 정보 추가
                result["source_note"] = {
                    "title": note.title,
                    "file_path": note.file_path,
                    "created_date": note.created_date.isoformat() if note.created_date else None
                }
                
                print(f"✅ 완료: {len(result.get('atomic_notes', []))}개의 Atomic Notes 생성")
                
                return result
                
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  JSON 파싱 실패 ({e}). 재시도 중... (시도 {attempt + 1}/{max_retries})")
                    print(f"   응답 길이: {len(response_text)} 글자")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"❌ JSON 파싱 최종 실패: {e}")
                    print(f"응답 (처음 1000자): {response_text[:1000]}")
                return {
                        "error": "JSON parsing failed after retries",
                        "raw_response": response_text[:1000],
                    "atomic_notes": []
                }
            except Exception as e:
                error_msg = str(e)
                
                # Rate Limit 에러 확인
                if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        print(f"⚠️  Rate Limit 도달. {wait_time}초 후 재시도... (시도 {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ Rate Limit 초과: 최대 재시도 횟수 도달")
                
                print(f"❌ 처리 실패: {e}")
                return {
                    "error": str(e),
                    "atomic_notes": []
                }
    
    def decompose_vault(self, vault_path: str, output_dir: str = "./atomic_notes", skip_existing: bool = True) -> List[Dict]:
        """
        Obsidian Vault 전체를 Atomic Notes로 분해
        
        Args:
            vault_path: Obsidian vault 경로
            output_dir: 출력 디렉토리
            skip_existing: True면 이미 존재하는 JSON 파일 스킵
            
        Returns:
            모든 Atomic Notes 리스트
        """
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # Vault 로드
        loader = ObsidianVaultLoader(vault_path)
        notes = loader.load_vault()
        
        all_atomic_notes = []
        skipped_count = 0
        processed_count = 0
        
        print(f"\n🚀 Vault 분해 시작: {len(notes)}개 노트")
        print("=" * 60)
        
        for i, note in enumerate(notes, 1):
            print(f"\n[{i}/{len(notes)}] {note.title}")
            
            # 빈 노트 스킵
            if len(note.content.strip()) < 50:
                print("⏭️  너무 짧은 노트 - 스킵")
                continue
            
            # JSON 파일 경로 (안전한 파일명)
            safe_title = note.title.replace(' ', '_').replace('/', '_').replace('\\', '_')
            output_file = os.path.join(output_dir, f"{safe_title}_atomic.json")
            
            # 이미 존재하는 파일 확인
            if skip_existing and os.path.exists(output_file):
                print("♻️  이미 처리됨 - JSON 로드 중...")
                with open(output_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                all_atomic_notes.append(result)
                skipped_count += 1
                print(f"✅ 로드 완료: {len(result.get('atomic_notes', []))}개 Atomic Notes")
            else:
            # Atomic Notes로 분해
                print("🔍 분석 중...")
            result = self.decompose_note(note)
            
            # 결과 저장
            if result.get("atomic_notes"):
                all_atomic_notes.append(result)
                
                # JSON 파일로 저장
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                    processed_count += 1
                print(f"💾 저장: {output_file}")
            
            # Rate Limit 방지를 위한 대기 (마지막 노트는 제외)
            if i < len(notes):
                print("⏳ 다음 노트 처리를 위해 2초 대기 중...")
                time.sleep(2)
        
        print("\n" + "=" * 60)
        print(f"✅ 전체 완료: {len(all_atomic_notes)}개 파일")
        print(f"   - 새로 처리: {processed_count}개")
        print(f"   - 기존 로드: {skipped_count}개")
        print(f"📂 출력 디렉토리: {output_dir}")
        
        # 전체 통계
        total_atomic_notes = sum(
            len(result.get("atomic_notes", [])) 
            for result in all_atomic_notes
        )
        print(f"📊 총 Atomic Notes: {total_atomic_notes}개")
        
        return all_atomic_notes
    
    def save_as_markdown(self, atomic_notes_result: Dict, output_dir: str = "./atomic_notes_md"):
        """
        Atomic Notes를 마크다운 형식으로 저장
        
        Args:
            atomic_notes_result: decompose_note의 결과
            output_dir: 출력 디렉토리
        """
        os.makedirs(output_dir, exist_ok=True)
        
        source_title = atomic_notes_result.get("source_note", {}).get("title", "Unknown")
        
        for atomic_note in atomic_notes_result.get("atomic_notes", []):
            # 파일명 생성 (특수문자 제거)
            safe_title = atomic_note['title'].replace(' ', '_')
            # 파일시스템에서 허용되지 않는 문자 제거
            safe_title = re.sub(r'[<>:"/\\|?*]', '', safe_title)
            # 연속된 언더스코어 제거
            safe_title = re.sub(r'_+', '_', safe_title)
            
            filename = f"{atomic_note['id']}_{safe_title}.md"
            filepath = os.path.join(output_dir, filename)
            
            # 마크다운 생성
            markdown = f"""---
type: atomic_note
source: {source_title}
id: {atomic_note['id']}
domain: {atomic_note.get('domain', 'general')}
confidence: {atomic_note.get('confidence', 'medium')}
entities: {json.dumps(atomic_note.get('extracted_entities', []), ensure_ascii=False)}
created_date: {datetime.now().strftime('%Y-%m-%d')}
---

# {atomic_note['title']}

## 핵심 개념
{atomic_note['content']}

## 상세 내용
{atomic_note.get('detailed_content', '')}

## 추출된 엔티티
{', '.join(f'`{e}`' for e in atomic_note.get('extracted_entities', []))}

## 관계
"""
            
            # 관계 추가
            for rel in atomic_note.get('relationships', []):
                markdown += f"- `{rel['from']}` --[{rel['type']}]--> `{rel['to']}`\n"
            
            # 관련 노트
            if atomic_note.get('related_notes'):
                markdown += "\n## 관련 노트\n"
                for related in atomic_note['related_notes']:
                    markdown += f"- [[{related}]]\n"
            
            # 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"📝 생성: {filename}")


# CLI 인터페이스
if __name__ == "__main__":
    import sys
    
    # API 키 확인 (.env 파일은 이미 상단에서 로드됨)
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        print("\n다음 중 하나를 선택하세요:")
        print("1. .env 파일에 GEMINI_API_KEY=your-api-key 추가")
        print("2. 환경변수로 설정: export GEMINI_API_KEY='your-api-key'")
        print("\nAPI 키는 https://makersuite.google.com/app/apikey 에서 발급받을 수 있습니다.")
        sys.exit(1)
    
    # Agent 초기화
    agent = AtomicNoteAgent()
    
    # Vault 경로 설정
    VAULT_PATH = "/Users/inyoungpark/Documents/Obsidian Vault"
    
    print("🤖 Atomic Note Agent (Gemini 2.0 Flash)")
    print("=" * 60)
    print(f"📂 Vault: {VAULT_PATH}")
    print(f"🔧 Model: {agent.model_name}")
    print(f"⚡ 특징: 최신 모델 - 빠른 속도 + 높은 품질")
    print("=" * 60)
    
    # 전체 Vault 분해
    results = agent.decompose_vault(VAULT_PATH)
    
    # 마크다운으로도 저장
    print("\n📝 마크다운 형식으로 저장 중...")
    for result in results:
        agent.save_as_markdown(result)
    
    print("\n✅ 모든 작업 완료!")
