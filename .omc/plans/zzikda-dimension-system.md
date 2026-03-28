# 찍다 — 차원 조합 이미지 생성 시스템 구현 계획서

> 작성일: 2026-03-28
> 상태: 검토 대기

---

## 1. 요약

자영업자가 음식 사진을 올리고, **분위기→배경→앵글→소품**을 시각적으로 골라서 전문가급 메뉴사진을 AI로 재생성하는 시스템.
현재 "스타일당 프롬프트 1개" 모놀리식 구조를 → **차원별 프롬프트 조각(fragment) 조합** 구조로 전환한다.

---

## 2. 차원 분류 체계 (Taxonomy)

### 2.1 4개 차원 정의

기존 프로필 JSON의 필드를 분석해서 추출한 차원 체계:

```
차원 1: 분위기 (Mood)
├── 밝고 경쾌한 (Bright & Airy)
├── 따뜻한 가정식 (Warm & Rustic)
├── 어둡고 무디한 (Dark & Moody)
├── 필름 빈티지 (Film Vintage)
├── 클린 미니멀 (Clean Minimal)
├── 비비드 팝 (Vibrant Pop)
├── 일본식 정갈한 (Japanese Zen)
├── 스트릿 캐주얼 (Street Casual)
├── 에디토리얼 매거진 (Editorial Magazine)
└── 시네마틱 (Cinematic)

차원 2: 배경 (Background)
├── 어두운 나무 테이블 (Dark Wood)
├── 밝은 나무 테이블 (Light Wood)
├── 대리석/타일 (Marble/Tile)
├── 린넨/천 (Linen/Fabric)
├── 콘크리트/시멘트 (Concrete)
├── 한지/한식 상 (Korean Traditional)
├── 접시 위 (On Plate Only)
├── 스테인리스/메탈 (Metal/Steel)
├── 컬러 단색 배경 (Solid Color)
└── 실제 매장 배경 (Real Restaurant)

차원 3: 앵글 (Angle)
├── 탑다운 / 플랫레이 (Top-down, 90°)
├── 하이앵글 (High Angle, 45°)
├── 아이레벨 (Eye Level, 0°)
├── 로우앵글 (Low Angle, -15°)
└── 다이내믹 틸트 (Dynamic Tilt)

차원 4: 소품 (Props) — 복수 선택 가능, 선택 사항
├── 젓가락/수저 (Chopsticks/Spoon)
├── 냅킨/천 (Napkin/Fabric)
├── 허브/채소 장식 (Herbs/Garnish)
├── 음료/물잔 (Beverage/Glass)
├── 양념통/소스 (Condiments/Sauce)
├── 사이드 반찬 (Side Dishes)
├── 손/사람 (Human Hands)
├── 꽃/식물 (Flowers/Plants)
├── 빈 접시/그릇 (Empty Dishes)
└── 없음 (None)
```

### 2.2 각 차원 값에 대응하는 프롬프트 조각 (Fragment)

**예시: 분위기 "밝고 경쾌한" 프래그먼트**
```
bright and airy high-key lighting, soft diffused natural light,
warm color temperature ~5400K, Kodak Portra 400 film style,
low contrast with lifted blacks, clean and fresh atmosphere
```

**예시: 배경 "어두운 나무 테이블" 프래그먼트**
```
on a rustic dark wooden table surface, artisanal ceramic tableware,
natural wood grain texture visible
```

**예시: 앵글 "탑다운" 프래그먼트**
```
shot from directly above (top-down flat lay), 90-degree overhead angle,
deep depth of field, everything in sharp focus
```

**예시: 소품 "허브/채소 장식" 프래그먼트**
```
garnished with fresh herbs (basil, parsley, or green onion),
scattered decorative vegetable elements around the main dish
```

### 2.3 프래그먼트 데이터 구조

```json
// dimensions/mood/bright-airy.json
{
  "id": "mood-bright-airy",
  "dimension": "mood",
  "name_ko": "밝고 경쾌한",
  "name_en": "Bright & Airy",
  "prompt_fragment": "bright and airy high-key lighting, soft diffused natural light, warm color temperature ~5400K, Kodak Portra 400 film style, low contrast with lifted blacks, clean and fresh atmosphere",
  "preview_image": "dimensions/mood/previews/bright-airy.jpg",
  "source_style": "bright-airy",
  "derived_from": {
    "profiles_count": 100,
    "key_stats": {
      "lighting_quality": "soft 34% / hard 64%",
      "color_temp_mean": 5452,
      "saturation": "high 주류"
    }
  }
}
```

