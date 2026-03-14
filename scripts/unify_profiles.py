"""
unify_profiles.py - 개별 스타일 프로필 JSON → 통합 스타일 프로필 생성

사용법:
    uv run unify_profiles.py --style-name "클린 미니멀" --folder 분석결과_clean-minimal
    uv run unify_profiles.py --style-name "김현경 작가" --folder 분석결과
    uv run unify_profiles.py --style-name "따뜻한 러스틱" --folder 분석결과_warm-rustic --output custom_name.json
    uv run unify_profiles.py --exclude-category other
"""

# /// script
# requires-python = ">=3.10"
# dependencies = ["rich>=13.0.0"]
# ///

import json
import sys
import argparse
from pathlib import Path
from collections import Counter
from typing import Any


def load_all_profiles(folder: Path, exclude_categories: list[str]) -> tuple[list[dict], list[str]]:
    """폴더에서 모든 _profile.json 파일 로드"""
    profiles = []
    skipped = []

    for json_file in sorted(folder.glob("*_profile.json")):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            category = data.get("category", "unknown")
            if category in exclude_categories:
                skipped.append(f"{json_file.name} (category={category})")
                continue
            profiles.append(data)
        except Exception as e:
            print(f"   파일 읽기 실패: {json_file.name}  {e}", file=sys.stderr)

    return profiles, skipped


def mode_counter(values: list) -> dict:
    """값 목록에서 빈도 분석 반환"""
    counter = Counter(v for v in values if v is not None)
    total = len(values)
    result = []
    for value, count in counter.most_common():
        result.append({
            "value": value,
            "count": count,
            "percent": round(count / total * 100, 1) if total > 0 else 0
        })
    return {
        "most_common": counter.most_common(1)[0][0] if counter else None,
        "distribution": result
    }


def numeric_stats(values: list[float | int]) -> dict:
    """숫자 목록의 통계 계산"""
    clean = [v for v in values if v is not None and isinstance(v, (int, float))]
    if not clean:
        return {"min": None, "max": None, "mean": None, "count": 0}
    mean_val = sum(clean) / len(clean)
    return {
        "min": min(clean),
        "max": max(clean),
        "mean": round(mean_val, 1),
        "count": len(clean),
        "range_str": f"{min(clean)}~{max(clean)}K, 평균 {round(mean_val)}K" if "K" in str(clean[0]) else f"{min(clean)}~{max(clean)}, 평균 {round(mean_val, 1)}"
    }


def flatten_list_field(profiles: list[dict], *keys) -> list:
    """중첩된 리스트 필드를 단일 목록으로 평탄화"""
    result = []
    for p in profiles:
        obj = p
        for k in keys:
            obj = obj.get(k, {}) if isinstance(obj, dict) else {}
        if isinstance(obj, list):
            result.extend(obj)
        elif obj:
            result.append(obj)
    return result


def get_field(profiles: list[dict], *keys) -> list:
    """각 프로필에서 특정 필드 값 수집"""
    values = []
    for p in profiles:
        obj = p
        for k in keys:
            obj = obj.get(k) if isinstance(obj, dict) else None
        values.append(obj)
    return values


def analyze_film_stock(values: list[str]) -> dict:
    """필름 스탁 분류  복수 언급 있을 경우 파싱"""
    normalized = []
    for v in values:
        if not v:
            continue
        v_lower = v.lower()
        if "portra 800" in v_lower or "portra800" in v_lower:
            normalized.append("Kodak Portra 800")
        elif "portra 400" in v_lower or "portra400" in v_lower:
            normalized.append("Kodak Portra 400")
        elif "gold 200" in v_lower or "gold200" in v_lower:
            normalized.append("Kodak Gold 200")
        elif "ultramax" in v_lower:
            normalized.append("Kodak Ultramax 400")
        elif "fuji" in v_lower or "velvia" in v_lower:
            normalized.append("Fuji Velvia")
        elif "kodak" in v_lower:
            normalized.append("Kodak (기타)")
        else:
            normalized.append(v[:50])  # 너무 길면 자름
    return mode_counter(normalized)


def generate_unified_prompt(summary: dict) -> str:
    """통합 프로필 기반으로 nano_banana_prompt 생성"""
    lighting_dir = summary["lighting"]["direction"]["most_common"] or "back-left"
    quality = summary["lighting"]["quality"]["most_common"] or "soft"
    temp_k = summary["color"]["temperature_k"]["mean"] or 5000
    film = summary["color"]["film_stock"]["most_common"] or "Kodak Portra 400"
    angle = summary["composition"]["angle"]["most_common"] or "45-degree"
    dof = summary["composition"]["dof"]["most_common"] or "shallow"
    lens = summary["composition"]["estimated_lens_mm"]["mean"] or 85
    sharpness = summary["texture"]["sharpness"]["most_common"] or "very-high"
    mood_tone = summary["mood"]["tone"]["most_common"] or "moody"
    top_keywords = [item["value"] for item in summary["mood"]["keywords"]["distribution"][:5]]

    prompt = (
        f"Professional Korean food photography, shot at {angle} high angle, "
        f"{quality} {lighting_dir} directional lighting from studio strobe, "
        f"warm color temperature ~{round(temp_k)}K, {film} film style, "
        f"desaturated and muted tones with cinematic grading, lifted blacks, "
        f"on {lens:.0f}mm lens with {dof} depth of field, "
        f"extreme sharpness ({sharpness}) on food texture, "
        f"{mood_tone} atmosphere  {', '.join(top_keywords)}, "
        f"rustic dark wooden table, artisanal ceramic tableware, "
        f"editorial food magazine quality, 8K resolution."
    )
    return prompt


