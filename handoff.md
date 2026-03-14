# 핸드오프 문서 - Chef Photo (음식 사진 보정 프로젝트)

## 현재 상태: 스타일 수집 파이프라인 4개 스크립트 완성 (수집→필터→분석→통합→검증)

---

## 프로젝트 목표

- 유명 사진작가의 샘플 사진을 분석하여 스타일을 추출하고, 그 스타일대로 음식 사진을 일관되게 보정/생성하는 시스템 구축
- 최종적으로 "사진 넣기 → 자동 전문 분석 → 스타일 프로필 생성 → 일괄 보정" 워크플로우 완성
- **찍다 서비스**: 자영업자를 위한 AI 메뉴사진 생성 (작가 스타일 프리셋 선택 → 음식명 입력 → 전문가급 사진)

## 사용자 요청사항

1. 이미지 보정 프로그램을 만들고 싶다
2. 나노바나나프로2(Gemini 이미지 모델)를 활용하고 싶다
3. 샘플 사진을 넣으면 작가의 스타일을 분석 → 그 스타일대로 보정/생성하고 싶다
4. 일관적으로 좋은 품질의 결과물을 원한다
5. 전문적인 이미지 분석을 자동화하고 싶다
6. 반드시 가지고 있는 모든 자원(MCP, 스킬, 도구)을 다 사용해야 한다
7. **핵심 의도 (세션4 명확화)**: 기존 사진 보정이 아닌, nano-banana-pro로 처음부터 김현경 스타일로 생성하는 것이 목적 ("태블릿/템플릿" 개념)
8. **스타일 라이브러리 확장 (세션6)**: 김현경 스타일 1개만이 아닌, 4~5개 이상의 스타일 프리셋을 확보하여 서비스 런칭 준비

---

## 완료된 작업

### 세션 1 (2026-03-11)

1. ✅ Playwright MCP 설정 - `c:/claudcode-work/chef-photo/.mcp.json` 생성
2. ✅ 이미지 보정 스킬 조사 및 비교 - `intellectronica/agent-skills@nano-banana-pro` 선정 (설치 수 1,200회)
3. ✅ nano-banana-pro 스킬 설치 - `~/.agents/skills/nano-banana-pro/` (Gemini 3 Pro Image API 래퍼)
4. ✅ GEMINI_API_KEY 환경변수 등록
5. ✅ nano-banana-prompt 스킬 설치 - `~/.agents/skills/nano-banana-prompt/`
6. ✅ 전문 분석 프롬프트 개발 및 테스트 - "대충" vs "전문적" 비교 결과 전문 프롬프트 채택
7. ✅ 리소스 보고서 작성 - `c:/claudcode-work/chef-photo/available-resources-report.md` (30개 스킬, 6개 MCP, 37+ Gemini 도구)

### 세션 2 (2026-03-12)

1. ✅ photo-style-analyzer 스킬 설계 및 SKILL.md 작성
   - 경로: `C:\Users\emre8\.claude\skills\photo-style-analyzer\SKILL.md`
   - 4단계 프로세스: 이미지 읽기 → Gemini Pro 분석 → JSON 구조화 → 저장/출력
2. ✅ 전문 분석 레퍼런스 3종 작성
   - `references/analysis-prompt-templates.md` - 음식/인물/제품/풍경/범용 프롬프트
   - `references/photography-terminology.md` - 사진 전문 용어 사전
   - `references/style-profile-schema.md` - JSON 스키마 (9개 필드, enum 값 정의)
3. ✅ analyze_photo.py 작성 - 분석 텍스트 → JSON 변환 + Pydantic 검증 (3회 재시도)
   - 경로: `C:\Users\emre8\.claude\skills\photo-style-analyzer\scripts\analyze_photo.py`
   - 14개 Pydantic Enum 모델로 엄격 검증
4. ✅ 첫 번째 실전 테스트 성공 (돼지갈비이미샷베스트.jpeg)

### 세션 3 (2026-03-13)

1. ✅ batch_analyze.py 배치 스크립트 작성
   - 경로: `c:\claudcode-work\chef-photo\batch_analyze.py`
   - Gemini Python SDK(`google-genai`)로 이미지 직접 분석
2. ✅ 김현경작가 사진 75장 전체 분석 완료 (실패 0건)
   - 샘플1: 30장 / 43분, 샘플2: 28장 / 41분, 샘플3: 14장 / 20분

### 세션 4 (2026-03-13)

