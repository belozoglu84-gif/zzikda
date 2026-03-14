"""
새우볼 완자탕 20장 일괄 생성 스크립트 - 김현경 작가 스타일
"""
# /// script
# requires-python = ">=3.10"
# dependencies = ["google-genai>=1.0.0", "Pillow>=10.0.0"]
# ///

import os
import sys
import time
import subprocess
from pathlib import Path

STYLE_BASE = (
    "Professional Korean food photography, "
    "soft back-left side lighting from studio strobe with natural light fill, "
    "warm ~4600K color temperature, Kodak Portra 400 film style, "
    "desaturated and muted tones, lifted blacks with cinematic matte finish, "
    "subtle warm amber undertone, analog film grain, "
    "very sharp focus on food texture, shallow depth of field, "
    "rustic dark wooden table, artisanal ceramic tableware, "
    "warm cozy 정갈한 Kinfolk magazine editorial style, 8K resolution."
)

# 20가지 변주 — 구도/소품/배경/앵글을 조금씩 다르게
VARIATIONS = [
    # 1~5: 각도 변주
    {
        "desc": "45도 하이앵글 정통샷, 돌솥에 담긴 새우볼 완자탕",
        "scene": "Saewubol Wanjatang (Korean shrimp ball soup with vegetable broth) in a matte black stone pot (dolsot), shot from 45-degree high angle. Golden broth, round golden-brown shrimp balls, enoki mushrooms, green onion, tofu cubes. Chopsticks resting on the side.",
        "setting": "Dark wooden tray on rustic oak table."
    },
    {
        "desc": "30도 로우앵글, 국물이 보이는 깊이감",
        "scene": "Saewubol Wanjatang in a deep ceramic earthenware bowl, shot from 30-degree low angle showing depth of the broth. Steaming hot soup, glistening shrimp balls, fresh green onion garnish, sesame oil droplets on surface.",
        "setting": "Linen napkin beside bowl, wooden spoon on side."
    },
    {
        "desc": "탑다운 플랫레이 정면샷",
        "scene": "Saewubol Wanjatang flat lay top-down view in a wide shallow ceramic bowl. Symmetrical arrangement of 5 shrimp balls, shiitake mushrooms, watercress, thin rice noodles. Clear amber broth.",
        "setting": "Dark slate stone surface, white ceramic spoon."
    },
    {
        "desc": "45도 클로즈업, 새우볼 질감 극대화",
        "scene": "Extreme close-up of Saewubol Wanjatang, 45-degree angle, macro shot of 2-3 golden shrimp balls in simmering broth. Steam wisps visible, crispy texture detail on shrimp balls, sesame seeds on top.",
        "setting": "Black iron pot, bamboo chopsticks, dark stone surface."
    },
    {
        "desc": "60도 앵글, 세트 구성 풀샷",
        "scene": "Saewubol Wanjatang full set meal from 60-degree angle. Main stone pot with soup, small rice bowl, kimchi side dish, seasoned vegetables. Complete Korean meal composition.",
        "setting": "Dark wood table, folded cloth napkin, wooden tray."
    },
    # 6~10: 그릇/소품 변주
    {
        "desc": "백자 흰 사기그릇, 미니멀 스타일",
        "scene": "Saewubol Wanjatang in elegant white porcelain bowl with delicate blue patterns. Clean minimal composition. Three perfect shrimp balls, clear golden broth, microgreens garnish, drizzle of sesame oil.",
        "setting": "White marble surface, silver spoon, folded white linen."
    },
    {
        "desc": "뚝배기 전통 스타일",
        "scene": "Saewubol Wanjatang in traditional Korean ttukbaegi (earthenware pot), still bubbling at the edges. Rustic and hearty presentation. Large shrimp balls, glass noodles, crown daisy herb.",
        "setting": "Wooden trivet under pot, Korean newspaper underneath, aged wooden table."
    },
    {
        "desc": "구리 냄비, 프리미엄 스타일",
        "scene": "Saewubol Wanjatang in a small copper pot, premium fine dining style. Precisely arranged shrimp balls, julienned vegetables, delicate herb oil drops on broth surface, edible flowers.",
        "setting": "Charcoal grey stone surface, copper ladle, fine linen."
    },
    {
        "desc": "대나무 찜기 스타일, 찜 완자",
        "scene": "Steamed Saewubol (shrimp balls) in bamboo steamer basket, no broth version. Plump white shrimp balls with visible shrimp texture, garnished with chili threads and sesame seeds. Dipping sauce in small dish.",
        "setting": "Dark wood surface, steam rising, bamboo chopsticks."
    },
    {
        "desc": "유리 그릇, 맑은 국물 투명감",
        "scene": "Saewubol Wanjatang in clear glass bowl showcasing crystal-clear golden broth. Shrimp balls visible from the side, floating mushrooms, thin glass noodles, chive garnish.",
        "setting": "Light grey linen, silver spoon, minimal modern setting."
    },
    # 11~15: 계절/분위기 변주
    {
        "desc": "겨울 분위기, 김이 모락모락",
        "scene": "Saewubol Wanjatang in winter setting, heavy steam rising dramatically. Dark and moody atmosphere, black ceramic bowl, golden broth glowing, 3 large shrimp balls, dried jujube and ginkgo nuts.",
        "setting": "Dark charcoal surface, droplets of condensation, warm candlelight feeling."
    },
    {
        "desc": "가을 분위기, 따뜻한 어스톤",
        "scene": "Saewubol Wanjatang with autumn mood. Amber and brown tones, earthy mushroom variety (shiitake, oyster, king oyster), rich golden broth with sesame oil, chestnuts and pine nuts.",
        "setting": "Oak cutting board, fallen dry leaves as decoration, warm earth tones."
    },
    {
        "desc": "봄 분위기, 나물 곁들임",
        "scene": "Saewubol Wanjatang with spring vegetables. Light clear broth, tender spring greens (spinach, watercress), pale green shrimp balls with herbs inside, pea shoots on top.",
        "setting": "Light celadon ceramic, pale linen, fresh minimal spring aesthetic."
    },
    {
        "desc": "야간 촬영 분위기, 캔들라이트",
        "scene": "Saewubol Wanjatang in intimate evening atmosphere. Deep rich broth, candlelight warmth on ceramic bowl, dramatic shadows, 4 shrimp balls arranged beautifully, gold garnish.",
        "setting": "Very dark wooden table, candle flame blur in background, chopsticks."
    },
    {
        "desc": "모던 한식 레스토랑 스타일",
        "scene": "Saewubol Wanjatang plated as modern Korean fine dining. Asymmetric composition, 5 precisely placed shrimp balls, consomme-clear broth, microgreens, edible gold flakes, chive oil drizzle.",
        "setting": "Matte black slate, minimalist white ceramic, silver tongs."
    },
    # 16~20: 액션/스토리텔링 변주
    {
        "desc": "젓가락으로 집는 액션샷",
        "scene": "Saewubol Wanjatang action shot — wooden chopsticks lifting one golden shrimp ball from the broth, broth dripping. Motion blur on chopsticks, sharp focus on shrimp ball and steam.",
        "setting": "Dark iron pot, wooden tray, atmospheric moody lighting."
    },
    {
        "desc": "숟가락 퍼올리는 국물샷",
        "scene": "Saewubol Wanjatang action — ceramic spoon scooping golden broth with a shrimp ball, showing the rich soup texture. Close-up at 45-degree angle, steam and motion.",
        "setting": "Black ceramic bowl, rustic wooden surface, linen cloth."
    },
    {
        "desc": "2인상 세팅, 테이블 전체 구성",
        "scene": "Saewubol Wanjatang table setting for two. Two matching earthenware pots side by side, shared side dishes (kimchi, namul, rice), wooden chopsticks, hand visible reaching for bowl.",
        "setting": "Full dark wooden dining table, Korean traditional table setting."
    },
    {
        "desc": "재료 플랫레이, 요리 전 준비",
        "scene": "Saewubol Wanjatang ingredients flat lay. Raw shrimp, ground pork, vegetables, seasonings arranged artfully around a center bowl of finished soup. Recipe-style composition.",
        "setting": "White marble surface, fresh herbs, premium ingredient styling."
    },
    {
        "desc": "완성된 뚝배기, 밥과 함께 풀세트",
        "scene": "Saewubol Wanjatang complete meal set. Bubbling ttukbaegi (traditional Korean earthenware), bowl of white rice, assorted banchan side dishes, neatly arranged. Homemade warmth.",
        "setting": "Vintage wooden tray, aged oak table, cozy home kitchen atmosphere."
    },
]

OUTPUT_DIR = Path("c:/claudcode-work/chef-photo/완자탕")
SKILL_SCRIPT = Path.home() / ".claude/skills/nano-banana-pro/scripts/generate_image.py"

def generate_one(idx: int, variation: dict) -> bool:
    filename = OUTPUT_DIR / f"완자탕_{idx:02d}.png"
    prompt = f"{variation['scene']} {variation['setting']} {STYLE_BASE}"

    cmd = [
        "uv", "run", str(SKILL_SCRIPT),
        "--prompt", prompt,
        "--filename", str(filename),
        "--resolution", "2K"
    ]

    print(f"[{idx:02d}/20] {variation['desc']} 생성 중...", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

    if filename.exists():
        print(f"  -> 저장 완료: {filename.name}", flush=True)
        return True
    else:
        print(f"  -> 실패: {result.stderr[:200]}", flush=True)
        return False

success = 0
for i, variation in enumerate(VARIATIONS, 1):
    ok = generate_one(i, variation)
    if ok:
        success += 1
    time.sleep(3)  # API rate limit 방지

print(f"\n완료: {success}/20장 생성됨 -> {OUTPUT_DIR}")
