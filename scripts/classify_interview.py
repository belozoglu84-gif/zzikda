#!/usr/bin/env python3
"""
찍다 — 사진 분류 인터뷰 도구

사진을 보면서 4차원(분위기/배경/앵글/소품) 태그를 달 수 있는 터미널 도구.
Phase 1의 자동 매핑 결과를 프리필로 보여주고, 확인/수정할 수 있음.

사용법:
  python scripts/classify_interview.py                 # 미분류(unknown) 항목부터
  python scripts/classify_interview.py --all           # 전체 사진
  python scripts/classify_interview.py --style bright-airy  # 특정 스타일만
  python scripts/classify_interview.py --stats         # 현재 통계만 출력
"""

import json
import os
import sys
import argparse
import subprocess
import platform
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = ROOT / "dimensions" / "taxonomy.json"
TAGGED_PATH = ROOT / "dimensions" / "tagged_photos.json"
PROGRESS_PATH = ROOT / "dimensions" / "classify_progress.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def open_image(filepath):
    """이미지를 기본 뷰어로 열기"""
    filepath = str(filepath)
    if not os.path.exists(filepath):
        print(f"  (이미지 파일 없음: {filepath})")
        return
    try:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", filepath])
        else:
            subprocess.Popen(["xdg-open", filepath])
    except Exception as e:
        print(f"  (이미지 열기 실패: {e})")


def find_image_path(photo_id, source_style):
    """photo_id로 실제 이미지 파일 경로 찾기"""
    # 스타일 폴더 매핑
    style_folders = {
        "bright-airy": "bright-airy",
        "kim-hyunkyung": "김현경작가",
        "dark-moody": "dark-moody",
        "clean-minimal": "clean-minimal",
        "film-vintage": "film-vintage",
        "japanese-zen": "japanese-zen",
        "warm-rustic": "warm-rustic",
        "vibrant-pop": "vibrant-pop",
        "street-casual": "street-casual",
        "overhead-table": "overhead-table",
        "action-shot": "action-shot",
    }

    folder = style_folders.get(source_style, source_style)

    # 가능한 경로들 시도
    search_dirs = [
        ROOT / "styles" / folder / "0_원본수집",
        ROOT / "styles" / folder / "1_pinterest",
        ROOT / "styles" / folder,
    ]

    extensions = [".jpg", ".jpeg", ".png", ".webp"]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for ext in extensions:
            candidate = search_dir / f"{photo_id}{ext}"
            if candidate.exists():
                return candidate
            # 부분 매칭 시도 (파일명에 photo_id가 포함된 경우)
            for f in search_dir.iterdir():
                if f.is_file() and photo_id in f.stem and f.suffix.lower() in extensions:
                    return f

    return None


def print_stats(tagged, taxonomy):
    """현재 분류 통계 출력"""
    total = len(tagged)
    print(f"\n{'=' * 50}")
    print(f"  분류 현황 (전체 {total}장)")
    print(f"{'=' * 50}")

    for dim_name in ["mood", "background", "angle"]:
        dim_ko = taxonomy["dimensions"][dim_name]["name_ko"]
        values = [t.get(dim_name, "unknown") for t in tagged.values()]
        unknown = values.count("unknown")
        classified = total - unknown
        print(f"\n  {dim_ko}: {classified}/{total} ({classified/total*100:.1f}%)")

        counter = Counter(values)
        for val, cnt in counter.most_common(5):
            val_ko = taxonomy["dimensions"][dim_name]["values"].get(val, {}).get("name_ko", val)
            print(f"    {val_ko}: {cnt}장")
        if len(counter) > 5:
            print(f"    ... 외 {len(counter)-5}개")

    # 수동 분류된 항목 수
    progress = {}
    if PROGRESS_PATH.exists():
        progress = load_json(PROGRESS_PATH)
    manual_count = len(progress.get("manually_classified", []))
    print(f"\n  수동 분류 완료: {manual_count}장")
    print(f"{'=' * 50}\n")


