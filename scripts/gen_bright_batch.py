#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-genai>=1.0.0",
#     "Pillow>=10.0.0",
# ]
# ///
"""
밝은 스타일 음식 사진 일괄 생성 스크립트.
6개 메뉴 x 5장 = 30장 생성.
"""

import time
import subprocess
from pathlib import Path

# 프로젝트 루트
ROOT = Path("c:/claudcode-work/chef-photo/밝은스타일_생성")

# nano-banana-pro 스크립트 경로
SCRIPT = Path.home() / ".claude" / "skills" / "nano-banana-pro" / "scripts" / "generate_image.py"

# 밝은 스타일 공통 프롬프트
def style_base(background):
    """배경 프롬프트를 포함한 스타일 베이스 생성"""
    return (
        "hard left-side directional lighting, "
        "strong defined shadows, bright highlights, graphic shadow patterns. "
        "Color: neutral-warm ~5450K, high saturation vivid colors, "
        "rich deep blacks, no film grain, clean digital look. "
        "Lens: 71mm equivalent, deep depth of field, razor-sharp focus across entire frame. "
        f"Setting: {background}, "
        "modern minimal ceramic plates, fresh garnishes and colorful props. "
        "Mood: bright & cheerful, vibrant, fresh, energetic, modern food styling. "
        "High detail, Instagram-editorial food magazine quality, 8K resolution."
    )

# 앵글 프리셋 (1~5번)
ANGLES = [
    ("탑뷰", "shot from directly overhead (flat lay, top-down 90 degrees), symmetrical composition"),
    ("45도", "shot from 45-degree high angle"),
    ("아이레벨", "shot from eye-level angle (0-10 degrees), emphasizing height and volume of food"),
    ("30도", "shot from 30-degree low-high angle showing depth and layers"),
    ("60도", "shot from 60-degree high angle, showing full food composition and arrangement"),
]

# 메뉴 정의 (이름, 영문 설명, 배경 프롬프트)
MENUS = [
    ("김치찌개", "Korean kimchi stew (kimchi-jjigae) with tofu, pork, and bubbling red broth in a hot stone pot",
     "clean matte white surface, soft pastel pink linen napkin, minimal props"),
    ("돈까스", "Japanese-style tonkatsu (deep-fried breaded pork cutlet) with shredded cabbage, rice, and tonkatsu sauce",
     "light natural bamboo mat, clean beige ceramic plate, simple bright background"),
    ("치아바타샌드위치", "Italian ciabatta sandwich with fresh mozzarella, tomatoes, basil, prosciutto, and olive oil",
     "pale marble countertop, fresh herb garnish scattered around, bright natural light"),
    ("비빔밥", "Korean bibimbap with colorful vegetables, gochujang sauce, fried egg on top, served in a bowl",
     "warm light wood cutting board, natural linen cloth, clean bright background"),
    ("떡볶이", "Korean tteokbokki (spicy rice cakes) with fish cakes in gochujang sauce, topped with green onions",
     "kraft paper sheet, bright solid warm yellow or clean white background"),
    ("치킨", "Korean fried chicken (yangnyeom chicken) with sweet and spicy glaze, sesame seeds, and pickled radish",
     "kraft paper sheet, bright solid warm yellow or clean white background"),
]

DATE = "2026-03-14"

def generate_one(menu_kr, menu_en, background, angle_name, angle_prompt, idx):
    """1장 생성"""
    folder = ROOT / f"{menu_kr}_{DATE}"
    filename = folder / f"{menu_kr}-{angle_name}-{idx:02d}.png"

    if filename.exists():
        print(f"  [SKIP] {filename.name} (already exists)")
        return True

    prompt = f"Bright, vibrant food photography of {menu_en}. {angle_prompt}, {style_base(background)}"

    cmd = [
        "uv", "run", str(SCRIPT),
        "--prompt", prompt,
        "--filename", str(filename),
        "--resolution", "2K",
    ]

    print(f"  [{idx}] {menu_kr} - {angle_name}...", end=" ", flush=True)
    t0 = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        elapsed = time.time() - t0
        if result.returncode == 0:
            print(f"OK ({elapsed:.0f}s)")
            return True
        else:
            print(f"FAIL ({result.stderr[:100]})")
            return False
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        return False
    except Exception as e:
        print(f"ERROR ({e})")
        return False


def main():
    total = len(MENUS) * len(ANGLES)
    success = 0
    fail = 0
    start = time.time()

    for menu_kr, menu_en, background in MENUS:
        print(f"\n=== {menu_kr} (5장) ===")
        for idx, (angle_name, angle_prompt) in enumerate(ANGLES, 1):
            if generate_one(menu_kr, menu_en, background, angle_name, angle_prompt, idx):
                success += 1
            else:
                fail += 1
            time.sleep(2)  # API rate limit

    elapsed = time.time() - start
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    print(f"\n{'='*50}")
    print(f"[완료] {success}/{total} 성공, {fail} 실패")
    print(f"소요 시간: {minutes}분 {seconds}초")
    print(f"저장 위치: {ROOT}")


if __name__ == "__main__":
    main()