1. ✅ **unify_profiles.py 작성 및 실행** - 75개 JSON → 통합 스타일 프로필 생성
2. ✅ **김현경_unified_profile.json 생성 완료**
3. ✅ **분석결과/ 폴더 생성 및 정리** - 151개 파일
4. ✅ **kim-style 스킬 생성** - `C:\Users\emre8\.claude\skills\kim-style\SKILL.md`
5. ✅ **보정 vs 생성 실험** → 결론: 처음부터 생성이 올바른 접근
6. ✅ **비빔밥/제육볶음 김현경 스타일 생성** 성공
7. ✅ **gen_wanjatang.py 스크립트 작성** - 완자탕 20장 일괄 생성용
8. ⬜ **완자탕 20장 생성 중단** - 11/20 완료 후 사용자 스탑 요청

### 세션 5 (2026-03-13)

1. ✅ **kim-style 스킬 앵글 프리셋 20종 추가**
2. ✅ **멀티샷 자동 로테이션 규칙 추가**
3. ✅ **모드 B 프롬프트 템플릿 수정** - `[ANGLE_PROMPT]` 변수화
4. ✅ **파일명 규칙 업데이트**

### 세션 6 (2026-03-15) ← 이번 세션

**목표**: 스타일 라이브러리 확장을 위한 이미지 수집 파이프라인 구축

1. ✅ **수집 전략 수립** — 하이브리드 전략 (작가 중심 + 스타일 중심 병행)
   - 플랜 파일: `C:\Users\emre8\.claude\plans\cached-painting-feather.md`
   - 프리미엄 라인: 실제 작가 협업 (김현경처럼)
   - 일반 라인: Unsplash/Pexels API로 분위기별 대량 수집 → 통계적 스타일 추출

2. ✅ **스타일 분류 체계 8가지 정의**
   - `dark-moody` (✅ 완성), `bright-airy` (🔄 수집완료/분석중), `clean-minimal`, `warm-rustic`, `vibrant-pop`, `film-vintage`, `overhead-editorial`, `street-casual`

3. ✅ **collect_style.py 신규 개발**
   - 경로: `c:\claudcode-work\chef-photo\collect_style.py`
   - Unsplash + Pexels API로 스타일별 음식사진 자동 수집
   - **핵심**: 모든 검색 키워드에 반드시 food/dish/meal 포함 (하늘/풍경 사진 방지)
   - 8가지 스타일별 검색 키워드 프리셋 내장
   - 중복 제거 (URL 해시), 최소 해상도 필터, 메타데이터 저장 (`_metadata.json`)
   - CLI: `uv run collect_style.py --style clean-minimal --source both --count 100`

4. ✅ **filter_photos.py 신규 개발**
   - 경로: `c:\claudcode-work\chef-photo\filter_photos.py`
   - Gemini 2.0 Flash로 빠른 1차 필터링
   - **필수 조건**: 음식이 주 피사체인지 확인 (음식 아닌 사진 즉시 제외)
   - 스타일 적합도 점수 (1~10) + 품질 점수 (1~10)
   - Rich 테이블로 상위 점수 사진 표시
   - CLI: `uv run filter_photos.py --folder 수집_clean-minimal --style clean-minimal`

5. ✅ **unify_profiles.py 범용화 수정**
   - `--style-name` 파라미터 추가 (예: `--style-name "클린 미니멀"`)
   - 김현경 하드코딩 제거 → 모든 스타일에 범용 사용 가능
   - 출력 파일명 자동 결정 (`{style_name}_unified_profile.json`)

6. ✅ **validate_style.py 신규 개발**
   - 경로: `c:\claudcode-work\chef-photo\validate_style.py`
   - 통합 프로필의 프롬프트로 테스트 이미지 3~5장 자동 생성
   - 기본 테스트 음식: 김치찌개, 크림파스타, 연어포케, 티라미수, 불고기
   - CLI: `uv run validate_style.py --profile 클린_미니멀_unified_profile.json`

---

## 미완료 작업 (다음 세션)

### 우선순위 높음

1. ⬜ **파이프라인 실행: clean-minimal 스타일 수집**
   ```bash
   # 1. 수집
   uv run collect_style.py --style clean-minimal --source both --count 100
   # 2. 필터링
   uv run filter_photos.py --folder 수집_clean-minimal --style clean-minimal
   # 3. 분석
   uv run batch_analyze.py --folder 필터링_clean-minimal
   # 4. 통합 프로필
   uv run unify_profiles.py --style-name "클린 미니멀" --folder 필터링_clean-minimal
   # 5. 검증
   uv run validate_style.py --profile 필터링_clean-minimal/클린_미니멀_unified_profile.json
   ```
   - **사전 필요**: `UNSPLASH_ACCESS_KEY`와 `PEXELS_API_KEY` 환경변수 확인

