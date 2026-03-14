"""
filter_photos.py - 수집된 사진에서 음식사진만 필터링

Gemini Flash로 빠른 1차 필터링:
  1) 음식이 주 피사체인지 확인 (음식 없으면 즉시 제외)
  2) 원하는 스타일에 부합하는지 점수 (1~10)
  3) 사진 품질 점수 (1~10)

사용법:
    uv run filter_photos.py --folder 수집_clean-minimal --style clean-minimal
    uv run filter_photos.py --folder 수집_warm-rustic --style warm-rustic --min-score 6
    uv run filter_photos.py --folder 수집_vibrant-pop --style vibrant-pop --dry-run
"""

# /// script
# requires-python = ">=3.10"
# dependencies = ["google-genai>=1.0.0", "Pillow>=10.0.0", "rich>=13.0.0"]
# ///

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

from google import genai
from PIL import Image
from rich.console import Console
from rich.table import Table

console = Console()

# 이미지 확장자
IMAGE_EXTENSIONS = {".jpeg", ".jpg", ".png", ".webp"}

# 스타일 설명 (필터링 판단용)
STYLE_DESCRIPTIONS = {
    "clean-minimal": "흰 배경 또는 밝고 깨끗한 배경, 최소한의 소품, 높은 선명도, 심플한 플레이팅. 배달앱이나 메뉴판에 적합한 깔끔한 음식 사진.",
    "warm-rustic": "나무 테이블이나 천 소재 배경, 따뜻한 색온도, 킨포크 감성, 가정식 느낌. 자연스럽고 따뜻한 분위기의 음식 사진.",
    "vibrant-pop": "높은 채도, 선명하고 강렬한 색감, 에너지 넘치는 느낌. SNS에서 눈에 띄는 화려한 음식 사진.",
    "bright-airy": "밝은 배경, 자연광 느낌, 높은 명도, 에어리한 분위기. 카페나 브런치 메뉴에 적합한 밝은 음식 사진.",
    "dark-moody": "어두운 배경, 드라마틱한 조명, 낮은 채도, 무디한 분위기. 고급 레스토랑이나 바에 적합한 분위기 있는 음식 사진.",
    "film-vintage": "필름 그레인, 바랜 색감, 레트로 느낌. 아날로그 감성의 빈티지 음식 사진.",
    "overhead-editorial": "탑다운(위에서 내려다보는) 구도, 잡지급 스타일링, 접시와 소품이 잘 배치된 플랫레이 음식 사진.",
    "street-casual": "실제 식당이나 길거리 현장, 자연스러운 연출, 캐주얼한 분위기. 맛집 리뷰에 어울리는 현장감 있는 음식 사진.",
}


def create_filter_prompt(style: str) -> str:
    """필터링용 프롬프트 생성"""
    style_desc = STYLE_DESCRIPTIONS.get(style, "전문적인 음식 사진")

    return f"""이 사진을 평가해주세요. 반드시 아래 JSON 형식으로만 답해주세요.

평가 기준:
1. is_food: 음식이 사진의 주 피사체인가? (true/false)
   - 음식이 화면의 중심에 있고 주제인 경우만 true
   - 풍경, 하늘, 건물, 사람, 동물, 식물만 있는 사진은 false
   - 음식이 아주 작게 보이거나 부수적인 경우도 false

2. style_score: 아래 스타일에 얼마나 부합하는가? (1~10)
   목표 스타일: "{style_desc}"
   - 10: 완벽하게 부합
   - 7~9: 대체로 부합
   - 4~6: 부분적으로 부합
   - 1~3: 스타일이 다름

3. quality_score: 사진 품질 (1~10)
   - 해상도, 선명도, 전문성 수준
   - 10: 프로 사진작가 수준
   - 5: 보통
   - 1~3: 흐릿하거나 저품질

4. food_type: 음식 종류 (예: "파스타", "샐러드", "한식", "디저트" 등, 음식이 아니면 "없음")

JSON 형식:
{{"is_food": true, "style_score": 8, "quality_score": 7, "food_type": "파스타"}}"""


def filter_image(client: genai.Client, image_path: Path, style: str) -> dict | None:
    """Gemini Flash로 이미지 필터링"""
    try:
        img = Image.open(image_path)

        # 필터링용으로 이미지 축소 (API 비용 절감)
        max_size = 800
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        prompt = create_filter_prompt(style)

        response = client.models.generate_content(
            model="gemini-2.0-flash",  # Flash 모델로 빠르게 필터링
            contents=[prompt, img],
            config={"temperature": 0.1},
        )

        # JSON 파싱
        text = response.text.strip()
        # 코드 블록 제거
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        result = json.loads(text)
        return result

    except json.JSONDecodeError:
        console.print(f"  [yellow]JSON 파싱 실패: {image_path.name}[/yellow]")
        return None
    except Exception as e:
        console.print(f"  [red]오류: {image_path.name} — {e}[/red]")
        return None


