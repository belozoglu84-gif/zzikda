#!/usr/bin/env python3
"""프래그먼트 JSON 파일 일괄 생성 (1회성 스크립트)"""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "dimensions" / "fragments"

# === 분위기 (Mood) ===
mood = {
    "bright-airy": {
        "id": "mood-bright-airy",
        "name_ko": "밝고 경쾌한",
        "name_en": "Bright & Airy",
        "prompt_fragment": "bright and airy high-key lighting, soft diffused natural light, warm color temperature around 5400K, Kodak Portra 400 film style, low contrast with lifted blacks, clean and fresh atmosphere, vibrant yet gentle tones"
    },
    "warm-rustic": {
        "id": "mood-warm-rustic",
        "name_ko": "따뜻한 가정식",
        "name_en": "Warm & Rustic",
        "prompt_fragment": "warm and cozy atmosphere, soft golden hour lighting, warm color temperature around 4500K, rustic homestyle feel, gentle shadows, nostalgic and comforting mood, slightly desaturated warm tones"
    },
    "dark-moody": {
        "id": "mood-dark-moody",
        "name_ko": "어둡고 무디한",
        "name_en": "Dark & Moody",
        "prompt_fragment": "dramatic low-key lighting, deep rich shadows, chiaroscuro style, dark and moody atmosphere, single directional light source, high contrast, cinematic color grading with teal and orange tones, mysterious and elegant"
    },
    "film-vintage": {
        "id": "mood-film-vintage",
        "name_ko": "필름 빈티지",
        "name_en": "Film Vintage",
        "prompt_fragment": "vintage film photography aesthetic, visible fine grain, faded blacks with lifted shadow tones, retro color palette, warm analog feel, reminiscent of Kodak Gold 200 or Fuji Superia, nostalgic and timeless"
    },
    "clean-minimal": {
        "id": "mood-clean-minimal",
        "name_ko": "클린 미니멀",
        "name_en": "Clean Minimal",
        "prompt_fragment": "clean and minimal aesthetic, bright even lighting, neutral white balance, simple and uncluttered composition, modern and sophisticated, high-key with soft shadows, crisp and precise"
    },
    "vibrant-pop": {
        "id": "mood-vibrant-pop",
        "name_ko": "비비드 팝",
        "name_en": "Vibrant Pop",
        "prompt_fragment": "vibrant and bold color palette, highly saturated vivid colors, pop art inspired, bright punchy lighting, playful and energetic mood, strong color contrast, eye-catching and dynamic"
    },
    "japanese-zen": {
        "id": "mood-japanese-zen",
        "name_ko": "일본식 정갈한",
        "name_en": "Japanese Zen",
        "prompt_fragment": "serene Japanese wabi-sabi aesthetic, soft diffused lighting, muted and restrained color palette, zen-like calm and balance, elegant simplicity, subtle earthy tones, meditative and refined atmosphere"
    },
    "street-casual": {
        "id": "mood-street-casual",
        "name_ko": "스트릿 캐주얼",
        "name_en": "Street Casual",
        "prompt_fragment": "natural candid street photography style, available ambient light, casual and authentic atmosphere, lifestyle documentary feel, slightly imperfect and spontaneous, real-world setting"
    },
    "editorial": {
        "id": "mood-editorial",
        "name_ko": "에디토리얼 매거진",
        "name_en": "Editorial Magazine",
        "prompt_fragment": "editorial magazine quality, professional studio lighting setup, polished and styled, high-end food magazine aesthetic, precise and intentional composition, commercial photography grade"
    },
    "cinematic": {
        "id": "mood-cinematic",
        "name_ko": "시네마틱",
        "name_en": "Cinematic",
        "prompt_fragment": "cinematic film still quality, anamorphic lens feel, dramatic directional lighting, teal and orange color grading, movie scene atmosphere, shallow depth of field with beautiful bokeh, epic and storytelling mood"
    }
}

# === 배경 (Background) ===
background = {
    "dark-wood": {
        "id": "bg-dark-wood",
        "name_ko": "어두운 나무 테이블",
        "name_en": "Dark Wood",
        "prompt_fragment": "on a rustic dark wooden table surface, natural wood grain texture visible, warm brown and walnut tones"
    },
    "light-wood": {
        "id": "bg-light-wood",
        "name_ko": "밝은 나무 테이블",
        "name_en": "Light Wood",
        "prompt_fragment": "on a light natural wood table, pale oak or pine surface, bright and airy wooden texture"
    },
    "marble-tile": {
        "id": "bg-marble-tile",
        "name_ko": "대리석/타일",
        "name_en": "Marble / Tile",
        "prompt_fragment": "on a white marble or ceramic tile surface, subtle veining pattern, clean and elegant stone texture"
    },
    "linen-fabric": {
        "id": "bg-linen-fabric",
        "name_ko": "린넨/천",
        "name_en": "Linen / Fabric",
        "prompt_fragment": "on a natural linen cloth or textured fabric, soft wrinkled textile surface, warm and organic feel"
    },
    "concrete": {
        "id": "bg-concrete",
        "name_ko": "콘크리트/시멘트",
        "name_en": "Concrete",
        "prompt_fragment": "on a raw concrete or cement surface, industrial gray texture, minimalist and urban feel"
    },
    "korean-traditional": {
        "id": "bg-korean-traditional",
        "name_ko": "한지/한식 상",
        "name_en": "Korean Traditional",
        "prompt_fragment": "on a traditional Korean wooden soban table or hanji paper surface, authentic Korean dining setting, warm traditional aesthetics"
    },
    "plate-only": {
        "id": "bg-plate-only",
        "name_ko": "접시 위",
        "name_en": "On Plate Only",
        "prompt_fragment": "isolated on a clean plate, minimal background, focus entirely on the dish, negative space around the plate"
    },
    "metal-steel": {
        "id": "bg-metal-steel",
        "name_ko": "스테인리스/메탈",
        "name_en": "Metal / Steel",
        "prompt_fragment": "on a brushed metal or stainless steel surface, industrial kitchen aesthetic, reflective metallic texture"
    },
    "solid-color": {
        "id": "bg-solid-color",
        "name_ko": "컬러 단색 배경",
        "name_en": "Solid Color",
        "prompt_fragment": "on a solid colored backdrop, clean studio background, bold single-color surface for maximum contrast"
    },
    "real-restaurant": {
        "id": "bg-real-restaurant",
        "name_ko": "실제 매장 배경",
        "name_en": "Real Restaurant",
        "prompt_fragment": "in a real restaurant or cafe setting, ambient interior background with soft bokeh, authentic dining environment"
    }
}

