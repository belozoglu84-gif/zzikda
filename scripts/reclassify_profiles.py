#!/usr/bin/env python3
"""
찍다 — 기존 프로필 JSON을 4차원 태그로 자동 재분류

입력: styles/*/2_분석/*_profile.json
출력: dimensions/tagged_photos.json + 정확도 리포트
"""

import json
import glob
import os
import re
from pathlib import Path
from collections import Counter

# 프로젝트 루트
ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = ROOT / "dimensions" / "taxonomy.json"
OUTPUT_PATH = ROOT / "dimensions" / "tagged_photos.json"
REPORT_PATH = ROOT / "dimensions" / "mapping_report.txt"


def load_taxonomy():
    """taxonomy.json 로드"""
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_text_fields(profile):
    """프로필에서 매핑에 사용할 텍스트 필드들을 추출"""
    texts = {
        "mood_tone": str(profile.get("mood", {}).get("tone", "")),
        "mood_keywords": " ".join(profile.get("mood", {}).get("keywords", [])),
        "angle": str(profile.get("composition", {}).get("angle", "")),
        "distance": str(profile.get("composition", {}).get("distance", "")),
        "prompt": str(profile.get("nano_banana_prompt", "")),
        "improvement": str(profile.get("improvement_notes", "")),
        "grading": str(profile.get("color", {}).get("grading_style", "")),
        "film_stock": str(profile.get("color", {}).get("similar_film_stock", "")),
        "saturation": str(profile.get("color", {}).get("saturation", "")),
        "lighting_quality": str(profile.get("lighting", {}).get("quality", "")),
        "lighting_equipment": str(profile.get("lighting", {}).get("equipment", "")),
        "temp_k": profile.get("color", {}).get("temperature_k", 5500),
        "dof": str(profile.get("composition", {}).get("dof", "")),
    }
    # 전체 텍스트 합치기 (키워드 검색용)
    texts["all"] = " ".join([
        texts["mood_tone"], texts["mood_keywords"], texts["prompt"],
        texts["improvement"], texts["grading"], texts["film_stock"]
    ]).lower()
    return texts


def match_keywords(text, keywords):
    """텍스트에서 키워드 매칭 점수 계산"""
    text_lower = text.lower()
    score = 0
    for kw in keywords:
        if kw.lower() in text_lower:
            score += 1
    return score


def map_mood(texts, taxonomy):
    """분위기 차원 매핑"""
    mood_values = taxonomy["dimensions"]["mood"]["values"]
    all_text = texts["all"]
    mood_tone = texts["mood_tone"].lower()
    grading = texts["grading"].lower()

    best_id = "unknown"
    best_score = 0

    for value_id, value_def in mood_values.items():
        score = match_keywords(all_text, value_def["keywords"])

        # 보정: mood.tone에서 매칭되면 가중치 2배
        tone_score = match_keywords(mood_tone, value_def["keywords"])
        score += tone_score * 2

        # 보정: grading_style 매칭
        grading_score = match_keywords(grading, value_def["keywords"])
        score += grading_score

        if score > best_score:
            best_score = score
            best_id = value_id

    # 최소 점수 미달이면 unknown
    if best_score < 1:
        return "unknown"

    return best_id


def map_background(texts, taxonomy):
    """배경 차원 매핑 — nano_banana_prompt에서 주로 추출"""
    bg_values = taxonomy["dimensions"]["background"]["values"]
    prompt = texts["prompt"].lower()
    all_text = texts["all"]

    best_id = "unknown"
    best_score = 0

    for value_id, value_def in bg_values.items():
        # 프롬프트에서 우선 검색 (배경 정보가 가장 정확)
        score = match_keywords(prompt, value_def["keywords"]) * 2
        # 전체 텍스트에서도 보조 검색
        score += match_keywords(all_text, value_def["keywords"])

        if score > best_score:
            best_score = score
            best_id = value_id

    if best_score < 1:
        return "unknown"

    return best_id


def map_angle(texts, taxonomy):
    """앵글 차원 매핑 — composition.angle 필드에서 주로 추출"""
    angle_values = taxonomy["dimensions"]["angle"]["values"]
    angle_text = texts["angle"].lower()
    prompt = texts["prompt"].lower()

    # 직접 매핑 (가장 정확한 패턴)
    # 탑다운
    if any(kw in angle_text for kw in ["탑다운", "플랫레이", "top-down", "top down", "flat lay", "flatlay", "overhead", "90", "버드아이"]):
        return "angle-topdown"
    if any(kw in prompt for kw in ["top-down", "flat lay", "flatlay", "overhead", "bird"]):
        return "angle-topdown"

    # 45도
    if any(kw in angle_text for kw in ["45", "three-quarter", "하이앵글", "사선", "high angle", "high-angle"]):
        return "angle-high-45"
    if "45" in prompt and ("angle" in prompt or "degree" in prompt):
        return "angle-high-45"

    # 아이레벨
    if any(kw in angle_text for kw in ["eye level", "eye-level", "eyelevel", "아이레벨", "정면", "straight", "눈높이"]):
        return "angle-eye-level"
    if any(kw in prompt for kw in ["eye level", "eye-level", "straight on", "front view"]):
        return "angle-eye-level"

    # 로우앵글
    if any(kw in angle_text for kw in ["low", "로우", "아래"]):
        return "angle-low"

    # 다이내믹 틸트
    if any(kw in angle_text for kw in ["tilt", "dutch", "dynamic", "틸트", "기울"]):
        return "angle-dynamic-tilt"

    # 키워드 매칭 폴백
    best_id = "unknown"
    best_score = 0
    combined = angle_text + " " + prompt
    for value_id, value_def in angle_values.items():
        score = match_keywords(combined, value_def["keywords"])
        if score > best_score:
            best_score = score
            best_id = value_id

    return best_id if best_score >= 1 else "unknown"