def ask_dimension(dim_name, dim_def, current_value, taxonomy):
    """하나의 차원에 대해 질문하고 답변 받기"""
    values = dim_def["values"]
    value_list = list(values.items())
    dim_ko = dim_def["name_ko"]

    # 현재 값의 한글 이름
    current_ko = values.get(current_value, {}).get("name_ko", current_value)

    # 프리필 번호 찾기
    prefill_num = None
    for i, (vid, vdef) in enumerate(value_list):
        if vid == current_value:
            prefill_num = i + 1
            break

    # 질문 출력
    is_multiple = dim_def.get("multiple", False)
    if is_multiple:
        print(f"\n  Q. {dim_ko}? (복수 선택: 1,3,5 / Enter=현재값 유지)")
    else:
        print(f"\n  Q. {dim_ko}? (숫자 입력 / Enter=현재값 유지)")

    for i, (vid, vdef) in enumerate(value_list):
        marker = " ◀" if vid == current_value else ""
        # 현재 값이 리스트인 경우 (소품)
        if isinstance(current_value, list) and vid in current_value:
            marker = " ◀"
        print(f"    {i+1:2d}) {vdef['name_ko']:<12s} ({vdef['name_en']}){marker}")

    # 현재 값 표시
    if isinstance(current_value, list):
        current_display = ", ".join(
            values.get(v, {}).get("name_ko", v) for v in current_value
        )
    else:
        current_display = current_ko
    print(f"    현재: [{current_display}]")

    # 입력 받기
    try:
        answer = input("    > ").strip()
    except (EOFError, KeyboardInterrupt):
        return None  # 종료 신호

    # Enter = 현재값 유지
    if not answer:
        return current_value

    if is_multiple:
        # 복수 선택 파싱
        try:
            nums = [int(x.strip()) for x in answer.split(",")]
            selected = []
            for n in nums:
                if n == 0:
                    return ["prop-none"]
                if 1 <= n <= len(value_list):
                    selected.append(value_list[n - 1][0])
            return selected if selected else current_value
        except ValueError:
            print("    (잘못된 입력, 현재값 유지)")
            return current_value
    else:
        # 단일 선택
        try:
            num = int(answer)
            if 1 <= num <= len(value_list):
                return value_list[num - 1][0]
            else:
                print("    (범위 밖, 현재값 유지)")
                return current_value
        except ValueError:
            print("    (잘못된 입력, 현재값 유지)")
            return current_value


def classify_one(photo_id, tags, taxonomy):
    """사진 1장을 인터뷰 방식으로 분류"""
    dims = taxonomy["dimensions"]

    print(f"\n{'─' * 50}")
    print(f"  사진: {photo_id}")
    print(f"  소스: {tags.get('source_style', 'unknown')}")
    print(f"{'─' * 50}")

    # 이미지 열기
    img_path = find_image_path(photo_id, tags.get("source_style", ""))
    if img_path:
        print(f"  (이미지 열기: {img_path.name})")
        open_image(img_path)
    else:
        print("  (이미지 파일을 찾을 수 없음)")

    new_tags = dict(tags)

    # 분위기
    result = ask_dimension("mood", dims["mood"], tags.get("mood", "unknown"), taxonomy)
    if result is None:
        return None
    new_tags["mood"] = result

    # 배경
    result = ask_dimension("background", dims["background"], tags.get("background", "unknown"), taxonomy)
    if result is None:
        return None
    new_tags["background"] = result

    # 앵글
    result = ask_dimension("angle", dims["angle"], tags.get("angle", "unknown"), taxonomy)
    if result is None:
        return None
    new_tags["angle"] = result

    # 소품
    result = ask_dimension("props", dims["props"], tags.get("props", ["prop-none"]), taxonomy)
    if result is None:
        return None
    new_tags["props"] = result

    # 결과 요약
    mood_ko = dims["mood"]["values"].get(new_tags["mood"], {}).get("name_ko", new_tags["mood"])
    bg_ko = dims["background"]["values"].get(new_tags["background"], {}).get("name_ko", new_tags["background"])
    angle_ko = dims["angle"]["values"].get(new_tags["angle"], {}).get("name_ko", new_tags["angle"])
    props_ko = ", ".join(
        dims["props"]["values"].get(p, {}).get("name_ko", p) for p in new_tags["props"]
    )

    print(f"\n  ✅ {photo_id}")
    print(f"     {mood_ko} / {bg_ko} / {angle_ko} / {props_ko}")

    return new_tags


def get_filter_list(tagged, mode, style_filter=None):
    """필터링된 사진 목록 반환"""
    items = list(tagged.items())

    if style_filter:
        items = [(k, v) for k, v in items if v.get("source_style") == style_filter]

    if mode == "unknown":
        # unknown이 하나라도 있는 항목만
        items = [
            (k, v) for k, v in items
            if v.get("mood") == "unknown"
            or v.get("background") == "unknown"
            or v.get("angle") == "unknown"
        ]

    return items