---

## 3. 구현 단계

### Phase 1: 차원 분류 체계 구축 + 기존 데이터 재분류

**목표**: 기존 JSON 프로필 100+장을 차원별 태그로 재분류 (API 비용 0원)

**작업 내용**:

#### 1-1. 차원 정의 파일 생성
- **파일**: `dimensions/taxonomy.json`
- **내용**: 4개 차원, 각 차원의 값 목록, 한글/영문 이름
- **기준**: 위 2.1의 분류 체계 기반
- **검증**: 기존 10개 스타일이 모두 차원 조합으로 표현 가능한지 확인

#### 1-2. 기존 프로필 자동 매핑 스크립트
- **파일**: `scripts/reclassify_profiles.py`
- **입력**: `styles/*/2_분석/*_profile.json` (기존 분석 결과)
- **처리**: 각 프로필의 필드를 차원 값으로 매핑
  ```python
  # 매핑 규칙 예시
  def map_mood(profile):
      tone = profile["mood"]["tone"].lower()
      if "bright" in tone or "airy" in tone or "light" in tone:
          return "mood-bright-airy"
      elif "dark" in tone or "moody" in tone:
          return "mood-dark-moody"
      # ...

  def map_background(profile):
      # improvement_notes, nano_banana_prompt에서 배경 키워드 추출
      prompt = profile.get("nano_banana_prompt", "")
      if "wood" in prompt and "dark" in prompt:
          return "bg-dark-wood"
      # ...

  def map_angle(profile):
      angle = profile["composition"]["angle"]
      if "탑다운" in angle or "top" in angle.lower() or "90" in angle:
          return "angle-topdown"
      elif "45" in angle:
          return "angle-high-45"
      # ...
  ```
- **출력**: `dimensions/tagged_photos.json`
  ```json
  {
    "bright-airy_001.jpg": {
      "mood": "mood-bright-airy",
      "background": "bg-light-wood",
      "angle": "angle-eye-level",
      "props": ["prop-herbs", "prop-empty-dish"],
      "source_style": "bright-airy",
      "source_profile": "styles/bright-airy/2_분석/bright-airy_001_profile.json"
    }
  }
  ```
- **한계**: 자동 매핑이 100% 정확하지 않을 수 있음 → Phase 2의 인터뷰 도구로 보정

#### 1-3. 매핑 정확도 리포트
- 자동 매핑 후 "미분류(unknown)" 비율 출력
- 미분류 항목은 Phase 2에서 수동 태깅

**검증 기준**:
- [ ] taxonomy.json에 4개 차원 × 5~10개 값 정의됨
- [ ] 기존 bright-airy 100장 프로필이 전부 태깅됨
- [ ] 자동 매핑 정확도 70% 이상 (수동 샘플링 10장 확인)
- [ ] 미분류 항목 목록이 리포트에 출력됨

---

### Phase 2: 사진 분류 인터뷰 도구

**목표**: 사진을 보면서 사용자가 직접 차원별 태그를 달 수 있는 도구

**작업 내용**:

