#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pydantic>=2.0.0",
#     "Pillow>=10.0.0",
# ]
# ///
"""
사진 폴더를 일괄 분석하는 배치 스크립트.

사용법:
  uv run batch_analyze.py --folder "김현경작가_샘플1"
  uv run batch_analyze.py --folder "김현경작가_샘플1" --limit 5
  uv run batch_analyze.py --folder "김현경작가_샘플1" --delay 5 --no-skip
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from google import genai
from PIL import Image
from pydantic import ValidationError

# ── analyze_photo.py에서 모델 + 변환 함수 임포트 ─────────────────
SKILL_SCRIPTS = Path.home() / ".claude" / "skills" / "photo-style-analyzer" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
from analyze_photo import StyleProfile, convert_with_gemini  # noqa: E402

# ── 카테고리별 분석 프롬프트 ──────────────────────────────────────

PROMPTS = {
    "food": """당신은 20년 경력의 상업 푸드 포토그래퍼이자 컬러리스트입니다.
이 음식 사진을 다음 항목별로 전문적으로 분석해주세요:

1. **조명 분석**: 광원 방향, 광질(경광/연광), 그림자 특성, 하이라이트/섀도우 비율, 추정 조명 장비
2. **색감/컬러 분석**: 색온도(K값 추정), 화이트밸런스, 주조색/보조색, 채도 수준, 컬러 그레이딩 스타일, 가장 유사한 필름스톡(Kodak Portra 400 등)
3. **구도 분석**: 카메라 앵글, 촬영 거리, 추정 렌즈 화각(mm), 피사계심도(DOF), 초점 위치, 구도 법칙(삼분할/대칭/리딩라인 등)
4. **질감/디테일**: 선명도, 노이즈 수준, 텍스처 표현력, 후보정 정도
5. **분위기/무드**: 전체적 톤앤매너, 타깃 용도(SNS/메뉴판/광고), 감성 키워드 3개
6. **개선점**: 프로 수준으로 끌어올리려면 조명/색감/구도에서 각각 무엇을 바꿔야 하는지

최종적으로, 이 사진의 스타일을 다른 음식 사진에 동일하게 적용할 수 있는 Nano Banana Pro용 프롬프트를 작성해주세요.""",
    "portrait": """당신은 20년 경력의 상업 인물 사진작가이자 리터처입니다.
이 인물 사진을 다음 항목별로 전문적으로 분석해주세요:

1. **조명 분석**: 주광/보조광/테두리광 위치, 광질, 캐치라이트 형태, 조명 비율, 추정 장비
2. **색감/컬러 분석**: 색온도(K값), 스킨톤 렌더링, 주조색/보조색, 채도, 컬러 그레이딩, 유사 필름스톡
3. **구도 분석**: 촬영 앵글, 프레이밍, 렌즈(mm), 피사계심도, 초점 위치, 배경 처리
4. **질감/디테일**: 피부 질감, 선명도, 리터칭 수준, 디테일
5. **분위기/무드**: 톤앤매너, 표정/포즈, 타깃 용도, 감성 키워드 3개
6. **개선점**: 조명/포즈/후보정 각각에서 개선할 점

최종적으로 이 스타일을 재현할 수 있는 Nano Banana Pro용 프롬프트를 작성해주세요.""",
    "other": """당신은 20년 경력의 상업 사진작가이자 컬러리스트입니다.
이 사진을 다음 항목별로 전문적으로 분석해주세요:

1. **조명 분석**: 광원 방향, 광질, 그림자 특성, 하이라이트/섀도우 비율, 추정 조명
2. **색감/컬러 분석**: 색온도(K값 추정), 화이트밸런스, 주조색/보조색, 채도, 컬러 그레이딩, 유사 필름스톡
3. **구도 분석**: 카메라 앵글, 렌즈 화각(mm), 피사계심도, 초점 위치, 구도 법칙
4. **질감/디테일**: 선명도, 노이즈, 텍스처 표현력, 후보정 정도
5. **분위기/무드**: 톤앤매너, 타깃 용도, 감성 키워드 3개
6. **개선점**: 전문적 수준으로 끌어올리기 위한 제안

