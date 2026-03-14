# 찍다 - AI 메뉴사진 생성 서비스 랜딩페이지

## 필수: 작업 시작 전 반드시 아래 파일을 모두 읽을 것

1. `기획서_찍다_랜딩페이지.md` — 서비스 기획서
2. `.claude/skills/landing-dev/SKILL.md` — 개발 규칙 (기술 스택, HTML 구조, JS 패턴)
3. `.claude/skills/landing-design/SKILL.md` — 디자인 시스템 (컬러, 타이포, 애니메이션)
4. `.claude/skills/landing-sections/SKILL.md` — 섹션 구조 가이드
5. `.claude/skills/landing-reference/SKILL.md` — 레퍼런스 활용 가이드

**스킬을 읽지 않고 코드를 작성하면 안 된다.**

---

## 리소스 경로

- 레퍼런스: c:/claudcode-work/homepage_src/references/
- 샘플 이미지: c:/claudcode-work/chef-photo/landing/images/

---

## 프로젝트 개요

- **프로젝트**: 찍다 - AI 메뉴사진 생성 서비스 랜딩페이지
- **서비스**: 자영업자를 위한 AI 메뉴사진 생성 (작가 스타일 프리셋 선택 → 음식명 입력 → 전문가급 사진)
- **목적**: 서비스 소개 + 사전등록(이메일) 수집 + 스타일 갤러리 쇼케이스
- **경로**: c:/claudcode-work/chef-photo/

## 기술 스택 (절대 변경 금지)

| 기술 | 버전/CDN | 역할 |
|------|----------|------|
| HTML5 | 단일 `index.html` 파일 | 전체 페이지 |
| Tailwind CSS | CDN (play.tailwindcss.com) | 스타일링 |
| Google Fonts | CDN | 영문 헤드라인 폰트 |
| 한글 폰트 | CDN (jsdelivr 등) | 한글 본문 폰트 |
| Vanilla JS | `<script>` 태그 | 인터랙션 |

**빌드 도구 없음. React 없음. Node.js 없음. 프레임워크 없음.**

## 사진

- **경로**: `images/` 폴더
- **포맷**: JPG + WebP 쌍으로 준비
- **사용법**: `<picture>` 태그로 WebP 우선 로딩

## 핵심 규칙

1. **단일 파일**: `index.html` 하나에 HTML + CSS + JS 모두 포함
2. **한국어**: 대화, 주석, 커밋 메시지 모두 한국어
3. **영어**: 변수명, 함수명, CSS 클래스명
4. **기존 코드 보호**: 승인 없이 이미 작동하는 코드를 리팩토링하지 말 것
5. **사진 경로**: 항상 `images/` 폴더의 전처리된 파일 사용
6. **WebP 우선**: `<picture>` 태그로 WebP 먼저, JPG fallback

## 워크플로우 명령어

- `/새랜딩 [브랜드명]` → 5단계 워크플로우 시작 (브랜드분석 → 레퍼런스 → 설계 → 코딩 → 검증)

## 금지 사항

| 금지 | 이유 |
|------|------|
| React, Vue, Angular 등 프레임워크 | 단일 HTML 파일 프로젝트 |
| npm, yarn, pnpm | 빌드 도구 없음 |
| 외부 JS 라이브러리 (jQuery, GSAP 등) | Vanilla JS만 사용 |
| 원본 사진 직접 참조 | `images/` 폴더의 전처리 파일만 사용 |
| 영어 주석/커밋 | 한국어만 사용 |
