---
name: landing-design
description: 랜딩페이지 디자인 시스템. 레퍼런스에서 색상/폰트/여백을 추출하고 적용하는 방법. 디자인, 색상, 컬러, 폰트, 애니메이션, 스타일 관련 작업 시 트리거.
---

# 디자인 시스템 (레퍼런스 기반)

## 핵심 원칙

디자인 수치를 직접 정하지 마라.
선택된 레퍼런스의 `blueprint.json`에서 colors/fonts/layout을 읽고 그대로 적용하라.
blueprint가 없으면 `styles.json`과 `report.md`에서 추출한다.

---

## 1. 레퍼런스에서 디자인 추출하기

### 색상 추출

**blueprint.json이 있으면** → `colors` 객체를 그대로 사용:

```json
"colors": {
  "bg_primary": "#000000",     → bg-[#000000] (홀수 섹션)
  "bg_secondary": "#111111",   → bg-[#111111] (짝수 섹션)
  "text_primary": "#FFFFFF",   → text-[#FFFFFF] (제목, 본문)
  "text_secondary": "#999999", → text-[#999999] (캡션, 라벨)
  "accent": "#FFFFFF",         → bg-[#FFFFFF] (CTA 버튼)
  "border": "#333333"          → border-[#333333] (구분선)
}
```

**blueprint가 없으면** → `styles.json` → `topColors`에서 RGB를 HEX로 변환해서 추출

아래 템플릿에 채워서 사용:

| 용도 | Tailwind 클래스 | 추출 위치 |
|------|-----------------|-----------|
| 배경 (주) | `bg-[#______]` | 홀수 섹션 |
| 배경 (보조) | `bg-[#______]` | 짝수 섹션 (교차) |
| 텍스트 (주) | `text-[#______]` | 제목, 본문 |
| 텍스트 (보조) | `text-[#______]` | 캡션, 라벨 |
| 액센트 | `bg-[#______]` | CTA 버튼, 강조 숫자 |
| 보더 | `border-[#______]` | 구분선, 입력폼 |

### 폰트 추출

레퍼런스의 `report.md` → 폰트 항목에서:

- 헤드라인 폰트 (영문 또는 특수 한글)
- 본문 폰트 (한글 산세리프/명조)
- 2개만 쓴다. 3개 이상 금지.

### 여백 추출

레퍼런스의 `styles.json` → `spacing` 에서:

- 섹션 패딩값 확인 → 그대로 적용
- gap값 확인 → 그대로 적용

---

## 2. 실측 기반 디자인 가드레일

레퍼런스가 없거나 판단이 필요할 때만 아래 수치를 참고한다.

### 색상

- 전체 색상 5~7개 (실측 평균 6.3개)
- 배경: 흰색(#FFFFFF) 90% 사용 / 다크(#000000~#1E1E1E)
- 텍스트: #000000 35% / #333333 25% / #222222 15%

### 폰트 크기 스케일 (이 값만 사용)

```
본문:    14px, 16px, 18px
소제목:  20px, 24px, 28px, 32px
제목:    36px, 40px, 48px
대제목:  56px, 64px, 72px (히어로 전용)
```

### 여백 (이 값만 사용)

- 섹션 패딩: 40px, 60px, 80px, 100px, 120px (100px이 34%로 1위)
- gap: 10px, 20px, 24px, 30px, 40px, 50px, 60px (30px이 25%로 1위)
- 컨테이너: max-w-7xl (1280px)

### 버튼

- border-radius: 0px(각진, 51%) 또는 pill(rounded-full, 15%)
- font-size: 14px 또는 16px
- padding: 세로 8~16px / 가로 20~30px

### 애니메이션

- 호버: 0.2~0.3초 (duration-300)
- 등장: 0.5~0.7초 (duration-700)
- easing: ease-out 기본

---

## 3. 폰트 조합 레퍼런스

레퍼런스에서 폰트를 직접 못 찾았을 때 아래에서 선택:

| 분위기 | 영문 헤드라인 | 한글 본문 | 사용 레퍼런스 |
|--------|-------------|-----------|-------------|
| 프리미엄 | Playfair Display | Pretendard | 001 옥된장 참고 |
| 전통/격조 | - | GyeonggiBatang(명조) | 002 새마을식당 참고 |
| 모던/깔끔 | Montserrat | Noto Sans KR | 004, 019 참고 |
| 전통 한식 | - | NanumMyeongjo | 009 국밥도 참고 |

---

## 4. 컴포넌트 패턴

### 섹션 제목

```html
<div class="text-center mb-16">
  <span class="text-[액센트] text-sm tracking-widest uppercase">[영문 라벨]</span>
  <h2 class="font-display text-3xl md:text-4xl text-[텍스트주] mt-3">[한글 섹션 제목]</h2>
  <div class="w-16 h-0.5 bg-[액센트] mx-auto mt-4"></div>
</div>
```

### 메뉴 카드

```html
<div class="group relative overflow-hidden bg-[배경보조]">
  <div class="aspect-[4/3] overflow-hidden">
    <picture>
      <source srcset="images/menu.webp" type="image/webp">
      <img src="images/menu.jpg" alt="메뉴 설명" loading="lazy"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
    </picture>
  </div>
  <div class="p-5">
    <h3 class="font-display text-lg text-[텍스트주]">[메뉴명]</h3>
    <p class="text-[텍스트보조] text-sm mt-2">[메뉴 설명]</p>
  </div>
</div>
```

### CTA 버튼

```html
<!-- 채움형 -->
<a href="#contact" class="inline-block bg-[액센트] text-white font-bold
  py-3 px-8 text-base transition-all duration-300 ease-out hover:opacity-90">
  가맹 문의하기
</a>

<!-- 아웃라인형 -->
<a href="#contact" class="inline-block border border-[액센트] text-[액센트] font-bold
  py-3 px-8 text-base transition-all duration-300 ease-out
  hover:bg-[액센트] hover:text-white">
  자세히 보기
</a>
```

---

## 5. 다크 테마 보조 기법

다크 배경 레퍼런스(002, 003, 008, 021, 022)를 참고할 때:

- 히어로 오버레이: `bg-black/50` ~ `bg-black/60`
- 호버 밝기: `brightness(1.1)`
- 노이즈 텍스처 (선택):

```css
.noise-overlay::after {
  content: '';
  position: fixed;
  inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.5'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 9999;
}
```