def map_props(texts, taxonomy):
    """소품 차원 매핑 — 복수 선택, prompt + improvement_notes에서 추출"""
    prop_values = taxonomy["dimensions"]["props"]["values"]
    combined = (texts["prompt"] + " " + texts["improvement"]).lower()

    matched = []
    for value_id, value_def in prop_values.items():
        if value_id == "prop-none":
            continue
        score = match_keywords(combined, value_def["keywords"])
        if score >= 1:
            matched.append(value_id)

    return matched if matched else ["prop-none"]


def detect_source_style(file_path):
    """파일 경로에서 소스 스타일 추출"""
    path_str = str(file_path).replace("\\", "/")
    if "bright-airy" in path_str:
        return "bright-airy"
    if "김현경" in path_str:
        return "kim-hyunkyung"
    if "dark-moody" in path_str:
        return "dark-moody"
    if "clean-minimal" in path_str:
        return "clean-minimal"
    if "film-vintage" in path_str:
        return "film-vintage"
    if "japanese-zen" in path_str:
        return "japanese-zen"
    if "warm-rustic" in path_str:
        return "warm-rustic"
    if "vibrant-pop" in path_str:
        return "vibrant-pop"
    if "street-casual" in path_str:
        return "street-casual"
    if "overhead-table" in path_str:
        return "overhead-table"
    if "action-shot" in path_str:
        return "action-shot"
    return "unknown"


def find_all_profiles():
    """모든 프로필 JSON 파일 경로 수집"""
    pattern = str(ROOT / "styles" / "*" / "2_분석" / "*_profile.json")
    files = glob.glob(pattern, recursive=False)
    return sorted(files)


def generate_report(results, taxonomy):
    """매핑 정확도 리포트 생성"""
    lines = []
    lines.append("=" * 60)
    lines.append("  찍다 — 차원 재분류 매핑 리포트")
    lines.append("=" * 60)
    lines.append("")

    total = len(results)
    lines.append(f"전체 프로필 수: {total}")
    lines.append("")

    # 차원별 통계
    for dim_name in ["mood", "background", "angle", "props"]:
        dim_ko = taxonomy["dimensions"][dim_name]["name_ko"]
        lines.append(f"--- {dim_ko} ({dim_name}) ---")

        if dim_name == "props":
            # 소품은 복수이므로 다르게 집계
            all_props = []
            for r in results.values():
                all_props.extend(r.get("props", []))
            counter = Counter(all_props)
        else:
            values = [r.get(dim_name, "unknown") for r in results.values()]
            counter = Counter(values)

        unknown_count = counter.get("unknown", 0)
        for value, count in counter.most_common():
            pct = count / total * 100
            marker = " ⚠️" if value == "unknown" else ""
            lines.append(f"  {value}: {count}장 ({pct:.1f}%){marker}")

        if dim_name != "props":
            classified = total - unknown_count
            lines.append(f"  → 분류 성공: {classified}/{total} ({classified/total*100:.1f}%)")
            lines.append(f"  → 미분류: {unknown_count}장")
        lines.append("")

    # 미분류 항목 목록
    lines.append("--- 미분류 항목 상세 ---")
    for photo_id, tags in results.items():
        unknowns = []
        for dim in ["mood", "background", "angle"]:
            if tags.get(dim) == "unknown":
                unknowns.append(dim)
        if unknowns:
            lines.append(f"  {photo_id}: {', '.join(unknowns)}")
    lines.append("")

    # 소스 스타일별 집계
    lines.append("--- 소스 스타일별 프로필 수 ---")
    style_counter = Counter(r.get("source_style", "unknown") for r in results.values())
    for style, count in style_counter.most_common():
        lines.append(f"  {style}: {count}장")

    return "\n".join(lines)


def main():
    print("📂 taxonomy.json 로드...")
    taxonomy = load_taxonomy()

    print("🔍 프로필 파일 검색...")
    profile_files = find_all_profiles()
    print(f"  → {len(profile_files)}개 프로필 발견")

    if not profile_files:
        print("❌ 프로필 파일을 찾을 수 없습니다.")
        return

    results = {}
    errors = []

    print("🏷️  자동 매핑 시작...")
    for filepath in profile_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                profile = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            errors.append(f"{filepath}: {e}")
            continue

        # 파일명 추출 (확장자 제거)
        filename = profile.get("file", os.path.basename(filepath).replace("_profile.json", ".jpg"))
        photo_id = os.path.splitext(filename)[0]

        texts = extract_text_fields(profile)

        tags = {
            "mood": map_mood(texts, taxonomy),
            "background": map_background(texts, taxonomy),
            "angle": map_angle(texts, taxonomy),
            "props": map_props(texts, taxonomy),
            "source_style": detect_source_style(filepath),
            "source_profile": str(Path(filepath).relative_to(ROOT)).replace("\\", "/"),
        }

        results[photo_id] = tags

    # 결과 저장
    print(f"\n💾 결과 저장: {OUTPUT_PATH}")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 리포트 생성
    report = generate_report(results, taxonomy)
    print(f"📊 리포트 저장: {REPORT_PATH}")
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    # 리포트 출력
    print("\n" + report)

    if errors:
        print(f"\n⚠️  읽기 실패: {len(errors)}개")
        for e in errors:
            print(f"  {e}")

    print(f"\n✅ 완료! {len(results)}장 태깅됨")


if __name__ == "__main__":
    main()