#### 2-1. 인터뷰 도구 구현
- **파일**: `scripts/classify_interview.py`
- **방식**: 터미널 기반 (Python + 이미지 뷰어)
- **흐름**:
  ```
  1. 미분류 또는 전체 사진 목록 로드
  2. 사진 1장을 기본 이미지 뷰어로 열기 (os.startfile 또는 PIL show)
  3. 터미널에 객관식 질문 표시

  === 사진: bright-airy_001.jpg ===
  [이미지가 뷰어에서 열립니다]

  Q1. 분위기는? (숫자 입력)
   1) 밝고 경쾌한   2) 따뜻한 가정식   3) 어둡고 무디한
   4) 필름 빈티지   5) 클린 미니멀     6) 비비드 팝
   7) 일본식 정갈한  8) 스트릿 캐주얼   9) 에디토리얼
   0) 기타 (직접 입력)
  > 1

  Q2. 배경은?
   1) 어두운 나무   2) 밝은 나무   3) 대리석/타일
   4) 린넨/천      5) 콘크리트   6) 한지/한식 상
   7) 접시 위만    8) 메탈      9) 컬러 단색
   0) 기타
  > 2

  Q3. 앵글은?
   1) 탑다운(위에서)  2) 하이앵글(45도)  3) 아이레벨(정면)
   4) 로우앵글       5) 다이내믹 틸트
  > 3

  Q4. 소품은? (복수 선택: 1,3,5)
   1) 젓가락/수저  2) 냅킨/천    3) 허브/장식
   4) 음료/잔     5) 양념/소스  6) 사이드 반찬
   7) 손/사람     8) 꽃/식물   9) 빈 접시
   0) 없음
  > 1,3

  ✅ 저장: bright-airy_001.jpg → 밝고경쾌한 / 밝은나무 / 아이레벨 / 젓가락,허브
  다음 사진으로? (Enter=다음, q=종료, b=이전으로)
  ```

#### 2-2. 기능 요구사항
- **진행 상태 저장**: 중간에 종료해도 이어서 작업 가능 (`dimensions/classify_progress.json`)
- **자동 매핑 프리필**: Phase 1에서 자동 매핑된 값을 기본값으로 보여주기 (확인만 하면 됨)
- **수정 기능**: 이전 태깅을 수정할 수 있음 (b키)
- **통계 표시**: 현재까지 분류된 사진 수 / 전체 수 표시
- **결과 저장**: `dimensions/tagged_photos.json`에 누적 저장

#### 2-3. 웹 버전 (선택사항, 나중에)
- 터미널 버전으로 충분하면 생략
- 필요하면 간단한 HTML 페이지로 구현 (이미지 표시 + 버튼 클릭)

**검증 기준**:
- [ ] 사진이 뷰어에 정상 표시됨
- [ ] 4개 질문에 답하면 JSON에 저장됨
- [ ] 중간 종료 후 이어서 작업 가능
- [ ] 자동 매핑 프리필이 표시됨 (Enter만 치면 확인)
- [ ] 10장 연속 분류 테스트 통과

---

### Phase 3: 프롬프트 프래그먼트 시스템

**목표**: 차원별 선택을 조합해서 하나의 생성 프롬프트를 만드는 엔진

**작업 내용**:

#### 3-1. 프래그먼트 정의
- **폴더**: `dimensions/fragments/`
  ```
  dimensions/fragments/
  ├── mood/
  │   ├── bright-airy.json      (프롬프트 조각 + 메타데이터)
  │   ├── dark-moody.json
  │   └── ...
  ├── background/
  │   ├── dark-wood.json
  │   ├── marble.json
  │   └── ...
  ├── angle/
  │   ├── topdown.json
  │   ├── high-45.json
  │   └── ...
  └── props/
      ├── chopsticks.json
      ├── herbs.json
      └── ...
  ```

#### 3-2. 프래그먼트 추출 방법

기존 통합 프로필에서 차원별로 분해:

```
현재 unified_nano_banana_prompt (bright-airy):
"Professional Korean food photography,
 shot at 탑다운 / 플랫레이 high angle,          ← 앵글 프래그먼트
 hard left / 좌측 directional lighting           ← 분위기 프래그먼트 (일부)
 from studio strobe,
 warm color temperature ~5452K,                  ← 분위기 프래그먼트 (일부)
 Kodak Portra 400 film style,                    ← 분위기 프래그먼트 (일부)
 desaturated and muted tones with cinematic
 grading, lifted blacks,
 on 71mm lens with deep depth of field,          ← 앵글 프래그먼트 (일부)
 extreme sharpness (very-high) on food texture,
 warm & cozy atmosphere,                         ← 분위기 프래그먼트 (일부)
 rustic dark wooden table,                       ← 배경 프래그먼트
 artisanal ceramic tableware,                    ← 소품 프래그먼트
 editorial food magazine quality, 8K resolution." ← 공통 품질 프래그먼트
```