def main():
    parser = argparse.ArgumentParser(description="수집된 사진에서 음식사진만 필터링")
    parser.add_argument("--folder", required=True, help="수집된 사진 폴더")
    parser.add_argument("--style", required=True, help="스타일 코드 (예: clean-minimal)")
    parser.add_argument("--min-score", type=int, default=5, help="최소 스타일+품질 평균 점수 (기본: 5)")
    parser.add_argument("--output-dir", type=str, help="필터링 결과 저장 폴더 (기본: 필터링_{스타일})")
    parser.add_argument("--delay", type=float, default=1.0, help="API 호출 간격 초 (기본: 1.0)")
    parser.add_argument("--dry-run", action="store_true", help="필터링만 하고 복사하지 않음")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        console.print(f"[red]오류: 폴더가 없습니다: {folder}[/red]")
        sys.exit(1)

    if args.style not in STYLE_DESCRIPTIONS:
        console.print(f"[red]오류: 알 수 없는 스타일: {args.style}[/red]")
        console.print("사용 가능:", ", ".join(STYLE_DESCRIPTIONS.keys()))
        sys.exit(1)

    output_dir = Path(args.output_dir or f"필터링_{args.style}")

    # 이미지 파일 목록
    images = sorted([
        f for f in folder.iterdir()
        if f.suffix.lower() in IMAGE_EXTENSIONS and not f.name.startswith("_")
    ])

    if not images:
        console.print(f"[red]오류: {folder}에 이미지 파일이 없습니다[/red]")
        sys.exit(1)

    console.print(f"\n{'='*60}")
    console.print(f" [bold]음식사진 필터링[/bold]")
    console.print(f" 폴더: {folder} ({len(images)}장)")
    console.print(f" 스타일: {args.style}")
    console.print(f" 최소 점수: {args.min_score}")
    console.print(f" 모드: {'분석만 (dry-run)' if args.dry_run else '분석 + 복사'}")
    console.print(f"{'='*60}\n")

    # Gemini 클라이언트
    client = genai.Client()

    # 필터링 실행
    results = []
    passed = 0
    rejected_not_food = 0
    rejected_low_score = 0
    errors = 0

    for i, image_path in enumerate(images, 1):
        console.print(f"  [{i}/{len(images)}] {image_path.name}...", end=" ")

        result = filter_image(client, image_path, args.style)

        if result is None:
            errors += 1
            console.print("[yellow]오류[/yellow]")
            results.append({"file": image_path.name, "status": "error"})
            time.sleep(args.delay)
            continue

        is_food = result.get("is_food", False)
        style_score = result.get("style_score", 0)
        quality_score = result.get("quality_score", 0)
        avg_score = (style_score + quality_score) / 2
        food_type = result.get("food_type", "없음")

        entry = {
            "file": image_path.name,
            "is_food": is_food,
            "style_score": style_score,
            "quality_score": quality_score,
            "avg_score": round(avg_score, 1),
            "food_type": food_type,
        }

        if not is_food:
            entry["status"] = "rejected_not_food"
            rejected_not_food += 1
            console.print(f"[red]제외 (음식 아님: {food_type})[/red]")
        elif avg_score < args.min_score:
            entry["status"] = "rejected_low_score"
            rejected_low_score += 1
            console.print(f"[yellow]제외 (점수 {avg_score:.1f} < {args.min_score})[/yellow]")
        else:
            entry["status"] = "passed"
            passed += 1
            console.print(f"[green]통과 (스타일:{style_score} 품질:{quality_score} 음식:{food_type})[/green]")

        results.append(entry)
        time.sleep(args.delay)

    # 결과 요약
    console.print(f"\n{'='*60}")
    console.print(f" [bold]필터링 결과[/bold]")
    console.print(f"  전체: {len(images)}장")
    console.print(f"  [green]통과: {passed}장[/green]")
    console.print(f"  [red]제외 (음식 아님): {rejected_not_food}장[/red]")
    console.print(f"  [yellow]제외 (점수 부족): {rejected_low_score}장[/yellow]")
    console.print(f"  오류: {errors}장")
    console.print(f"{'='*60}\n")

    # 통과한 사진 복사
    if not args.dry_run and passed > 0:
        output_dir.mkdir(parents=True, exist_ok=True)
        copied = 0
        for entry in results:
            if entry.get("status") != "passed":
                continue
            src = folder / entry["file"]
            # 새 번호로 이름 변경
            copied += 1
            dst = output_dir / f"{args.style}_{copied:03d}.jpg"
            shutil.copy2(src, dst)

        console.print(f" {copied}장을 {output_dir}에 복사 완료\n")

    # 필터링 결과 저장
    filter_report_path = (output_dir if not args.dry_run else folder) / "_filter_report.json"
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "style": args.style,
        "source_folder": str(folder),
        "total": len(images),
        "passed": passed,
        "rejected_not_food": rejected_not_food,
        "rejected_low_score": rejected_low_score,
        "errors": errors,
        "min_score": args.min_score,
        "results": results,
    }
    filter_report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    console.print(f" 필터 보고서: {filter_report_path}")

    # 통과한 사진 상위 점수 테이블
    passed_results = [r for r in results if r.get("status") == "passed"]
    if passed_results:
        passed_results.sort(key=lambda x: x.get("avg_score", 0), reverse=True)
        table = Table(title="상위 점수 사진 (최대 10개)")
        table.add_column("파일", style="cyan")
        table.add_column("음식", style="green")
        table.add_column("스타일", justify="center")
        table.add_column("품질", justify="center")
        table.add_column("평균", justify="center", style="bold")
        for r in passed_results[:10]:
            table.add_row(
                r["file"],
                r.get("food_type", ""),
                str(r.get("style_score", "")),
                str(r.get("quality_score", "")),
                str(r.get("avg_score", "")),
            )
        console.print(table)

    if not args.dry_run and passed > 0:
        console.print(f"\n다음 단계:")
        console.print(f"  uv run batch_analyze.py --folder {output_dir} --output-dir 분석결과_{args.style}")


if __name__ == "__main__":
    main()
