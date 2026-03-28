#!/usr/bin/env python3
"""
찍다 — 프롬프트 프래그먼트 조합 엔진

차원별 선택값을 조합해서 하나의 생성 프롬프트를 만든다.

사용법 (CLI):
  python scripts/prompt_composer.py --food "비빔밥" --mood bright-airy --bg dark-wood --angle topdown
  python scripts/prompt_composer.py --food "김치찌개" --mood dark-moody --bg marble-tile --angle high-45 --props chopsticks,herbs
  python scripts/prompt_composer.py --food "돈까스" --mood clean-minimal --bg plate-only --angle eye-level --tweaks "소스 많이"

라이브러리로 사용:
  from prompt_composer import compose_prompt
  prompt = compose_prompt("비빔밥", "bright-airy", "dark-wood", "topdown", ["chopsticks"])
"""

import json
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRAGMENTS_DIR = ROOT / "dimensions" / "fragments"
RECIPES_PATH = ROOT / "recipes.json"

# 프래그먼트 캐시
_cache = {}


def load_fragment(dimension, value_key):
    """프래그먼트 JSON 로드 (캐시 사용)"""
    cache_key = f"{dimension}/{value_key}"
    if cache_key in _cache:
        return _cache[cache_key]

    path = FRAGMENTS_DIR / dimension / f"{value_key}.json"
    if not path.exists():
        print(f"  경고: 프래그먼트 없음 — {path}")
        return ""

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fragment = data.get("prompt_fragment", "")
    _cache[cache_key] = fragment
    return fragment


def get_food_description(food_name):
    """recipes.json에서 음식 영문 설명 가져오기"""
    if not RECIPES_PATH.exists():
        return food_name

    try:
        with open(RECIPES_PATH, "r", encoding="utf-8") as f:
            recipes = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return food_name

    # recipes.json 구조에 따라 검색
    if isinstance(recipes, list):
        for recipe in recipes:
            name = recipe.get("name", "") or recipe.get("name_ko", "")
            if food_name in name or name in food_name:
                return recipe.get("description_en", recipe.get("name_en", food_name))
    elif isinstance(recipes, dict):
        for key, recipe in recipes.items():
            if isinstance(recipe, dict):
                name = recipe.get("name", "") or recipe.get("name_ko", "")
                if food_name in str(name) or str(name) in food_name:
                    return recipe.get("description_en", recipe.get("name_en", food_name))

    return food_name


def strip_dimension_prefix(value_id):
    """차원 ID에서 프리픽스 제거 → 파일명으로 변환
    예: mood-bright-airy → bright-airy, bg-dark-wood → dark-wood
    """
    prefixes = ["mood-", "bg-", "angle-", "prop-"]
    for prefix in prefixes:
        if value_id.startswith(prefix):
            return value_id[len(prefix):]
    return value_id


def compose_prompt(
    food_name,
    mood,
    background,
    angle,
    props=None,
    tweaks="",
):
    """
    차원별 프래그먼트를 조합해서 최종 프롬프트 생성

    Args:
        food_name: "비빔밥" 또는 "kimchi jjigae"
        mood: "bright-airy" 또는 "mood-bright-airy"
        background: "dark-wood" 또는 "bg-dark-wood"
        angle: "topdown" 또는 "angle-topdown"
        props: ["chopsticks", "herbs"] 또는 ["prop-chopsticks"]
        tweaks: "소스 많이, 김치 조각 크게" (자유 입력)

    Returns:
        str: 조합된 최종 프롬프트
    """
    if props is None:
        props = []

    # 프리픽스 제거 (ID 형식으로 들어올 수 있음)
    mood_key = strip_dimension_prefix(mood)
    bg_key = strip_dimension_prefix(background)
    angle_key = strip_dimension_prefix(angle)
    prop_keys = [strip_dimension_prefix(p) for p in props]

    # 음식 영문 설명
    food_desc = get_food_description(food_name)

    # 프래그먼트 로드
    mood_frag = load_fragment("mood", mood_key)
    bg_frag = load_fragment("background", bg_key)
    angle_frag = load_fragment("angle", angle_key)
    prop_frags = [load_fragment("props", p) for p in prop_keys if p != "none"]
    # 빈 문자열 제거
    prop_frags = [f for f in prop_frags if f]

    # 조합
    parts = [
        f"Professional Korean food photography of {food_desc}",
        mood_frag,
        bg_frag,
        angle_frag,
    ]

    if prop_frags:
        parts.extend(prop_frags)

    if tweaks:
        parts.append(f"additional details: {tweaks}")

    # 품질 접미사
    parts.append("editorial food magazine quality, ultra detailed, 8K resolution")

    # 조합 (빈 파트 제거)
    prompt = ", ".join(p for p in parts if p)

    return prompt