def main():
    parser = argparse.ArgumentParser(description="개별 프로필 → 통합 스타일 프로필 생성")
    parser.add_argument("--folder", default=".", help="프로필 JSON이 있는 폴더 (기본: 현재 폴더)")
    parser.add_argument("--style-name", default="", help="스타일 이름 (예: '클린 미니멀', '김현경 작가')")
    parser.add_argument("--output", default="", help="출력 파일명 (기본: {style_name}_unified_profile.json)")
    parser.add_argument("--exclude-category", nargs="*", default=["other"], help="제외할 카테고리 (기본: other)")
    args = parser.parse_args()

    folder = Path(args.folder)

    # 출력 파일명 자동 결정
    if args.output:
        output_path = folder / args.output
    elif args.style_name:
        safe_name = args.style_name.replace(" ", "_")
        output_path = folder / f"{safe_name}_unified_profile.json"
    else:
        output_path = folder / "unified_profile.json"

    style_label = args.style_name or "스타일"

    print(f"\n[폴더] {folder.resolve()}")
    print(f"[분석 시작...]\n")

    # 1. 프로필 로드
    profiles, skipped = load_all_profiles(folder, args.exclude_category)
    print(f" 로드 완료: {len(profiles)}개 프로필")
    if skipped:
        print(f"  제외: {len(skipped)}개")
        for s in skipped:
            print(f"   - {s}")
    print()

    if not profiles:
        print(" 분석할 프로필이 없습니다.")
        sys.exit(1)

    # 2. 각 필드 수집 및 분석
    summary: dict[str, Any] = {
        "meta": {
            "total_profiles": len(profiles),
            "excluded": skipped,
            "generator": "unify_profiles.py"
        }
    }

    #  카테고리 분포
    summary["category"] = mode_counter(get_field(profiles, "category"))

    #  조명 분석
    lighting_dirs = get_field(profiles, "lighting", "direction")
    # 방향 정규화 (한국어/영어 혼용)
    normalized_dirs = []
    for d in lighting_dirs:
        if not d:
            continue
        d_lower = str(d).lower()
        if "back" in d_lower or "후방" in d or "후광" in d or "역광" in d:
            normalized_dirs.append("back / 후방")
        elif "left" in d_lower or "좌" in d:
            normalized_dirs.append("left / 좌측")
        elif "right" in d_lower or "우" in d:
            normalized_dirs.append("right / 우측")
        elif "top" in d_lower or "상단" in d or "정면" in d:
            normalized_dirs.append("top / 상단")
        else:
            normalized_dirs.append(str(d)[:30])

    summary["lighting"] = {
        "direction": mode_counter(normalized_dirs),
        "quality": mode_counter(get_field(profiles, "lighting", "quality")),
        "equipment": mode_counter(get_field(profiles, "lighting", "equipment")),
        "highlight_shadow_ratio": {
            "samples": list(set(v for v in get_field(profiles, "lighting", "highlight_shadow_ratio") if v))[:8]
        }
    }

    #  색감 분석
    temp_values = get_field(profiles, "color", "temperature_k")
    temp_stats = numeric_stats(temp_values)
    temp_stats["range_str"] = f"{temp_stats['min']}~{temp_stats['max']}K, 평균 {round(temp_stats['mean'])}K"

    film_stocks = get_field(profiles, "color", "similar_film_stock")
    primary_colors = flatten_list_field(profiles, "color", "primary_colors")
    secondary_colors = flatten_list_field(profiles, "color", "secondary_colors")

    summary["color"] = {
        "temperature_k": temp_stats,
        "white_balance": mode_counter(get_field(profiles, "color", "white_balance")),
        "saturation": mode_counter(get_field(profiles, "color", "saturation")),
        "film_stock": analyze_film_stock(film_stocks),
        "primary_colors": mode_counter(primary_colors),
        "secondary_colors": mode_counter(secondary_colors),
    }

    #  구도 분석
    # 앵글 정규화
    raw_angles = get_field(profiles, "composition", "angle")
    norm_angles = []
    for a in raw_angles:
        if not a:
            continue
        a_lower = str(a).lower()
        if "45" in a_lower or "45도" in a or "45-degree" in a_lower:
            norm_angles.append("45도 하이앵글")
        elif "top" in a_lower or "탑" in a or "플랫레이" in a or "오버헤드" in a:
            norm_angles.append("탑다운 / 플랫레이")
        elif "eye" in a_lower or "아이레벨" in a or "정면" in a:
            norm_angles.append("아이레벨")
        elif "low" in a_lower or "로우" in a:
            norm_angles.append("로우앵글")
        else:
            norm_angles.append(str(a)[:30])

    lens_values = get_field(profiles, "composition", "estimated_lens_mm")
    lens_stats = numeric_stats(lens_values)
    lens_stats["range_str"] = f"{lens_stats['min']}~{lens_stats['max']}mm, 평균 {round(lens_stats['mean'])}mm"

    summary["composition"] = {
        "angle": mode_counter(norm_angles),
        "distance": mode_counter(get_field(profiles, "composition", "distance")),
        "estimated_lens_mm": lens_stats,
        "dof": mode_counter(get_field(profiles, "composition", "dof")),
    }

    #  질감 분석
    summary["texture"] = {
        "sharpness": mode_counter(get_field(profiles, "texture", "sharpness")),
        "noise": mode_counter(get_field(profiles, "texture", "noise")),
        "post_processing": mode_counter(get_field(profiles, "texture", "post_processing")),
    }

    #  분위기 분석
    # 톤 정규화
    raw_tones = get_field(profiles, "mood", "tone")
    norm_tones = []
    for t in raw_tones:
        if not t:
            continue
        t_lower = str(t).lower()
        if "dark" in t_lower or "모디" in t or "무디" in t or "moody" in t_lower:
            norm_tones.append("dark moody")
        elif "warm" in t_lower or "따뜻" in t or "웜" in t:
            norm_tones.append("warm & cozy")
        elif "minimal" in t_lower or "미니멀" in t:
            norm_tones.append("minimal & clean")
        elif "premium" in t_lower or "프리미엄" in t or "럭셔리" in t:
            norm_tones.append("premium")
        else:
            norm_tones.append(str(t)[:30])

    all_keywords = flatten_list_field(profiles, "mood", "keywords")
    summary["mood"] = {
        "tone": mode_counter(norm_tones),
        "target_use": mode_counter(get_field(profiles, "mood", "target_use")),
        "keywords": mode_counter(all_keywords),
    }

    #  통합 nano_banana_prompt 생성
    summary["unified_nano_banana_prompt"] = generate_unified_prompt(summary)

    #  활용 가이드
    summary["usage_guide"] = {
        "description": f"{style_label} 스타일 핵심 특성 요약",
        "lighting_tip": f"주 조명: {summary['lighting']['direction']['most_common']} 방향, {summary['lighting']['quality']['most_common']} 조명",
        "color_tip": f"색온도 {summary['color']['temperature_k']['range_str']}, 필름: {summary['color']['film_stock']['most_common']}",
        "composition_tip": f"앵글: {summary['composition']['angle']['most_common']}, 렌즈: {summary['composition']['estimated_lens_mm']['range_str']}",
        "mood_tip": f"분위기: {summary['mood']['tone']['most_common']}, 주요 키워드: {', '.join(item['value'] for item in summary['mood']['keywords']['distribution'][:5])}",
    }

    # 3. 저장
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f" 통합 프로필 저장 완료: {output_path}")

    # 4. 요약 출력
    print("\n" + "="*60)
    print(f" {style_label} 스타일 통합 분석 결과")
    print("="*60)
    print(f"\n[조명]")
    print(f"  방향: {summary['lighting']['direction']['most_common']}")
    dist = summary['lighting']['direction']['distribution']
    for d in dist[:3]:
        print(f"         {d['value']}: {d['count']}건 ({d['percent']}%)")
    print(f"  품질: {summary['lighting']['quality']['most_common']}")

    print(f"\n[색감]")
    print(f"  색온도: {summary['color']['temperature_k']['range_str']}")
    print(f"  채도: {summary['color']['saturation']['most_common']}")
    print(f"  필름: {summary['color']['film_stock']['most_common']}")

    print(f"\n[구도]")
    print(f"  앵글: {summary['composition']['angle']['most_common']}")
    print(f"  렌즈: {summary['composition']['estimated_lens_mm']['range_str']}")
    print(f"  심도: {summary['composition']['dof']['most_common']}")

    print(f"\n[질감]")
    print(f"  선명도: {summary['texture']['sharpness']['most_common']}")
    print(f"  노이즈: {summary['texture']['noise']['most_common']}")
    print(f"  후보정: {summary['texture']['post_processing']['most_common']}")

    print(f"\n[분위기]")
    print(f"  톤: {summary['mood']['tone']['most_common']}")
    print(f"  용도: {summary['mood']['target_use']['most_common']}")
    top_kw = [item['value'] for item in summary['mood']['keywords']['distribution'][:5]]
    print(f"  키워드: {', '.join(top_kw)}")

    print(f"\n[통합 프롬프트]")
    print(f"  {summary['unified_nano_banana_prompt'][:200]}...")

    print(f"\n 분석 완료! 저장: {output_path}\n")


if __name__ == "__main__":
    main()