2. ⬜ **bright-airy 스타일 통합 프로필 완성** — 이미 100장 수집+87장 분석 완료
   - `분석결과-밝은스타일/` 폴더의 기존 프로필 활용
   - `uv run unify_profiles.py --style-name "밝은 에어리" --folder 분석결과-밝은스타일`

3. ⬜ **kim-style 스킬 앵글 프리셋 테스트** (세션 5에서 미완)

4. ⬜ **완자탕 나머지 9장 생성** (세션 4에서 미완)

### 우선순위 보통

5. ⬜ warm-rustic 스타일 수집+분석+통합
6. ⬜ vibrant-pop 스타일 수집+분석+통합
7. ⬜ 각 스타일별 전용 스킬 생성 (kim-style 패턴 재사용)
8. ⬜ 랜딩페이지 갤러리에 생성 이미지 적용

---

## 핵심 결정사항

| 결정 | 이유 | 대안 |
| --- | --- | --- |
| nano-banana-pro 스킬 선택 | 설치 수 1,200회로 가장 검증됨 | steipete/clawdis, nkchivas 등 |
| Pydantic 엄격 검증 | 결과값 정확성이 가장 중요 | 느슨한 검증 |
| batch_analyze.py 독립 스크립트 | 74장 × ~300 MCP 호출 불가 | MCP 도구 반복 호출 (불가) |
| 보정 대신 생성 선택 | AI 이미지 편집은 원본 보존 경향 강함 | 이미지 편집/보정 모드 |
| 앵글 프리셋 20종 정의 | 완자탕 탑뷰가 45도보다 좋았음 → 다양화 필요 | 앵글 고정 (45도만) |
| **하이브리드 수집 전략** | 작가 중심(프리미엄) + 스타일 중심(일반) 병행이 가장 효율적 | 작가만 or 스타일만 |
| **검색 키워드에 food 필수 포함** | "clean minimal"만 검색하면 하늘/풍경 사진 대량 섞임 | 스타일 키워드만 사용 (실패) |
| **Gemini Flash로 음식 필터링** | 수집 후 비음식 사진 제거 필수 | 수동 선별 (비효율) |
| **Unsplash/Pexels 우선** | 무료 상업 이용 가능, API 자동화 가능, 저작권 안전 | Pinterest (저작권 위험) |

---

## 핵심 파일/폴더 경로

