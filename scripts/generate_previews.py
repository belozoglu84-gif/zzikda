#!/usr/bin/env python3
"""
찍다 — Phase 4: 프리뷰 이미지 라이브러리 생성

차원별 프리뷰 사진을 AI로 미리 생성해서 서비스 UI에서 보여줄 템플릿 이미지를 만든다.
대표 음식(비빔밥)으로 통일해서 스타일 차이만 보이게 한다.

사용법:
  python scripts/generate_previews.py --step mood          # 분위기 프리뷰 10장
  python scripts/generate_previews.py --step background     # 배경 프리뷰 (분위기별 × 10)
  python scripts/generate_previews.py --step angle          # 앵글 프리뷰
  python scripts/generate_previews.py --step all            # 전체 생성
  python scripts/generate_previews.py --dry-run             # 프롬프트만 출력 (API 호출 안 함)
"""

import argparse
import json
import time
import sys
import io
import os
from pathlib import Path
from datetime import datetime

# Windows 콘솔 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from prompt_composer import compose_prompt

# 기본 설정
DEFAULT_FOOD = "비빔밥"
PREVIEW_DIR = ROOT / "dimensions" / "previews"
META_PATH = ROOT / "dimensions" / "preview_meta.json"

# 인기 분위기 상위 5개 (배경/앵글 프리뷰에 사용)
TOP_MOODS = ["bright-airy", "warm-rustic", "dark-moody", "clean-minimal", "vibrant-pop"]

# 인기 조합 상위 20개 (앵글 프리뷰에 사용)
TOP_COMBOS = [
    ("bright-airy", "marble-tile"),
    ("bright-airy", "light-wood"),
    ("bright-airy", "linen-fabric"),
    ("bright-airy", "solid-color"),
    ("warm-rustic", "dark-wood"),
    ("warm-rustic", "linen-fabric"),
    ("warm-rustic", "korean-traditional"),
    ("warm-rustic", "marble-tile"),
    ("dark-moody", "dark-wood"),
    ("dark-moody", "concrete"),
    ("dark-moody", "metal-steel"),
    ("dark-moody", "marble-tile"),
    ("clean-minimal", "plate-only"),
    ("clean-minimal", "marble-tile"),
    ("clean-minimal", "solid-color"),
    ("clean-minimal", "concrete"),
    ("vibrant-pop", "solid-color"),
    ("vibrant-pop", "marble-tile"),
    ("vibrant-pop", "concrete"),
    ("vibrant-pop", "light-wood"),
]

ALL_MOODS = [
    "bright-airy", "warm-rustic", "dark-moody", "film-vintage",
    "clean-minimal", "vibrant-pop", "japanese-zen", "street-casual",
    "editorial", "cinematic"
]
ALL_BACKGROUNDS = [
    "dark-wood", "light-wood", "marble-tile", "linen-fabric", "concrete",
    "korean-traditional", "plate-only", "metal-steel", "solid-color", "real-restaurant"
]
ALL_ANGLES = ["topdown", "high-45", "eye-level", "low", "dynamic-tilt"]


def load_api_key():
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("GEMINI_IMAGE_API_KEY="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("GEMINI_IMAGE_API_KEY", "")


def generate_image(client, prompt, max_retries=3):
    """나노바나나프로로 이미지 1장 생성"""
    from google.genai import types

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    temperature=1.0,
                ),
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    return part.inline_data.data, part.inline_data.mime_type
            print(f"    경고: 이미지 없음, 재시도 {attempt + 1}/{max_retries}")
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                wait = 60
            elif "503" in err_msg or "UNAVAILABLE" in err_msg:
                wait = 30
            else:
                wait = 10
            print(f"    오류: {err_msg[:80]}... ({wait}초 대기)")
            if attempt < max_retries - 1:
                time.sleep(wait)

    return None, None