분해 후:
```
공통 = "Professional Korean food photography of {food_name}, {quality_suffix}"
분위기 = "bright and airy high-key lighting, soft diffused light, warm ~5400K, Kodak Portra 400 style, lifted blacks"
배경 = "on a rustic dark wooden table, natural wood grain texture"
앵글 = "shot from directly above (top-down flat lay), deep depth of field"
소품 = "with artisanal ceramic tableware"
품질 = "editorial food magazine quality, ultra detailed, 8K resolution"
```

#### 3-3. 프롬프트 조합 엔진
- **파일**: `scripts/prompt_composer.py`
- **입력**: 차원별 선택값 4개 + 음식명 + 미세조정 텍스트(선택)
- **출력**: 최종 프롬프트 문자열

```python
def compose_prompt(food_name: str, mood: str, background: str,
                   angle: str, props: list[str], tweaks: str = "") -> str:
    """
    차원별 프래그먼트를 조합해서 최종 프롬프트 생성

    Args:
        food_name: "김치찌개" 또는 recipes.json의 영문 설명
        mood: "mood-bright-airy"
        background: "bg-dark-wood"
        angle: "angle-topdown"
        props: ["prop-chopsticks", "prop-herbs"]
        tweaks: "소스 많이, 김치 조각 크게" (채팅에서 받은 미세조정)
    """
    # 1. 각 프래그먼트 로드
    mood_frag = load_fragment("mood", mood)
    bg_frag = load_fragment("background", background)
    angle_frag = load_fragment("angle", angle)
    prop_frags = [load_fragment("props", p) for p in props]

    # 2. 음식 설명 (recipes.json에서 영문 설명 가져오기)
    food_desc = get_food_description(food_name)

    # 3. 조합
    prompt = f"Professional Korean food photography of {food_desc}, "
    prompt += f"{mood_frag}, "
    prompt += f"{bg_frag}, "
    prompt += f"{angle_frag}, "
    if prop_frags:
        prompt += ", ".join(prop_frags) + ", "
    if tweaks:
        prompt += f"additional details: {tweaks}, "
    prompt += "editorial food magazine quality, ultra detailed, 8K resolution"

    return prompt
```

#### 3-4. 조합 품질 검증
- 10개 대표 조합으로 프롬프트 생성 후 실제 이미지 생성 테스트
- 프래그먼트 간 충돌 확인 (예: "밝은 분위기" + "어두운 나무 배경" → 어색하지 않은지)
- 충돌하는 조합은 `dimensions/conflicts.json`에 기록

**검증 기준**:
- [ ] 10개 스타일에 대응하는 프래그먼트 세트 완성
- [ ] compose_prompt()가 모든 차원 조합에서 유효한 프롬프트 생성
- [ ] 대표 조합 10개 실제 이미지 생성 → 스타일 반영 확인
- [ ] 충돌 조합 목록 작성됨

---

### Phase 4: 프리뷰 이미지 라이브러리 생성

**목표**: 서비스 UI에서 보여줄 템플릿 프리뷰 사진을 미리 생성

**작업 내용**:

#### 4-1. 생성 전략 — 계단식 (수직 조합 UX에 맞춤)

서비스 UX가 수직 조합이므로, 프리뷰도 계단식으로 생성:

```
Step 1: 분위기 프리뷰 (10장)
  → 대표 음식(비빔밥)으로, 분위기별 1장씩
  → 배경/앵글/소품은 기본값 고정

Step 2: 배경 프리뷰 (분위기별 × 10장 = 100장)
  → 분위기 "밝고 경쾌한" 선택 시 → 배경 10종 프리뷰
  → 분위기 "어둡고 무디한" 선택 시 → 배경 10종 프리뷰
  → 같은 음식, 같은 앵글, 분위기+배경만 변경

Step 3: 앵글 프리뷰 (5장 × 주요 조합)
  → 분위기+배경 조합별로 앵글 5종
  → 전체: 최대 10×10×5 = 500장이지만...
  → 실제: 인기 조합 상위 20개 × 5앵글 = 100장이면 충분

Step 4: 소품은 프리뷰 없이 아이콘/텍스트로 선택
  → 소품은 "적용될 수도 안될 수도" 있으므로 사진 불필요
```

#### 4-2. 실제 필요한 프리뷰 수량

