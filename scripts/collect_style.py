"""
collect_style.py - Unsplash/Pexels API로 스타일별 음식사진 자동 수집

사용법:
    uv run collect_style.py --style clean-minimal --source unsplash --count 80
    uv run collect_style.py --style warm-rustic --source pexels --count 100
    uv run collect_style.py --style vibrant-pop --source both --count 150
    uv run collect_style.py --list-styles  # 사용 가능한 스타일 목록 보기

환경변수:
    UNSPLASH_ACCESS_KEY - Unsplash API 키
    PEXELS_API_KEY - Pexels API 키
"""

# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27.0", "rich>=13.0.0"]
# ///

import httpx
import os
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path


# ============================================================
# 스타일별 검색 키워드 프리셋
# 모든 키워드에 음식 관련 단어 포함 (하늘/풍경 사진 방지)
# ============================================================
STYLE_PRESETS = {
    "clean-minimal": {
        "name": "클린 미니멀",
        "description": "흰 배경, 최소 소품, 높은 선명도 — 배달앱/메뉴판용",
        "keywords": [
            "minimal food photography white background",
            "clean food plating minimal style",
            "food dish white plate simple",
            "minimalist food styling restaurant menu",
            "food product photography clean background",
            "simple food presentation white surface",
        ],
    },
    "warm-rustic": {
        "name": "따뜻한 러스틱",
        "description": "나무/천 소재, 웜톤, 킨포크 감성 — 가정식/한식당용",
        "keywords": [
            "rustic food photography wooden table",
            "warm food styling homemade dish",
            "cozy food photography natural light",
            "kinfolk food photography warm tones",
            "food on wooden board rustic setting",
            "homestyle cooking food photography warm",
        ],
    },
    "vibrant-pop": {
        "name": "비비드 팝",
        "description": "높은 채도, 선명한 색감 — SNS 마케팅용",
        "keywords": [
            "vibrant colorful food photography",
            "bright food styling saturated colors",
            "colorful dish food photography pop",
            "food photography vivid bold colors",
            "eye catching food plate bright",
            "food photography high saturation colorful",
        ],
    },
    "bright-airy": {
        "name": "밝은 에어리",
        "description": "밝은 배경, 자연광, 높은 명도 — 카페/브런치용",
        "keywords": [
            "bright airy food photography",
            "light food styling natural daylight",
            "food photography bright white background",
            "cafe food photography bright natural light",
            "brunch food styling airy fresh",
            "food plate bright soft lighting",
        ],
    },
    "dark-moody": {
        "name": "다크 무디",
        "description": "어두운 배경, 드라마틱 조명 — 고급 레스토랑/바용",
        "keywords": [
            "dark moody food photography",
            "dramatic lighting food styling dark",
            "food photography dark background chiaroscuro",
            "low key food photography restaurant",
            "moody food plating dark tones",
            "food dish dramatic shadow dark",
        ],
    },
    "film-vintage": {
        "name": "필름 빈티지",
        "description": "필름 그레인, 바랜 색감, 레트로 — 감성 카페용",
        "keywords": [
            "vintage food photography film grain",
            "retro food styling faded colors",
            "film photography food analog style",
            "food photography nostalgic vintage tone",
            "cafe food retro vintage aesthetic",
            "food photography warm film look",
        ],
    },
    "overhead-editorial": {
        "name": "오버헤드 에디토리얼",
        "description": "탑다운 구도, 잡지급 스타일링 — 레시피/쿡북용",
        "keywords": [
            "overhead food photography flat lay",
            "top down food styling editorial",
            "food flat lay magazine style",
            "birds eye view food photography",
            "food photography overhead styled spread",
            "food recipe flat lay top view",
        ],
    },
    "street-casual": {
        "name": "스트릿 캐주얼",
        "description": "실제 식당 현장, 자연스러운 연출 — 맛집 리뷰용",
        "keywords": [
            "street food photography casual",
            "restaurant food real setting casual",
            "food photography authentic dining scene",
            "casual food styling real restaurant",
            "food photography candid dining experience",
            "local restaurant food authentic style",
        ],
    },
}