최종적으로 이 스타일을 재현할 수 있는 Nano Banana Pro용 프롬프트를 작성해주세요.""",
}

# ── 이미지 확장자 ─────────────────────────────────────────────────
IMAGE_EXTENSIONS = {".jpeg", ".jpg", ".png", ".webp"}


# ── 1단계: Gemini API로 이미지 분석 ──────────────────────────────
def analyze_image_with_gemini(client: genai.Client, image_path: Path, category: str = "food") -> str:
    """Gemini Pro로 이미지를 직접 분석하여 텍스트를 반환한다."""
    prompt = PROMPTS.get(category, PROMPTS["other"])

    # PIL로 이미지 로드
    img = Image.open(image_path)

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=[prompt, img],
        config={
            "temperature": 0.3,
        },
    )
    return response.text


# ── 마크다운 리포트 생성 ─────────────────────────────────────────
def save_analysis_md(filename: str, analysis_text: str, profile: dict, output_dir: Path) -> Path:
    """분석 결과를 한국어 마크다운 리포트로 저장한다."""
    stem = Path(filename).stem
    md_path = output_dir / f"{stem}_analysis.md"

    # 프로필에서 주요 정보 추출
    lighting = profile.get("lighting", {})
    color = profile.get("color", {})
    composition = profile.get("composition", {})
    texture = profile.get("texture", {})
    mood = profile.get("mood", {})

    content = f"""# 사진 분석 리포트: {filename}

**분석 일시**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**카테고리**: {profile.get("category", "unknown")}

---

## 분석 요약

| 항목 | 결과 |
|------|------|
| 조명 | {lighting.get("direction", "")} / {lighting.get("quality", "")} / {lighting.get("equipment", "")} |
| 색온도 | {color.get("temperature_k", "")}K / {color.get("white_balance", "")} |
| 채도 | {color.get("saturation", "")} |
| 필름스톡 | {color.get("similar_film_stock", "")} |
| 구도 | {composition.get("angle", "")} / {composition.get("composition_rule", "")} |
| 렌즈 | {composition.get("estimated_lens_mm", "")}mm / DOF: {composition.get("dof", "")} |
| 선명도 | {texture.get("sharpness", "")} / 노이즈: {texture.get("noise", "")} |
| 분위기 | {mood.get("tone", "")} |
| 키워드 | {", ".join(mood.get("keywords", []))} |

---

## Gemini 상세 분석

{analysis_text}

---

## Nano Banana Pro 프롬프트

