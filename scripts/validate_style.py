"""
validate_style.py - 통합 스타일 프로필의 품질 검증

통합 프로필의 unified_nano_banana_prompt로 테스트 이미지를 생성하여
원본 스타일과 비교 검증한다.

사용법:
    uv run validate_style.py --profile clean-minimal_unified_profile.json
    uv run validate_style.py --profile warm-rustic_unified_profile.json --count 5
    uv run validate_style.py --profile 김현경_unified_profile.json --foods "비빔밥,파스타,샐러드"
"""

# /// script
# requires-python = ">=3.10"
# dependencies = ["rich>=13.0.0"]
# ///

import json
import sys
import time
import argparse
import subprocess
from pathlib import Path

from rich.console import Console

console = Console()

# 기본 테스트 음식 목록 (다양한 종류)
DEFAULT_FOODS = [
    {
        "name": "김치찌개",
        "desc": "Kimchi Jjigae (Korean kimchi stew) in a traditional black earthenware ttukbaegi pot. Bubbling red broth with tofu cubes, sliced pork belly, green onions, kimchi pieces.",
        "setting": "Dark wooden table, metal spoon beside pot, small rice bowl."
    },
    {
        "name": "크림파스타",
        "desc": "Creamy garlic shrimp pasta in a wide ceramic bowl. Al dente fettuccine in white cream sauce, grilled shrimp, fresh basil, parmesan shavings, black pepper.",
        "setting": "Neutral stone surface, linen napkin, fork resting on plate edge."
    },
    {
        "name": "연어포케",
        "desc": "Fresh salmon poke bowl. Sushi-grade salmon cubes, avocado slices, edamame, cucumber, pickled ginger, sesame seeds, soy dressing. On a bed of sushi rice.",
        "setting": "Light ceramic bowl, wooden chopsticks, clean modern table surface."
    },
    {
        "name": "티라미수",
        "desc": "Classic tiramisu dessert in a glass cup, layered mascarpone cream and coffee-soaked ladyfingers. Dusted with cocoa powder on top. Cross-section visible through glass.",
        "setting": "Marble surface, small espresso cup beside, vintage dessert spoon."
    },
    {
        "name": "불고기",
        "desc": "Korean bulgogi (marinated beef) sizzling on a hot plate. Thinly sliced tender beef, caramelized onions, green pepper, mushrooms, sesame garnish. Glistening glaze.",
        "setting": "Traditional Korean table setting, lettuce wraps on the side, dipping sauce."
    },
]

SKILL_SCRIPT = Path.home() / ".claude/skills/nano-banana-pro/scripts/generate_image.py"


def generate_test_image(food: dict, style_prompt: str, output_dir: Path, index: int) -> bool:
    """통합 프롬프트로 테스트 이미지 생성"""
    filename = output_dir / f"test_{index:02d}_{food['name']}.png"

    if filename.exists():
        console.print(f"  [{index}] {food['name']} — 이미 존재, 건너뜀")
        return True

    # 음식 설명 + 세팅 + 스타일 프롬프트 결합
    prompt = f"{food['desc']} {food['setting']} {style_prompt}"

    cmd = [
        "uv", "run", str(SKILL_SCRIPT),
        "--prompt", prompt,
        "--filename", str(filename),
        "--resolution", "2K"
    ]

    console.print(f"  [{index}] {food['name']} 생성 중...", end=" ")

    result = subprocess.run(
        cmd, capture_output=True, text=True,
        encoding="utf-8", errors="replace"
    )

    if filename.exists():
        console.print("[green]성공[/green]")
        return True
    else:
        error_msg = result.stderr[:200] if result.stderr else "알 수 없는 오류"
        console.print(f"[red]실패: {error_msg}[/red]")
        return False


def main():
    parser = argparse.ArgumentParser(description="통합 스타일 프로필 검증")
    parser.add_argument("--profile", required=True, help="통합 프로필 JSON 경로")
    parser.add_argument("--count", type=int, default=3, help="생성할 테스트 이미지 수 (기본: 3, 최대: 5)")
    parser.add_argument("--foods", type=str, help="테스트 음식 목록 (쉼표 구분, 예: '비빔밥,파스타,샐러드')")
    parser.add_argument("--output-dir", type=str, help="출력 폴더 (기본: 검증_{프로필명})")
    args = parser.parse_args()

    profile_path = Path(args.profile)
    if not profile_path.exists():
        console.print(f"[red]오류: 프로필 파일이 없습니다: {profile_path}[/red]")
        sys.exit(1)

    # nano-banana-pro 스킬 확인
    if not SKILL_SCRIPT.exists():
        console.print(f"[red]오류: nano-banana-pro 스킬이 설치되어 있지 않습니다[/red]")
        console.print(f"  경로: {SKILL_SCRIPT}")
        sys.exit(1)

    # 프로필 로드
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    style_prompt = profile.get("unified_nano_banana_prompt", "")

    if not style_prompt:
        console.print("[red]오류: 프로필에 unified_nano_banana_prompt가 없습니다[/red]")
        sys.exit(1)

    # 스타일명 추출
    usage_guide = profile.get("usage_guide", {})
    style_name = usage_guide.get("description", profile_path.stem)

    # 테스트 음식 선택
    count = min(args.count, 5)

    if args.foods:
        # 사용자 지정 음식
        food_names = [f.strip() for f in args.foods.split(",")]
        foods = []
        for name in food_names[:count]:
            foods.append({
                "name": name,
                "desc": f"Professional food photography of {name}, beautifully plated and styled.",
                "setting": "Elegant table setting with complementary tableware and props."
            })
    else:
        foods = DEFAULT_FOODS[:count]

    # 출력 폴더
    output_dir = Path(args.output_dir or f"검증_{profile_path.stem}")
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n{'='*60}")
    console.print(f" [bold]스타일 검증[/bold]: {style_name}")
    console.print(f" 프로필: {profile_path}")
    console.print(f" 테스트 이미지: {count}장")
    console.print(f" 저장: {output_dir}")
    console.print(f"{'='*60}")

    # 프롬프트 미리보기
    console.print(f"\n[dim]프롬프트 (처음 200자):[/dim]")
    console.print(f"[dim]{style_prompt[:200]}...[/dim]\n")

    # 이미지 생성
    success = 0
    for i, food in enumerate(foods, 1):
        ok = generate_test_image(food, style_prompt, output_dir, i)
        if ok:
            success += 1
        time.sleep(3)  # API rate limit

    # 결과
    console.print(f"\n{'='*60}")
    console.print(f" [bold]검증 결과[/bold]")
    console.print(f"  생성 성공: {success}/{count}장")
    console.print(f"  저장 폴더: {output_dir}")
    console.print(f"{'='*60}")

    if success > 0:
        console.print(f"\n[green]검증 이미지가 생성되었습니다.[/green]")
        console.print(f"생성된 이미지를 원본 스타일과 비교하여 품질을 확인하세요.")
        console.print(f"\n파일 목록:")
        for f in sorted(output_dir.glob("test_*.png")):
            console.print(f"  {f.name}")
    else:
        console.print(f"\n[red]이미지 생성에 실패했습니다. API 키와 스킬 설치를 확인하세요.[/red]")


if __name__ == "__main__":
    main()