```
분위기 프리뷰:      10장
배경 프리뷰:        10 분위기 × 10 배경 = 100장 (최대)
                    → 실제: 인기 분위기 5개 × 10 배경 = 50장
앵글 프리뷰:        인기 조합 20개 × 5 앵글 = 100장
소품 프리뷰:        없음 (아이콘 사용)
────────────────────────────────────
총계:              약 160~260장
```

#### 4-3. 프리뷰 생성 스크립트
- **파일**: `scripts/generate_previews.py`
- **처리**: compose_prompt()로 프롬프트 만들고 → 나노바나나프로로 생성
- **저장**: `dimensions/previews/{dimension}/{value}/preview_{food}.jpg`
- **비용**: 260장 × Gemini 이미지 생성 = 1회성 비용 (서비스 준비 단계)
- **음식**: 대표 음식 1개(비빔밥)로 통일해서 스타일 차이만 보이게

#### 4-4. 저작권 안전 처리
- 수집한 참고 사진은 프리뷰로 직접 사용 불가
- AI로 재생성한 사진만 프리뷰로 사용
- 각 프리뷰에 생성 프롬프트 메타데이터 저장 (재현 가능하도록)

**검증 기준**:
- [ ] 분위기 프리뷰 10장 생성 완료
- [ ] 배경 프리뷰 50장 이상 생성 완료
- [ ] 프리뷰 간 스타일 차이가 시각적으로 명확
- [ ] 모든 프리뷰에 생성 메타데이터 저장됨

---

### Phase 5: 이미지 참조 생성 파이프라인

**목표**: 사용자 원본 사진 + 차원 선택 → 최종 메뉴사진 생성

**작업 내용**:

#### 5-1. 이미지 참조 생성 함수
- **파일**: `scripts/generate_with_reference.py`
- **방식**: 나노바나나프로의 이미지 참조(image consistency) 기능 활용

```python
def generate_menu_photo(
    reference_image_path: str,    # 사용자가 올린 원본 음식 사진
    mood: str,                    # 선택한 분위기
    background: str,              # 선택한 배경
    angle: str,                   # 선택한 앵글
    props: list[str],             # 선택한 소품
    tweaks: str = "",             # 채팅 미세조정
    food_name: str = "",          # 음식 이름 (선택)
) -> tuple[bytes, str]:
    """
    사용자 원본 사진을 참조해서 선택한 스타일로 재생성

    Returns: (이미지 바이트, MIME 타입)
    """
    # 1. 프롬프트 조합
    prompt = compose_prompt(food_name, mood, background, angle, props, tweaks)

    # 2. 참조 이미지 로드
    ref_image = load_image(reference_image_path)

    # 3. 나노바나나프로 호출 (이미지 참조 + 텍스트 프롬프트)
    from google.genai import types

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[
            ref_image,                    # 참조 이미지
            f"이 음식을 참고해서 다음 스타일로 전문가급 사진을 생성해주세요:\n{prompt}"
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            temperature=0.8,
        ),
    )

    # 4. 결과 이미지 추출
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data, part.inline_data.mime_type

    return None, None
```

#### 5-2. 프롬프트 최적화 실험
- 참조 이미지 + 텍스트 프롬프트 조합 시 최적의 지시문 패턴 찾기
- 테스트 케이스 (음식 3종 × 스타일 3종 = 9장):
  - 김치찌개: 밝은+나무+45도, 어두운+대리석+탑다운, 빈티지+천+정면
  - 비빔밥: 밝은+대리석+탑다운, 팝+컬러배경+45도, 클린+접시위+정면
  - 돈까스: 일식+나무+45도, 에디토리얼+대리석+탑다운, 캐주얼+매장+정면
- 각 결과를 평가: 원본 음식 인식도, 스타일 반영도, 전체 품질

#### 5-3. 음식 인식 보조 (선택사항)
- 참조 이미지만으로 부족할 때, 음식 설명 텍스트 추가
- recipes.json에 음식이 있으면 영문 설명 자동 삽입
- 없으면 Gemini Flash로 음식 인식 → 설명 텍스트 생성 (저비용)

**검증 기준**:
- [ ] 참조 이미지 + 프롬프트로 이미지 생성 성공
- [ ] 9개 테스트 케이스 생성 → 원본 음식이 인식 가능
- [ ] 스타일 차이가 시각적으로 명확
- [ ] 미세조정(tweaks) 텍스트가 결과에 반영됨