def main():
    parser = argparse.ArgumentParser(description="찍다 — 프롬프트 조합 엔진")
    parser.add_argument("--food", required=True, help="음식 이름 (예: 비빔밥)")
    parser.add_argument("--mood", required=True, help="분위기 (예: bright-airy)")
    parser.add_argument("--bg", required=True, help="배경 (예: dark-wood)")
    parser.add_argument("--angle", required=True, help="앵글 (예: topdown)")
    parser.add_argument("--props", default="", help="소품 (쉼표 구분, 예: chopsticks,herbs)")
    parser.add_argument("--tweaks", default="", help="미세조정 텍스트")
    parser.add_argument("--demo", action="store_true", help="대표 조합 10개 데모")
    args = parser.parse_args()

    if args.demo:
        run_demo()
        return

    props = [p.strip() for p in args.props.split(",") if p.strip()]

    prompt = compose_prompt(
        food_name=args.food,
        mood=args.mood,
        background=args.bg,
        angle=args.angle,
        props=props,
        tweaks=args.tweaks,
    )

    print(f"\n{'=' * 60}")
    print(f"  음식: {args.food}")
    print(f"  분위기: {args.mood}")
    print(f"  배경: {args.bg}")
    print(f"  앵글: {args.angle}")
    print(f"  소품: {args.props or '없음'}")
    if args.tweaks:
        print(f"  미세조정: {args.tweaks}")
    print(f"{'=' * 60}")
    print(f"\n{prompt}")
    print(f"\n  글자 수: {len(prompt)}")


def run_demo():
    """대표 조합 10개 데모"""
    combos = [
        ("비빔밥", "bright-airy", "marble-tile", "topdown", ["chopsticks", "herbs"], ""),
        ("김치찌개", "warm-rustic", "dark-wood", "high-45", ["side-dishes"], ""),
        ("돈까스", "clean-minimal", "plate-only", "eye-level", [], ""),
        ("불고기", "dark-moody", "dark-wood", "high-45", ["condiments"], ""),
        ("떡볶이", "vibrant-pop", "solid-color", "topdown", ["beverage"], ""),
        ("초밥", "japanese-zen", "light-wood", "high-45", ["chopsticks"], ""),
        ("파스타", "film-vintage", "linen-fabric", "eye-level", ["napkin", "beverage"], ""),
        ("삼겹살", "street-casual", "real-restaurant", "high-45", ["hands"], ""),
        ("갈비탕", "editorial", "marble-tile", "high-45", ["side-dishes", "condiments"], ""),
        ("냉면", "cinematic", "concrete", "eye-level", [], "얼음 위에 고명"),
    ]

    for i, (food, mood, bg, angle, props, tweaks) in enumerate(combos, 1):
        prompt = compose_prompt(food, mood, bg, angle, props, tweaks)
        props_str = ", ".join(props) if props else "없음"
        print(f"\n{'─' * 60}")
        print(f"  [{i}] {food} | {mood} + {bg} + {angle} | 소품: {props_str}")
        print(f"{'─' * 60}")
        print(f"  {prompt[:200]}...")
        print(f"  (총 {len(prompt)}자)")


if __name__ == "__main__":
    main()