| 파일/폴더 | 용도 | 상태 |
| --- | --- | --- |
| `c:\claudcode-work\chef-photo\` | 프로젝트 루트 | ✅ |
| `c:\claudcode-work\chef-photo\collect_style.py` | **API 기반 스타일별 음식사진 자동 수집** | ✅ 신규 |
| `c:\claudcode-work\chef-photo\filter_photos.py` | **Gemini Flash 음식사진 필터링** | ✅ 신규 |
| `c:\claudcode-work\chef-photo\validate_style.py` | **통합 프로필 검증 (테스트 이미지 생성)** | ✅ 신규 |
| `c:\claudcode-work\chef-photo\batch_analyze.py` | 폴더 일괄 분석 배치 스크립트 | ✅ |
| `c:\claudcode-work\chef-photo\unify_profiles.py` | 통합 프로필 생성 (범용화 수정 완료) | ✅ 수정됨 |
| `c:\claudcode-work\chef-photo\김현경_unified_profile.json` | 김현경 통합 스타일 프로필 (핵심 데이터) | ✅ |
| `c:\claudcode-work\chef-photo\gen_wanjatang.py` | 완자탕 20장 일괄 생성 스크립트 | ✅ (11/20) |
| `c:\claudcode-work\chef-photo\분석결과\` | 김현경 75장 분석 결과 | ✅ |
| `c:\claudcode-work\chef-photo\분석결과-밝은스타일\` | 밝은스타일 87장 분석 결과 | ✅ |
| `c:\claudcode-work\chef-photo\pinterest_수집_밝은스타일\` | 밝은스타일 100장 원본 | ✅ |
| `C:\Users\emre8\.claude\skills\photo-style-analyzer\` | 사진 분석 스킬 | ✅ |
| `C:\Users\emre8\.claude\skills\kim-style\SKILL.md` | 김현경 스타일 생성 스킬 | ✅ |
| `C:\Users\emre8\.claude\plans\cached-painting-feather.md` | 수집 전략 플랜 문서 | ✅ |

---

## 기술 환경

- **OS**: Windows 11 Home
- **이미지 분석 (배치)**: Gemini Python SDK (`google-genai`, gemini-2.5-pro) — batch_analyze.py
- **이미지 필터링**: Gemini 2.0 Flash — filter_photos.py
- **이미지 생성/편집**: nano-banana-pro 스킬 (Gemini 3 Pro Image API)
- **사진 수집**: Unsplash API + Pexels API — collect_style.py
- **JSON 변환+검증**: `analyze_photo.py` (Pydantic 14개 Enum 모델, 3회 재시도)
- **API 키**: `GEMINI_API_KEY`, `UNSPLASH_ACCESS_KEY`, `PEXELS_API_KEY` 환경변수
- **Python 실행**: `uv` (패키지 러너, 의존성 자동 설치)
- **MCP 서버**: Playwright, Gemini, Pencil, Memory, Sequential Thinking, Notion

### 전체 파이프라인 흐름

```
collect_style.py → filter_photos.py → batch_analyze.py → unify_profiles.py → validate_style.py
(API 수집)       (음식 필터링)       (상세 분석)        (통합 프로필)       (검증 이미지 생성)
```

### 스타일 분류 체계 (8가지)

| 코드 | 이름 | 타겟 업종 | 상태 |
|------|------|-----------|------|
| `dark-moody` | 다크 무디 | 고급 레스토랑 | ✅ 완성 (김현경 스타일) |
| `bright-airy` | 밝은 에어리 | 카페/브런치 | 🔄 수집+분석 완료, 통합 프로필 미생성 |
| `clean-minimal` | 클린 미니멀 | 배달앱/메뉴판 | ⬜ 미시작 |
| `warm-rustic` | 따뜻한 러스틱 | 가정식/한식당 | ⬜ 미시작 |
| `vibrant-pop` | 비비드 팝 | SNS 마케팅 | ⬜ 미시작 |
| `film-vintage` | 필름 빈티지 | 감성 카페 | ⬜ 미시작 |
| `overhead-editorial` | 오버헤드 에디토리얼 | 레시피/쿡북 | ⬜ 미시작 |
| `street-casual` | 스트릿 캐주얼 | 맛집 리뷰 | ⬜ 미시작 |

---

## 주의사항 / 알려진 이슈

1. **Windows 인코딩**: 터미널 출력이 깨져 보여도 파일은 정상 생성됨 (cp949 터미널 한계)
2. **nano-banana-pro는 래퍼**: Gemini API 직접 호출과 결과 동일
3. **사용자는 비전공자**: 기술 용어에 쉬운 설명 필요, 한국어 소통
4. **김현경 작가 웹 검색 불가**: 이름 검색 결과 없음. 작가 정보는 샘플 사진 분석으로만 파악
5. **Gemini Rate Limit**: 배치 분석 시 1장당 약 90초. --delay 5 이하로 줄이면 429 에러 가능
6. **보정 모드 한계**: AI 이미지 편집으로 스타일 적용은 효과 미미 → 처음부터 생성이 올바른 방법
7. **김현경_unified_profile.json 이동 주의**: 루트에 있어야 함
8. **"clean minimal"만 검색하면 하늘 사진 섞임**: 반드시 food/dish/meal 키워드 포함해야 함 (이미 collect_style.py에 반영됨)
9. **수집 사진은 학습용만**: 서비스에서 보여주는 사진은 반드시 AI 생성물이어야 함 (저작권)
10. **Unsplash API 속도 제한**: 50회/시간 → collect_style.py에서 3초 간격으로 호출
11. **Pexels API 속도 제한**: 200회/시간 → collect_style.py에서 2초 간격으로 호출

---

## 다음 세션 시작 시 할 일

1. 이 `handoff.md` 읽기
2. **API 키 확인**: `UNSPLASH_ACCESS_KEY`와 `PEXELS_API_KEY` 환경변수 설정 여부
3. **bright-airy 통합 프로필 먼저 완성** (이미 분석 완료되어 바로 가능):
   ```bash
   uv run unify_profiles.py --style-name "밝은 에어리" --folder 분석결과-밝은스타일
   ```
4. **clean-minimal 파이프라인 실행** (위의 미완료 작업 #1 참조)
5. 각 스타일 검증 이미지 결과물 사용자와 함께 검토