# === 앵글 (Angle) ===
angle = {
    "topdown": {
        "id": "angle-topdown",
        "name_ko": "탑다운 / 플랫레이",
        "name_en": "Top-down (90deg)",
        "prompt_fragment": "shot from directly above, top-down flat lay perspective, 90-degree overhead angle, deep depth of field with everything in sharp focus"
    },
    "high-45": {
        "id": "angle-high-45",
        "name_ko": "하이앵글 (45도)",
        "name_en": "High Angle (45deg)",
        "prompt_fragment": "shot from a 45-degree high angle, three-quarter view showing both top and side of the dish, natural dining perspective"
    },
    "eye-level": {
        "id": "angle-eye-level",
        "name_ko": "아이레벨 (정면)",
        "name_en": "Eye Level (0deg)",
        "prompt_fragment": "shot at eye level, straight-on front view, emphasizing the height and layers of the dish, shallow depth of field with beautifully blurred background"
    },
    "low": {
        "id": "angle-low",
        "name_ko": "로우앵글",
        "name_en": "Low Angle (-15deg)",
        "prompt_fragment": "shot from slightly below eye level, low angle looking up at the dish, dramatic and imposing perspective, heroic food presentation"
    },
    "dynamic-tilt": {
        "id": "angle-dynamic-tilt",
        "name_ko": "다이내믹 틸트",
        "name_en": "Dynamic Tilt",
        "prompt_fragment": "shot with a dynamic dutch angle tilt, energetic and unconventional perspective, creative diagonal composition adding movement and excitement"
    }
}

# === 소품 (Props) ===
props = {
    "chopsticks": {
        "id": "prop-chopsticks",
        "name_ko": "젓가락/수저",
        "name_en": "Chopsticks / Spoon",
        "prompt_fragment": "with chopsticks or a spoon placed alongside the dish"
    },
    "napkin": {
        "id": "prop-napkin",
        "name_ko": "냅킨/천",
        "name_en": "Napkin / Fabric",
        "prompt_fragment": "with a folded linen napkin or cloth beside the plate"
    },
    "herbs": {
        "id": "prop-herbs",
        "name_ko": "허브/채소 장식",
        "name_en": "Herbs / Garnish",
        "prompt_fragment": "garnished with fresh herbs and scattered decorative vegetable elements"
    },
    "beverage": {
        "id": "prop-beverage",
        "name_ko": "음료/물잔",
        "name_en": "Beverage / Glass",
        "prompt_fragment": "with a glass of water or beverage placed nearby"
    },
    "condiments": {
        "id": "prop-condiments",
        "name_ko": "양념통/소스",
        "name_en": "Condiments / Sauce",
        "prompt_fragment": "with small sauce bowls or condiment containers arranged around the dish"
    },
    "side-dishes": {
        "id": "prop-side-dishes",
        "name_ko": "사이드 반찬",
        "name_en": "Side Dishes",
        "prompt_fragment": "with small side dishes and banchan arranged around the main plate"
    },
    "hands": {
        "id": "prop-hands",
        "name_ko": "손/사람",
        "name_en": "Human Hands",
        "prompt_fragment": "with a human hand holding or reaching for the dish, adding life and scale"
    },
    "flowers": {
        "id": "prop-flowers",
        "name_ko": "꽃/식물",
        "name_en": "Flowers / Plants",
        "prompt_fragment": "with a small flower arrangement or botanical elements as decoration"
    },
    "empty-dish": {
        "id": "prop-empty-dish",
        "name_ko": "빈 접시/그릇",
        "name_en": "Empty Dishes",
        "prompt_fragment": "with additional empty plates or bowls arranged in the scene"
    },
    "none": {
        "id": "prop-none",
        "name_ko": "없음",
        "name_en": "None",
        "prompt_fragment": ""
    }
}


def save_dim(dim_name, data):
    folder = ROOT / dim_name
    folder.mkdir(parents=True, exist_ok=True)
    for key, val in data.items():
        path = folder / f"{key}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(val, f, ensure_ascii=False, indent=2)


save_dim("mood", mood)
save_dim("background", background)
save_dim("angle", angle)
save_dim("props", props)

total = len(mood) + len(background) + len(angle) + len(props)
print(f"생성 완료: {total}개 프래그먼트")
print(f"  mood: {len(mood)}개")
print(f"  background: {len(background)}개")
print(f"  angle: {len(angle)}개")
print(f"  props: {len(props)}개")