def main():
    parser = argparse.ArgumentParser(description="찍다 — 사진 분류 인터뷰 도구")
    parser.add_argument("--all", action="store_true", help="전체 사진 분류")
    parser.add_argument("--style", type=str, help="특정 스타일만 (예: bright-airy)")
    parser.add_argument("--stats", action="store_true", help="통계만 출력")
    args = parser.parse_args()

    # 데이터 로드
    taxonomy = load_json(TAXONOMY_PATH)
    tagged = load_json(TAGGED_PATH)

    # 통계만 출력
    if args.stats:
        print_stats(tagged, taxonomy)
        return

    # 진행 상태 로드
    progress = {"manually_classified": [], "current_index": 0}
    if PROGRESS_PATH.exists():
        progress = load_json(PROGRESS_PATH)

    # 필터링
    mode = "all" if args.all else "unknown"
    items = get_filter_list(tagged, mode, args.style)

    if not items:
        if mode == "unknown":
            print("\n✅ 미분류 항목이 없습니다! --all 옵션으로 전체 검토 가능.")
        else:
            print("\n❌ 해당 조건의 사진이 없습니다.")
        return

    print(f"\n📋 분류 대상: {len(items)}장")
    if mode == "unknown":
        print("   (미분류 항목만 표시. --all로 전체 검토 가능)")
    print("   Enter=현재값 유지 / Ctrl+C=저장 후 종료 / b=이전으로\n")

    # 이전 진행 위치에서 이어서 시작
    # 진행 상태의 photo_id 목록과 현재 목록이 다를 수 있으므로 index 기반 대신 처음부터
    i = 0
    classified_count = 0

    while i < len(items):
        photo_id, tags = items[i]

        # 이미 수동 분류한 항목이면 건너뛰기 (--all 모드에서)
        if photo_id in progress.get("manually_classified", []) and mode == "unknown":
            i += 1
            continue

        # 진행 상태 표시
        print(f"\n  [{i+1}/{len(items)}]", end="")

        try:
            new_tags = classify_one(photo_id, tags, taxonomy)
        except KeyboardInterrupt:
            print("\n\n💾 진행 상태 저장 중...")
            save_json(PROGRESS_PATH, progress)
            save_json(TAGGED_PATH, tagged)
            print(f"   저장 완료! (수동 분류: {classified_count}장)")
            print(f"   이어서 하려면: python scripts/classify_interview.py")
            return

        if new_tags is None:
            # Ctrl+C 또는 EOF
            print("\n\n💾 진행 상태 저장 중...")
            save_json(PROGRESS_PATH, progress)
            save_json(TAGGED_PATH, tagged)
            print(f"   저장 완료! (수동 분류: {classified_count}장)")
            return

        # 네비게이션
        print("\n  다음? (Enter=다음 / b=이전 / q=저장후종료 / s=통계)")
        try:
            nav = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            nav = "q"

        if nav == "q":
            # 현재 결과 저장 후 종료
            tagged[photo_id] = new_tags
            if photo_id not in progress["manually_classified"]:
                progress["manually_classified"].append(photo_id)
            classified_count += 1
            save_json(PROGRESS_PATH, progress)
            save_json(TAGGED_PATH, tagged)
            print(f"\n💾 저장 완료! (이번 세션: {classified_count}장)")
            return
        elif nav == "b":
            # 이전으로 (현재 결과는 저장하지 않음)
            if i > 0:
                i -= 1
            else:
                print("  (첫 번째 사진입니다)")
            continue
        elif nav == "s":
            # 현재까지 저장 + 통계 표시
            tagged[photo_id] = new_tags
            if photo_id not in progress["manually_classified"]:
                progress["manually_classified"].append(photo_id)
            classified_count += 1
            print_stats(tagged, taxonomy)
            i += 1
            continue
        else:
            # 다음 (Enter 포함)
            tagged[photo_id] = new_tags
            if photo_id not in progress["manually_classified"]:
                progress["manually_classified"].append(photo_id)
            classified_count += 1
            i += 1

    # 전부 완료
    save_json(PROGRESS_PATH, progress)
    save_json(TAGGED_PATH, tagged)
    print(f"\n🎉 전체 분류 완료! (이번 세션: {classified_count}장)")
    print_stats(tagged, taxonomy)


if __name__ == "__main__":
    main()