def search_unsplash(query: str, page: int, per_page: int, api_key: str) -> list[dict]:
    """Unsplash API로 사진 검색"""
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "page": page,
        "per_page": per_page,
        "orientation": "landscape",  # 음식사진은 보통 가로
    }
    headers = {"Authorization": f"Client-ID {api_key}"}

    resp = httpx.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for photo in data.get("results", []):
        results.append({
            "id": photo["id"],
            "url": photo["urls"]["regular"],  # 1080px 너비
            "full_url": photo["urls"]["full"],
            "width": photo["width"],
            "height": photo["height"],
            "photographer": photo["user"]["name"],
            "photographer_url": photo["user"]["links"]["html"],
            "source": "unsplash",
            "source_url": photo["links"]["html"],
            "license": "Unsplash License (무료 상업 이용 가능)",
        })
    return results


def search_pexels(query: str, page: int, per_page: int, api_key: str) -> list[dict]:
    """Pexels API로 사진 검색"""
    url = "https://api.pexels.com/v1/search"
    params = {
        "query": query,
        "page": page,
        "per_page": per_page,
        "orientation": "landscape",
    }
    headers = {"Authorization": api_key}

    resp = httpx.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for photo in data.get("photos", []):
        results.append({
            "id": str(photo["id"]),
            "url": photo["src"]["large"],  # 940px 너비
            "full_url": photo["src"]["original"],
            "width": photo["width"],
            "height": photo["height"],
            "photographer": photo["photographer"],
            "photographer_url": photo["photographer_url"],
            "source": "pexels",
            "source_url": photo["url"],
            "license": "Pexels License (무료 상업 이용 가능)",
        })
    return results


def download_image(url: str, filepath: Path) -> bool:
    """이미지 다운로드"""
    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        data = resp.content
        if len(data) < 10000:  # 10KB 미만이면 유효하지 않은 이미지
            return False
        filepath.write_bytes(data)
        return True
    except Exception:
        return False


