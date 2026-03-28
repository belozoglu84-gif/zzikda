#!/usr/bin/env python3
"""
찍다 — Phase 5: 이미지 참조 생성 파이프라인

사용자 원본 사진 + 차원 선택 → 최종 메뉴사진 생성.
나노바나나프로의 이미지 참조(image-to-image) 기능을 활용한다.

사용법:
  python scripts/generate_with_reference.py --input photo.jpg --food "비빔밥" --mood bright-airy --bg marble-tile --angle topdown
  python scripts/generate_with_reference.py --input photo.jpg --food "김치찌개" --mood dark-moody --bg dark-wood --angle high-45 --props chopsticks,herbs
  python scripts/generate_with_reference.py --input photo.jpg --food "돈까스" --mood clean-minimal --bg plate-only --angle eye-level --tweaks "소스 많이"
  python scripts/generate_with_reference.py --dry-run --input photo.jpg --food "비빔밥" --mood bright-airy --bg marble-tile --angle topdown
"""

import argparse
import json
import time
import sys
import io
import os
import base64
from pathlib import Path
from datetime import datetime

# Windows 콘솔 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from prompt_composer import compose_prompt


def load_api_key():
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("GEMINI_IMAGE_API_KEY="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("GEMINI_IMAGE_API_KEY", "")


def load_image_as_part(image_path):
    """이미지를 Gemini API Part 형식으로 로드"""
    from google.genai import types

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"이미지 파일 없음: {image_path}")

    # MIME 타입 결정
    ext = path.suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime_type = mime_map.get(ext, "image/jpeg")

    # 이미지 읽기
    image_data = path.read_bytes()

    return types.Part.from_bytes(data=image_data, mime_type=mime_type)


def generate_with_reference(
    client,
    reference_image_path,
    food_name,
    mood,
    background,
    angle,
    props=None,
    tweaks="",
    max_retries=3,
):
    """
    사용자 원본 사진을 참조해서 선택한 스타일로 재생성

    Returns: (이미지 바이트, MIME 타입, 사용된 프롬프트)
    """
    from google.genai import types

    if props is None:
        props = []

    # 프롬프트 조합
    prompt = compose_prompt(food_name, mood, background, angle, props, tweaks)

    # 참조 이미지 로드
    ref_image = load_image_as_part(reference_image_path)

    # 지시문 (참조 이미지 + 스타일 프롬프트)
    instruction = (
        f"이 음식 사진을 참고해서 같은 음식을 다음 스타일로 전문가급 사진으로 재생성해주세요. "
        f"원본 음식의 형태와 구성을 유지하되, 조명/배경/앵글/분위기만 변경합니다:\n\n"
        f"{prompt}"
    )

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[ref_image, instruction],
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    temperature=0.8,
                ),
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    return part.inline_data.data, part.inline_data.mime_type, prompt

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

    return None, None, prompt


def generate_text_only(
    client,
    food_name,
    mood,
    background,
    angle,
    props=None,
    tweaks="",
    max_retries=3,
):
    """
    참조 이미지 없이 텍스트 프롬프트만으로 생성 (프리뷰 모드)

    Returns: (이미지 바이트, MIME 타입, 사용된 프롬프트)
    """
    from google.genai import types

    if props is None:
        props = []

    prompt = compose_prompt(food_name, mood, background, angle, props, tweaks)

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
                    return part.inline_data.data, part.inline_data.mime_type, prompt

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

    return None, None, prompt


def main():
    parser = argparse.ArgumentParser(description="찍다 — 참조 이미지 기반 사진 생성")
    parser.add_argument("--input", type=str, help="참조 이미지 경로 (없으면 텍스트만으로 생성)")
    parser.add_argument("--food", required=True, help="음식 이름 (예: 비빔밥)")
    parser.add_argument("--mood", required=True, help="분위기 (예: bright-airy)")
    parser.add_argument("--bg", required=True, help="배경 (예: dark-wood)")
    parser.add_argument("--angle", required=True, help="앵글 (예: topdown)")
    parser.add_argument("--props", default="", help="소품 (쉼표 구분)")
    parser.add_argument("--tweaks", default="", help="미세조정 텍스트")
    parser.add_argument("--output", type=str, default=None, help="출력 파일 경로")
    parser.add_argument("--dry-run", action="store_true", help="프롬프트만 출력")
    args = parser.parse_args()

    props = [p.strip() for p in args.props.split(",") if p.strip()]

    # 프롬프트 미리보기
    prompt = compose_prompt(args.food, args.mood, args.bg, args.angle, props, args.tweaks)

    print(f"\n{'=' * 60}")
    print(f"  음식: {args.food}")
    print(f"  분위기: {args.mood}")
    print(f"  배경: {args.bg}")
    print(f"  앵글: {args.angle}")
    print(f"  소품: {args.props or '없음'}")
    print(f"  참조: {args.input or '없음 (텍스트만)'}")
    if args.tweaks:
        print(f"  미세조정: {args.tweaks}")
    print(f"{'=' * 60}")
    print(f"\n프롬프트:\n  {prompt[:200]}...")
    print(f"  ({len(prompt)}자)")

    if args.dry_run:
        print(f"\n전체 프롬프트:\n{prompt}")
        print("\n(dry-run 모드 — API 호출 안 함)")
        return

    # API 클라이언트
    api_key = load_api_key()
    if not api_key:
        print("\n오류: GEMINI_IMAGE_API_KEY를 .env에 설정해주세요")
        return

    from google import genai
    client = genai.Client(api_key=api_key)

    # 생성
    print("\n이미지 생성 중...", flush=True)

    if args.input:
        data, mime, used_prompt = generate_with_reference(
            client, args.input, args.food, args.mood, args.bg, args.angle, props, args.tweaks
        )
    else:
        data, mime, used_prompt = generate_text_only(
            client, args.food, args.mood, args.bg, args.angle, props, args.tweaks
        )

    if not data:
        print("\n이미지 생성 실패")
        return

    # 저장
    ext = ".png" if "png" in mime else ".jpg"
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = ROOT / "생성결과" / "차원조합"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{args.food}_{args.mood}_{args.bg}_{args.angle}_{timestamp}{ext}"
        output_path = output_dir / filename

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(data)

    print(f"\n저장 완료: {output_path}")
    print(f"  파일 크기: {len(data) // 1024}KB")

    # 메타데이터 저장
    meta_path = output_path.with_suffix(".json")
    meta = {
        "food": args.food,
        "mood": args.mood,
        "background": args.bg,
        "angle": args.angle,
        "props": props,
        "tweaks": args.tweaks,
        "reference_image": args.input,
        "prompt": used_prompt,
        "generated_at": datetime.now().isoformat(),
        "output_path": str(output_path),
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"  메타데이터: {meta_path}")


if __name__ == "__main__":
    main()
