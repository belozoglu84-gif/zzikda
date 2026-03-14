# Blueprint 스키마 정의

## blueprint.json이란?

각 레퍼런스의 핵심 디자인 데이터를 **실제 코드에 바로 쓸 수 있는 형태**로 정제한 파일.
기존 styles.json(CSS 덤프)과 report.md(분석 요약)에서 추출하되,
**슬롯(slot)** 개념으로 "여기에 사용자 자료를 넣어라"를 명시한다.

---

## 구조

```json
{
  "id": "003",
  "name": "하남돼지집",
  "industry": "고기",
  "tone": "dark-premium",
  "grade": "A",

  "colors": {
    "bg_primary": "#000000",
    "bg_secondary": "#111111",
    "text_primary": "#FFFFFF",
    "text_secondary": "#AAAAAA",
    "accent": "#FFFFFF",
    "accent_secondary": null,
    "border": "#333333"
  },

  "fonts": {
    "heading": {
      "family": "SUIT",
      "cdn": "https://cdn.jsdelivr.net/...",
      "weights": [700]
    },
    "body": {
      "family": "NotoSansKR",
      "cdn": "https://fonts.googleapis.com/...",
      "weights": [400, 700]
    },
    "sizes": {
      "hero": "48px",
      "section_title": "32px",
      "subtitle": "24px",
      "body": "16px",
      "caption": "14px",
      "button": "16px"
    }
  },

  "layout": {
    "container_max": "1280px",
    "section_padding": "100px",
    "gap": "30px",
    "button_radius": "0px"
  },

  "sections": [
    {
      "id": "hero",
      "name": "히어로",
      "bg": "bg_primary",
      "height": "100vh",
      "slots": {
        "headline": "[메인 슬로건]",
        "subtext": "[서브 메시지]",
        "image": "[히어로 배경 이미지]",
        "cta_text": "가맹 상담 신청"
      }
    },
    {
      "id": "brand",
      "name": "브랜드 소개",
      "bg": "bg_secondary",
      "slots": {
        "title": "[브랜드명] 이야기",
        "description": "[브랜드 철학/스토리]",
        "image": "[브랜드 대표 이미지]"
      }
    },
    {
      "id": "menu",
      "name": "메뉴/상품",
      "bg": "bg_primary",
      "slots": {
        "title": "대표 메뉴",
        "items": [
          { "name": "[메뉴1]", "desc": "[설명]", "image": "[사진]" },
          { "name": "[메뉴2]", "desc": "[설명]", "image": "[사진]" },
          { "name": "[메뉴3]", "desc": "[설명]", "image": "[사진]" }
        ]
      }
    },
    {
      "id": "franchise",
      "name": "가맹 안내",
      "bg": "bg_secondary",
      "slots": {
        "title": "가맹 안내",
        "costs": {
          "franchise_fee": "[가맹비]",
          "education_fee": "[교육비]",
          "interior_fee": "[인테리어비]",
          "deposit": "[보증금]",
          "total": "[총 창업비용]"
        },
        "cta_text": "가맹 문의하기"
      }
    },
    {
      "id": "interior",
      "name": "인테리어/매장",
      "bg": "bg_primary",
      "slots": {
        "title": "매장 갤러리",
        "images": ["[매장사진1]", "[매장사진2]", "[매장사진3]"]
      }
    },
    {
      "id": "support",
      "name": "본사 지원",
      "bg": "bg_secondary",
      "slots": {
        "title": "본사 지원 시스템",
        "items": [
          { "icon": "education", "title": "[교육 지원]", "desc": "[설명]" },
          { "icon": "interior", "title": "[인테리어 지원]", "desc": "[설명]" },
          { "icon": "logistics", "title": "[물류 지원]", "desc": "[설명]" },
          { "icon": "marketing", "title": "[마케팅 지원]", "desc": "[설명]" }
        ]
      }
    },
    {
      "id": "success",
      "name": "성공 사례",
      "bg": "bg_primary",
      "slots": {
        "title": "성공 사례",
        "cases": [
          { "name": "[점주명]", "location": "[지역]", "quote": "[후기]" }
        ]
      }
    },
    {
      "id": "contact",
      "name": "문의/상담",
      "bg": "bg_secondary",
      "slots": {
        "title": "가맹 상담 신청",
        "phone": "[전화번호]",
        "form_fields": ["이름", "연락처", "희망지역", "문의내용"]
      }
    },
    {
      "id": "footer",
      "name": "푸터",
      "bg": "bg_primary",
      "slots": {
        "company": "[회사명]",
        "ceo": "[대표자]",
        "address": "[주소]",
        "business_number": "[사업자번호]",
        "phone": "[전화번호]",
        "email": "[이메일]"
      }
    }
  ],

  "animations": {
    "hover_duration": "0.3s",
    "appear_duration": "0.7s",
    "easing": "ease-out",
    "scroll_library": null,
    "slider_count": 0
  },

  "cta": {
    "count": 5,
    "positions": ["nav", "hero", "franchise", "contact", "floating_mobile"],
    "primary_style": {
      "bg": "accent",
      "text": "bg_primary",
      "radius": "0px",
      "padding": "12px 32px",
      "font_size": "16px"
    }
  },

  "contact_form": {
    "fields": ["이름", "연락처", "희망지역", "문의내용"],
    "submit_text": "무료 상담 신청"
  },

  "floating_cta": {
    "enabled": true,
    "mobile_only": true,
    "buttons": [
      { "text": "전화 상담", "action": "tel:[전화번호]", "style": "outline" },
      { "text": "가맹 문의", "action": "#contact", "style": "filled" }
    ]
  }
}
```

---

## 슬롯(slot) 규칙

- `[대괄호]` 안의 텍스트 = 사용자가 채워야 할 항목
- 슬롯은 프로젝트 기획서(brief.md)의 값으로 자동 대체된다
- 대괄호가 없는 텍스트 = 레퍼런스의 기본값 (그대로 써도 됨)

---

## colors 키 설명

| 키 | 용도 | Tailwind 변환 |
|----|------|-------------|
| bg_primary | 메인 배경 (홀수 섹션) | `bg-[#값]` |
| bg_secondary | 보조 배경 (짝수 섹션) | `bg-[#값]` |
| text_primary | 제목, 본문 텍스트 | `text-[#값]` |
| text_secondary | 캡션, 라벨, 보조 텍스트 | `text-[#값]` |
| accent | CTA 버튼, 강조 숫자 | `bg-[#값]` or `text-[#값]` |
| accent_secondary | 보조 강조 (있으면) | 선택적 사용 |
| border | 구분선, 입력폼 테두리 | `border-[#값]` |

---

## 기획서에서 색상 오버라이드

사용자가 브랜드 컬러를 지정하면 레퍼런스 colors를 오버라이드한다:

```
기획서의 brand_color → colors.accent를 대체
기획서의 brand_color_dark → colors.accent_secondary를 대체
나머지(bg, text)는 레퍼런스 기본값 유지
```
