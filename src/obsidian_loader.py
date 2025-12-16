"""
Obsidian Vault Loader
Obsidian vault에서 마크다운 파일을 로드하고 파싱하는 모듈
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import yaml


@dataclass
class ObsidianNote:
    """Obsidian 노트를 표현하는 데이터 클래스"""
    
    file_path: str
    title: str
    content: str
    frontmatter: Dict = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    
    def __repr__(self):
        return f"ObsidianNote(title='{self.title}', links={len(self.links)}, tags={len(self.tags)})"


class ObsidianVaultLoader:
    """Obsidian Vault에서 노트를 로드하는 클래스"""
    
    def __init__(self, vault_path: str):
        """
        Args:
            vault_path: Obsidian vault의 경로
        """
        self.vault_path = Path(vault_path).expanduser()
        
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")
    
    def load_vault(self, include_hidden: bool = False) -> List[ObsidianNote]:
        """
        Vault의 모든 마크다운 파일을 로드
        
        Args:
            include_hidden: 숨김 파일/폴더 포함 여부 (기본값: False)
            
        Returns:
            ObsidianNote 리스트
        """
        notes = []
        
        for md_file in self.vault_path.glob("**/*.md"):
            # 숨김 파일/폴더 제외
            if not include_hidden:
                if any(part.startswith('.') for part in md_file.parts):
                    continue
            
            try:
                note = self.load_note(md_file)
                notes.append(note)
            except Exception as e:
                print(f"⚠️  Failed to load {md_file}: {e}")
        
        print(f"✅ Loaded {len(notes)} notes from {self.vault_path}")
        return notes
    
    def load_note(self, file_path: Path) -> ObsidianNote:
        """
        단일 노트 파일을 로드하고 파싱
        
        Args:
            file_path: 마크다운 파일 경로
            
        Returns:
            ObsidianNote 객체
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        # YAML frontmatter 파싱
        frontmatter, content = self._parse_frontmatter(raw_content)
        
        # 파일 메타데이터
        stat = file_path.stat()
        created_date = datetime.fromtimestamp(stat.st_ctime)
        modified_date = datetime.fromtimestamp(stat.st_mtime)
        
        # Obsidian 링크 추출 [[link]]
        links = self._extract_links(content)
        
        # 태그 추출 #tag
        tags = self._extract_tags(content)
        
        return ObsidianNote(
            file_path=str(file_path),
            title=file_path.stem,
            content=content,
            frontmatter=frontmatter,
            links=links,
            tags=tags,
            created_date=created_date,
            modified_date=modified_date
        )
    
    def _parse_frontmatter(self, content: str) -> tuple[Dict, str]:
        """
        YAML frontmatter를 파싱
        
        Args:
            content: 원본 마크다운 내용
            
        Returns:
            (frontmatter dict, content without frontmatter)
        """
        frontmatter = {}
        
        # YAML frontmatter 패턴: --- ... ---
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)
        
        if match:
            yaml_content = match.group(1)
            try:
                frontmatter = yaml.safe_load(yaml_content) or {}
            except yaml.YAMLError as e:
                print(f"⚠️  YAML parsing error: {e}")
            
            # frontmatter 제거한 본문
            content = content[match.end():]
        
        return frontmatter, content
    
    def _extract_links(self, content: str) -> List[str]:
        """
        Obsidian 링크 추출: [[link]], [[link|alias]]
        
        Args:
            content: 마크다운 내용
            
        Returns:
            링크 리스트
        """
        # [[link]] 또는 [[link|alias]] 패턴
        pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        matches = re.findall(pattern, content)
        
        # 중복 제거
        return list(set(matches))
    
    def _extract_tags(self, content: str) -> List[str]:
        """
        태그 추출: #tag
        
        Args:
            content: 마크다운 내용
            
        Returns:
            태그 리스트
        """
        # #tag 패턴 (단, 헤딩 #은 제외)
        # 단어 경계나 공백 뒤의 #만 매치
        pattern = r'(?:^|\s)#([a-zA-Z가-힣0-9_/-]+)'
        matches = re.findall(pattern, content)
        
        # 중복 제거
        return list(set(matches))
    
    def get_note_by_title(self, title: str) -> Optional[ObsidianNote]:
        """
        제목으로 노트 검색
        
        Args:
            title: 노트 제목
            
        Returns:
            찾은 노트 또는 None
        """
        target_path = self.vault_path / f"{title}.md"
        
        if target_path.exists():
            return self.load_note(target_path)
        
        return None
    
    def get_backlinks(self, note_title: str, all_notes: List[ObsidianNote]) -> List[ObsidianNote]:
        """
        특정 노트를 링크하는 다른 노트들 찾기 (역링크)
        
        Args:
            note_title: 대상 노트 제목
            all_notes: 모든 노트 리스트
            
        Returns:
            역링크를 가진 노트 리스트
        """
        backlinks = []
        
        for note in all_notes:
            if note_title in note.links:
                backlinks.append(note)
        
        return backlinks
    
    def get_notes_by_tag(self, tag: str, all_notes: List[ObsidianNote]) -> List[ObsidianNote]:
        """
        특정 태그를 가진 노트들 찾기
        
        Args:
            tag: 태그명 (# 없이)
            all_notes: 모든 노트 리스트
            
        Returns:
            해당 태그를 가진 노트 리스트
        """
        return [note for note in all_notes if tag in note.tags]
    
    def export_to_dict(self, note: ObsidianNote) -> Dict:
        """
        ObsidianNote를 딕셔너리로 변환 (JSON 직렬화 가능)
        
        Args:
            note: ObsidianNote 객체
            
        Returns:
            딕셔너리
        """
        return {
            "file_path": note.file_path,
            "title": note.title,
            "content": note.content,
            "frontmatter": note.frontmatter,
            "links": note.links,
            "tags": note.tags,
            "created_date": note.created_date.isoformat() if note.created_date else None,
            "modified_date": note.modified_date.isoformat() if note.modified_date else None,
        }


# 사용 예시
if __name__ == "__main__":
    import json
    
    # Vault 경로 설정 (본인의 경로로 변경)
    VAULT_PATH = "~/Documents/Obsidian Vault"
    
    # 로더 초기화
    loader = ObsidianVaultLoader(VAULT_PATH)
    
    # 모든 노트 로드
    notes = loader.load_vault()
    
    # 통계 출력
    print(f"\n📊 Vault Statistics")
    print(f"Total notes: {len(notes)}")
    print(f"Total links: {sum(len(note.links) for note in notes)}")
    print(f"Total tags: {len(set(tag for note in notes for tag in note.tags))}")
    
    # 샘플 노트 출력
    if notes:
        sample = notes[0]
        print(f"\n📄 Sample Note: {sample.title}")
        print(f"Links: {sample.links[:5]}")
        print(f"Tags: {sample.tags}")
        print(f"Frontmatter: {sample.frontmatter}")
        print(f"Content preview:\n{sample.content[:200]}...")
        
        # 역링크 찾기
        backlinks = loader.get_backlinks(sample.title, notes)
        print(f"\n🔗 Backlinks ({len(backlinks)}):")
        for bl in backlinks[:5]:
            print(f"  - {bl.title}")
        
        # JSON으로 변환
        note_dict = loader.export_to_dict(sample)
        print(f"\n📝 JSON Export:")
        print(json.dumps(note_dict, indent=2, ensure_ascii=False)[:500])