```
{profile.get("nano_banana_prompt", "")}
```
"""
    md_path.write_text(content, encoding="utf-8")
    return md_path


# ── 단일 사진 처리 ───────────────────────────────────────────────
def process_single_photo(
    client: genai.Client,
    image_path: Path,
    output_dir: Path,
    category: str = "food",
) -> dict:
    """1장을 분석하고 결과 파일을 저장한다."""
    filename = image_path.name
    stem = image_path.stem

    # 1단계: Gemini로 이미지 분석
    print(f"  1단계: Gemini Pro 분석 중...", end=" ", flush=True)
    t0 = time.time()
    analysis_text = analyze_image_with_gemini(client, image_path, category)
    elapsed = time.time() - t0
    print(f"완료 ({elapsed:.1f}초)")

    # 파일명 정보를 분석 텍스트에 추가
    analysis_with_file = f"파일명: {filename}\n카테고리: {category}\n\n{analysis_text}"

    # 2단계: JSON 구조화 + Pydantic 검증
    print(f"  2단계: JSON 구조화 중...", end=" ", flush=True)
    t0 = time.time()
    profile = convert_with_gemini(analysis_with_file, max_retries=3)
    elapsed = time.time() - t0
    print(f"완료 ({elapsed:.1f}초)")

    # 파일명 보정 (convert_with_gemini가 다른 이름을 넣을 수 있으므로)
    profile["file"] = filename

    # 3단계: 파일 저장
    # JSON 프로필 저장
    json_path = output_dir / f"{stem}_profile.json"
    json_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

    # 마크다운 리포트 저장
    md_path = save_analysis_md(filename, analysis_text, profile, output_dir)

    print(f"  3단계: 파일 저장 완료")
    print(f"    -> {json_path.name}")
    print(f"    -> {md_path.name}")

    return profile


# ── 배치 처리 메인 ───────────────────────────────────────────────
def batch_analyze(
    folder_path: Path,
    output_dir: Path,
    category: str = "food",
    skip_existing: bool = True,
    limit: int = 0,
    delay: float = 3.0,
    start_idx: int = 0,
    end_idx: int = 0,
    worker_id: str = "",
):
    """폴더 내 모든 이미지를 일괄 분석한다."""
    tag = f"[워커 {worker_id}]" if worker_id else "[배치 분석]"

    # 이미지 파일 목록 수집 (알파벳순 정렬)
    images = sorted(
        [f for f in folder_path.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS],
        key=lambda f: f.name,
    )
    total_found = len(images)

    # 범위 지정 (병렬 실행용)
    if start_idx > 0 or end_idx > 0:
        actual_end = end_idx if end_idx > 0 else len(images)
        images = images[start_idx:actual_end]
        print(f"{tag} 범위: {start_idx}~{actual_end} (전체 {total_found}장 중)")

    # 이미 분석된 파일 필터링
    skipped = 0
    if skip_existing:
        filtered = []
        for img in images:
            profile_path = output_dir / f"{img.stem}_profile.json"
            if profile_path.exists():
                skipped += 1
            else:
                filtered.append(img)
        images = filtered

    # limit 적용
    if limit > 0:
        images = images[:limit]

    to_process = len(images)
    print(f"\n{tag} 폴더: {folder_path.name}")
    print(f"  발견: {total_found}장 / 분석 완료: {skipped}장 / 처리 예정: {to_process}장")
    if limit > 0:
        print(f"  (--limit {limit} 적용)")
    print()

    if to_process == 0:
        print("처리할 사진이 없습니다.")
        return

    # Gemini 클라이언트 초기화
    client = genai.Client()

    # 처리 시작
    start_time = time.time()
    success = 0
    failed = 0
    errors = []

    for i, image_path in enumerate(images, 1):
        print(f"[{i}/{to_process}] {image_path.name}")

        try:
            process_single_photo(client, image_path, output_dir, category)
            success += 1
        except Exception as e:
            failed += 1
            error_msg = f"{image_path.name}: {type(e).__name__}: {e}"
            errors.append(error_msg)
            print(f"  [실패] {error_msg}", file=sys.stderr)

        # Rate Limit 방지 대기 (마지막 사진 제외)
        if i < to_process and delay > 0:
            print(f"  (다음 사진까지 {delay}초 대기...)")
            time.sleep(delay)

        print()

    # 최종 요약
    total_time = time.time() - start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)

    print("=" * 50)
    print(f"{tag} [완료] {success}/{to_process}장 성공, {failed}장 실패")
    print(f"  총 소요 시간: {minutes}분 {seconds}초")
    print(f"  결과 폴더: {output_dir}")

    if errors:
        print(f"\n  실패 목록:")
        for err in errors:
            print(f"    - {err}")

        # 에러 로그 파일 저장
        error_log = output_dir / "batch_errors.log"
        error_log.write_text(
            f"배치 분석 에러 로그 ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"
            + "\n".join(errors),
            encoding="utf-8",
        )
        print(f"  에러 로그: {error_log}")


# ── CLI ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="사진 폴더 일괄 분석 스크립트")
    parser.add_argument("--folder", required=True, help="분석할 이미지 폴더 경로")
    parser.add_argument("--output", help="결과 파일 저장 폴더 (기본: 프로젝트 루트)")
    parser.add_argument("--category", default="food", choices=["food", "portrait", "other"], help="사진 카테고리 (기본: food)")
    parser.add_argument("--no-skip", action="store_true", help="이미 분석된 파일도 다시 처리")
    parser.add_argument("--limit", type=int, default=0, help="처리할 최대 사진 수 (0=전부)")
    parser.add_argument("--delay", type=float, default=3.0, help="API 호출 간 대기 시간 초 (기본: 3)")
    parser.add_argument("--api-key", help="Gemini API 키 (기본: GEMINI_API_KEY 환경변수)")
    parser.add_argument("--start", type=int, default=0, help="시작 인덱스 (0부터, 병렬 실행용)")
    parser.add_argument("--end", type=int, default=0, help="끝 인덱스 (0=전부, 병렬 실행용)")
    parser.add_argument("--worker-id", type=str, default="", help="워커 식별자 (로그용)")

    args = parser.parse_args()

    # API 키 설정
    if args.api_key:
        import os
        os.environ["GOOGLE_API_KEY"] = args.api_key

    # 폴더 경로 확인
    folder = Path(args.folder)
    if not folder.is_absolute():
        folder = Path.cwd() / folder
    if not folder.exists():
        print(f"[에러] 폴더를 찾을 수 없습니다: {folder}", file=sys.stderr)
        sys.exit(1)

    # 출력 폴더
    if args.output:
        output_dir = Path(args.output)
        if not output_dir.is_absolute():
            output_dir = Path.cwd() / output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path.cwd()

    batch_analyze(
        folder_path=folder,
        output_dir=output_dir,
        category=args.category,
        skip_existing=not args.no_skip,
        limit=args.limit,
        delay=args.delay,
        start_idx=args.start,
        end_idx=args.end,
        worker_id=args.worker_id,
    )


if __name__ == "__main__":
    main()