def save_preview(data, mime_type, output_path, prompt, meta):
    """프리뷰 이미지 저장 + 메타데이터 기록"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ext = ".png" if "png" in mime_type else ".jpg"
    final_path = output_path.with_suffix(ext)

    with open(final_path, "wb") as f:
        f.write(data)

    # 메타데이터 기록
    meta[str(final_path.relative_to(ROOT))] = {
        "prompt": prompt,
        "generated_at": datetime.now().isoformat(),
        "food": DEFAULT_FOOD,
    }

    return final_path


def generate_mood_previews(client, dry_run, meta):
    """Step 1: 분위기 프리뷰 10장"""
    print("\n=== Step 1: 분위기 프리뷰 (10장) ===")
    count = 0

    for mood in ALL_MOODS:
        output = PREVIEW_DIR / "mood" / f"{mood}"
        prompt = compose_prompt(DEFAULT_FOOD, mood, "marble-tile", "high-45")

        if dry_run:
            print(f"  [{mood}] {prompt[:100]}...")
            count += 1
            continue

        print(f"  생성 중: {mood}...", end=" ", flush=True)
        data, mime = generate_image(client, prompt)
        if data:
            path = save_preview(data, mime, output, prompt, meta)
            print(f"저장 완료 ({len(data)//1024}KB)")
            count += 1
            time.sleep(5)  # API 쿨다운
        else:
            print("실패")

    print(f"  → 분위기 프리뷰: {count}/10장")
    return count


def generate_background_previews(client, dry_run, meta):
    """Step 2: 배경 프리뷰 (인기 분위기 5개 × 배경 10개 = 50장)"""
    print("\n=== Step 2: 배경 프리뷰 (최대 50장) ===")
    count = 0

    for mood in TOP_MOODS:
        for bg in ALL_BACKGROUNDS:
            output = PREVIEW_DIR / "background" / mood / f"{bg}"
            prompt = compose_prompt(DEFAULT_FOOD, mood, bg, "high-45")

            if dry_run:
                print(f"  [{mood}/{bg}] {prompt[:80]}...")
                count += 1
                continue

            print(f"  생성 중: {mood}/{bg}...", end=" ", flush=True)
            data, mime = generate_image(client, prompt)
            if data:
                path = save_preview(data, mime, output, prompt, meta)
                print(f"저장 완료 ({len(data)//1024}KB)")
                count += 1
                time.sleep(5)
            else:
                print("실패")

    print(f"  → 배경 프리뷰: {count}/50장")
    return count


def generate_angle_previews(client, dry_run, meta):
    """Step 3: 앵글 프리뷰 (인기 조합 20개 × 앵글 5개 = 100장)"""
    print("\n=== Step 3: 앵글 프리뷰 (최대 100장) ===")
    count = 0

    for mood, bg in TOP_COMBOS:
        for angle in ALL_ANGLES:
            output = PREVIEW_DIR / "angle" / f"{mood}_{bg}" / f"{angle}"
            prompt = compose_prompt(DEFAULT_FOOD, mood, bg, angle)

            if dry_run:
                print(f"  [{mood}/{bg}/{angle}] (건너뜀 — dry-run)")
                count += 1
                continue

            print(f"  생성 중: {mood}/{bg}/{angle}...", end=" ", flush=True)
            data, mime = generate_image(client, prompt)
            if data:
                path = save_preview(data, mime, output, prompt, meta)
                print(f"저장 완료 ({len(data)//1024}KB)")
                count += 1
                time.sleep(5)
            else:
                print("실패")

    print(f"  → 앵글 프리뷰: {count}/100장")
    return count


def main():
    parser = argparse.ArgumentParser(description="찍다 — 프리뷰 이미지 생성")
    parser.add_argument("--step", choices=["mood", "background", "angle", "all"],
                        default="mood", help="생성 단계 (기본: mood)")
    parser.add_argument("--dry-run", action="store_true", help="프롬프트만 출력, API 호출 안 함")
    args = parser.parse_args()

    # 메타데이터 로드
    meta = {}
    if META_PATH.exists():
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)

    client = None
    if not args.dry_run:
        api_key = load_api_key()
        if not api_key:
            print("오류: GEMINI_IMAGE_API_KEY를 .env에 설정해주세요")
            return
        from google import genai
        client = genai.Client(api_key=api_key)

    total = 0
    steps = [args.step] if args.step != "all" else ["mood", "background", "angle"]

    for step in steps:
        if step == "mood":
            total += generate_mood_previews(client, args.dry_run, meta)
        elif step == "background":
            total += generate_background_previews(client, args.dry_run, meta)
        elif step == "angle":
            total += generate_angle_previews(client, args.dry_run, meta)

    # 메타데이터 저장
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    mode = "dry-run" if args.dry_run else "생성"
    print(f"\n완료! 총 {total}장 {mode}")


if __name__ == "__main__":
    main()