def get_url_hash(url: str) -> str:
    """URL 기반 해시로 중복 방지"""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def main():
    parser = argparse.ArgumentParser(description="스타일별 음식사진 자동 수집")
    parser.add_argument("--style", type=str, help="수집할 스타일 (예: clean-minimal)")
    parser.add_argument("--source", choices=["unsplash", "pexels", "both"], default="both", help="수집 소스 (기본: both)")
    parser.add_argument("--count", type=int, default=100, help="수집 목표 수량 (기본: 100)")
    parser.add_argument("--min-resolution", type=int, default=1000, help="최소 해상도 (기본: 1000px)")
    parser.add_argument("--output-dir", type=str, help="저장 폴더 (기본: 수집_{스타일명})")
    parser.add_argument("--list-styles", action="store_true", help="사용 가능한 스타일 목록 보기")
    args = parser.parse_args()

    # 스타일 목록 보기
    if args.list_styles:
        print("\n사용 가능한 스타일:")
        print("-" * 60)
        for code, info in STYLE_PRESETS.items():
            print(f"  {code:25s} {info['name']} — {info['description']}")
        print()
        return

    if not args.style:
        print("오류: --style 옵션을 지정해주세요. (--list-styles로 목록 확인)")
        sys.exit(1)

    if args.style not in STYLE_PRESETS:
        print(f"오류: '{args.style}'은 없는 스타일입니다.")
        print("사용 가능:", ", ".join(STYLE_PRESETS.keys()))
        sys.exit(1)

    # API 키 확인
    unsplash_key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    pexels_key = os.environ.get("PEXELS_API_KEY", "")

    sources = []
    if args.source in ("unsplash", "both"):
        if not unsplash_key:
            print("경고: UNSPLASH_ACCESS_KEY 환경변수가 없습니다. Unsplash 건너뜀.")
        else:
            sources.append("unsplash")

    if args.source in ("pexels", "both"):
        if not pexels_key:
            print("경고: PEXELS_API_KEY 환경변수가 없습니다. Pexels 건너뜀.")
        else:
            sources.append("pexels")

    if not sources:
        print("오류: 사용 가능한 API 소스가 없습니다. 환경변수를 설정해주세요.")
        print("  set UNSPLASH_ACCESS_KEY=your_key")
        print("  set PEXELS_API_KEY=your_key")
        sys.exit(1)

    style = STYLE_PRESETS[args.style]
    output_dir = Path(args.output_dir or f"수집_{args.style}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f" 스타일: {style['name']} ({args.style})")
    print(f" 소스: {', '.join(sources)}")
    print(f" 목표: {args.count}장")
    print(f" 저장: {output_dir}")
    print(f"{'='*60}\n")

    # 검색 및 수집
    all_photos: list[dict] = []
    seen_hashes: set[str] = set()
    keywords = style["keywords"]

    for source in sources:
        print(f"\n[{source.upper()}] 검색 시작...")

        for ki, keyword in enumerate(keywords):
            # 소스별 목표량 분배
            target_per_source = args.count // len(sources)
            if len(all_photos) >= args.count:
                break

            page = 1
            per_page = 30

            while len(all_photos) < args.count and page <= 5:  # 최대 5페이지
                print(f"  키워드 [{ki+1}/{len(keywords)}] '{keyword}' (페이지 {page})...")

                try:
                    if source == "unsplash":
                        results = search_unsplash(keyword, page, per_page, unsplash_key)
                        # Unsplash 속도 제한: 50회/시간 → 안전하게 3초 간격
                        time.sleep(3)
                    else:
                        results = search_pexels(keyword, page, per_page, pexels_key)
                        # Pexels 속도 제한: 200회/시간 → 2초 간격
                        time.sleep(2)
                except httpx.HTTPStatusError as e:
                    print(f"    API 오류: {e.response.status_code} - {e.response.text[:100]}")
                    if e.response.status_code == 429:
                        print("    속도 제한 도달. 60초 대기...")
                        time.sleep(60)
                    break
                except Exception as e:
                    print(f"    요청 실패: {e}")
                    break

                if not results:
                    break

                # 중복 제거 및 해상도 필터
                added = 0
                for photo in results:
                    url_hash = get_url_hash(photo["url"])
                    if url_hash in seen_hashes:
                        continue
                    if photo["width"] < args.min_resolution and photo["height"] < args.min_resolution:
                        continue

                    seen_hashes.add(url_hash)
                    photo["url_hash"] = url_hash
                    photo["search_keyword"] = keyword
                    all_photos.append(photo)
                    added += 1

                    if len(all_photos) >= args.count:
                        break

                print(f"    +{added}장 (총 {len(all_photos)}장)")

                if added == 0 or len(results) < per_page:
                    break  # 더 이상 결과 없음

                page += 1

    print(f"\n검색 완료: 총 {len(all_photos)}장 후보 확보")

    # 다운로드
    print(f"\n이미지 다운로드 시작...")
    success = 0
    fail = 0

    for i, photo in enumerate(all_photos, 1):
        filename = f"{args.style}_{i:03d}.jpg"
        filepath = output_dir / filename
        photo["local_filename"] = filename

        if filepath.exists():
            print(f"  [{i}/{len(all_photos)}] {filename} — 이미 존재, 건너뜀")
            success += 1
            continue

        ok = download_image(photo["url"], filepath)
        if ok:
            success += 1
            if i % 10 == 0 or i == len(all_photos):
                print(f"  [{i}/{len(all_photos)}] 다운로드 중... ({success}장 완료)")
        else:
            fail += 1
            print(f"  [{i}/{len(all_photos)}] {filename} — 다운로드 실패")

        time.sleep(0.3)

    # 메타데이터 저장
    metadata_path = output_dir / "_metadata.json"
    metadata = {
        "style": args.style,
        "style_name": style["name"],
        "description": style["description"],
        "sources": sources,
        "total_collected": success,
        "total_failed": fail,
        "min_resolution": args.min_resolution,
        "photos": all_photos,
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f" 수집 완료!")
    print(f"  성공: {success}장")
    print(f"  실패: {fail}장")
    print(f"  저장 폴더: {output_dir}")
    print(f"  메타데이터: {metadata_path}")
    print(f"{'='*60}\n")

    print("다음 단계:")
    print(f"  uv run filter_photos.py --folder {output_dir} --style {args.style}")


if __name__ == "__main__":
    main()
