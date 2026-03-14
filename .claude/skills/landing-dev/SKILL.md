---
name: landing-dev
description: 랜딩페이지 개발 규칙. HTML/CSS/JS 코드 작성 시 활성화. 코딩, html, css, javascript, 구현, 개발, 섹션 만들기, 버그 수정 관련 작업 시 트리거.
---

# 개발 규칙 (코드 패턴)

## 기술 스택 (변경 금지)

```
index.html (단일 파일)
├── <head>
│   ├── Tailwind CSS CDN (play.tailwindcss.com)
│   ├── Google Fonts CDN (영문 헤드라인 폰트)
│   ├── 한글 본문 폰트 CDN (Pretendard 또는 Noto Sans KR)
│   └── <style> 커스텀 CSS (애니메이션, 텍스처)
├── <body>
│   └── 섹션들 (네비→히어로→...→푸터)
└── <script>
    └── Vanilla JS (캐러셀, 카운팅, 스크롤 감지, 탭 전환)
```

외부 라이브러리 금지: React, Vue, jQuery, GSAP, anime.js, npm, webpack, vite

---

## 1. Tailwind 설정

선택된 레퍼런스의 `blueprint.json`에서 colors/fonts를 읽어 여기에 등록한다:

```html
<script>
  tailwind.config = {
    theme: {
      extend: {
        fontFamily: {
          // blueprint.fonts.heading.family / blueprint.fonts.body.family
          display: ['"영문헤드라인폰트"', 'serif'],
          sans: ['한글본문폰트', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        },
        colors: {
          // blueprint.colors에서 가져옴
          // primary: blueprint.colors.accent,
          // accent: blueprint.colors.accent_secondary,
        },
      }
    }
  }
</script>
```

---

## 2. HTML 구조 패턴

### 섹션 기본 구조

```html
<!-- 섹션 N: 섹션이름 -->
<section id="section-id" class="relative py-[100px] bg-[배경색]">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- 섹션 내용 -->
  </div>
</section>
```

### 이미지 태그 (WebP 우선)

```html
<picture>
  <source srcset="images/파일명.webp" type="image/webp">
  <img src="images/파일명.jpg" alt="한국어 설명" loading="lazy"
       class="w-full h-full object-cover">
</picture>
```

히어로 이미지만 `loading="eager"` + `<link rel="preload">` 사용.

### 스크롤 애니메이션 요소

```html
<div data-animate class="opacity-0 translate-y-8 transition-all duration-700 ease-out">
  <!-- 내용 -->
</div>
```

---

## 3. JavaScript 패턴

### 스크롤 애니메이션 (Intersection Observer)

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('opacity-100', 'translate-y-0');
      entry.target.classList.remove('opacity-0', 'translate-y-8');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('[data-animate]').forEach(el => observer.observe(el));
```

### 카운팅 애니메이션

```javascript
function animateCount(el, target, duration = 2000) {
  const start = performance.now();
  const update = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(target * eased).toLocaleString();
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}
```

### 네비게이션 스크롤 감지

```javascript
const sections = document.querySelectorAll('section[id]');
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY + 100;
  sections.forEach(section => {
    if (scrollY >= section.offsetTop && scrollY < section.offsetTop + section.offsetHeight) {
      // 해당 섹션의 네비 탭 활성화
    }
  });
});
```

### 캐러셀/슬라이더

```javascript
let currentSlide = 0;
const slides = document.querySelectorAll('.slide');
function showSlide(index) {
  slides.forEach((s, i) => {
    s.style.opacity = i === index ? '1' : '0';
    s.style.transform = i === index ? 'translateX(0)' : 'translateX(100%)';
  });
}
setInterval(() => {
  currentSlide = (currentSlide + 1) % slides.length;
  showSlide(currentSlide);
}, 5000);
```

---

## 4. 반응형

| 기기 | 브레이크포인트 | Tailwind | 레이아웃 |
|------|-------------|----------|----------|
| 모바일 | ~767px | 기본값 | 1열, 세로 스택 |
| 태블릿 | 768px+ | `md:` | 2열 Flexbox |
| 데스크톱 | 1024px+ | `lg:` | 최대 4열 |
| 대형 | 1280px+ | `xl:` | 컨테이너 최대폭 제한 |

레이아웃은 Flexbox 기반 (`flex flex-wrap`). 레퍼런스의 layout.json에서 패턴을 확인.

---

## 5. SEO & 접근성

- `<html lang="ko">`
- 모든 이미지에 `alt` (한국어)
- 시맨틱 태그: `<nav>`, `<section>`, `<footer>`
- Open Graph 메타 태그 (카카오톡/SNS 공유)
- `<title>`: "[브랜드명] | [핵심 키워드]"
- 접근성: `@media (prefers-reduced-motion: reduce)` 지원

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