---

## 4. 폴더 구조 (최종)

```
c:/claudcode-work/chef-photo/
├── dimensions/                          # 차원 시스템 (신규)
│   ├── taxonomy.json                    # 차원 정의 (4개 차원 × N개 값)
│   ├── tagged_photos.json               # 전체 사진의 차원 태그
│   ├── classify_progress.json           # 인터뷰 도구 진행 상태
│   ├── conflicts.json                   # 충돌하는 차원 조합 목록
│   ├── fragments/                       # 프롬프트 조각
│   │   ├── mood/
│   │   │   ├── bright-airy.json
│   │   │   ├── dark-moody.json
│   │   │   └── ...
│   │   ├── background/
│   │   ├── angle/
│   │   └── props/
│   └── previews/                        # 프리뷰 이미지
│       ├── mood/
│       ├── background/
│       └── angle/
├── scripts/                             # 스크립트 (기존 + 신규)
│   ├── batch_analyze.py                 # 기존 (유지)
│   ├── unify_profiles.py                # 기존 (유지)
│   ├── generate_food_photos.py          # 기존 (유지)
│   ├── run_pipeline.py                  # 기존 (유지)
│   ├── reclassify_profiles.py           # 신규: Phase 1
│   ├── classify_interview.py            # 신규: Phase 2
│   ├── prompt_composer.py               # 신규: Phase 3
│   ├── generate_previews.py             # 신규: Phase 4
│   └── generate_with_reference.py       # 신규: Phase 5
├── styles/                              # 기존 스타일 데이터 (유지, 참조용)
└── recipes.json                         # 음식 레시피 데이터 (유지)
```

---

## 5. 실행 순서 및 의존성

```
Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4
(자동분류)   (수동보정)   (프롬프트)   (프리뷰)
                              │
                              └──→ Phase 5
                                   (참조생성)
```

| Phase | 예상 작업량 | API 비용 | 선행 조건 |
|-------|-----------|---------|----------|
| 1. 자동 재분류 | 스크립트 1개 | 0원 | 없음 |
| 2. 인터뷰 도구 | 스크립트 1개 | 0원 | Phase 1 |
| 3. 프롬프트 엔진 | 스크립트 1개 + 프래그먼트 JSON 40개 | 테스트용 소액 | Phase 1 |
| 4. 프리뷰 생성 | 스크립트 1개 + 이미지 160~260장 | 이미지 생성 비용 1회 | Phase 3 |
| 5. 참조 생성 | 스크립트 1개 + 실험 | 테스트용 소액 | Phase 3 |

---

## 6. 리스크 및 대응

| 리스크 | 영향 | 대응 |
|--------|------|------|
| 프래그먼트 조합이 어색한 결과를 낼 수 있음 | 특정 조합에서 품질 하락 | Phase 3에서 충돌 조합 사전 테스트, conflicts.json으로 관리 |
| 참조 이미지가 결과에 너무 강하게/약하게 반영 | 원본 음식 미인식 또는 스타일 미반영 | Phase 5에서 프롬프트 패턴 실험 (temperature, 지시문 조정) |
| 자동 매핑 정확도가 낮을 수 있음 | 잘못된 태그로 프래그먼트 추출 | Phase 2 인터뷰 도구로 수동 보정 |
| 프리뷰 260장 생성 비용 | 1회성이지만 비용 발생 | 인기 조합 우선 생성, 나머지는 필요할 때 추가 |
| 미세조정(채팅) 내용이 프롬프트에 안 맞을 수 있음 | 사용자 기대와 결과 불일치 | 채팅 입력을 구조화된 옵션으로 제한 (자유 입력은 보조) |

---

## 7. 향후 확장 (이번 플랜 범위 밖)

- **서비스 웹앱 개발**: 현재는 스크립트 기반, 나중에 웹 UI 필요
- **사용자 피드백 학습**: "이 결과 좋다/나쁘다" 피드백으로 프래그먼트 개선
- **새 차원 추가**: 조명 방향, 그릇 종류, 계절감 등
- **배치 생성**: 한 번에 메뉴판 전체 사진 세트 생성
- **A/B 테스트**: 같은 음식 다른 스타일 2장 생성 → 사용자가 선택
