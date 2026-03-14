import urllib.request
import os
import time

# 두 번째 검색에서 새로 발견된 URL (기존 100개와 중복 제거)
extra_urls = [
    "https://i.pinimg.com/originals/84/49/d3/8449d3da9fc1f1d70c6c60cf301473c8.jpg",
    "https://i.pinimg.com/originals/77/fe/77/77fe77cda2cc36d57f8f5a6978bac872.jpg",
    "https://i.pinimg.com/originals/2f/61/0b/2f610b65044db65ce5e3fd9bc68a8107.jpg",
    "https://i.pinimg.com/originals/01/44/12/01441265cb95d54b6693bf433369d42d.jpg",
    "https://i.pinimg.com/originals/97/0d/ac/970dac0d3f495b0a646fb797ed308dbd.jpg",
    "https://i.pinimg.com/originals/3f/be/ac/3fbeac881f94e69fc60131366e2f19ac.jpg",
    "https://i.pinimg.com/originals/87/ea/3b/87ea3b9a1dccec72f200f8c7989d50a1.jpg",
    "https://i.pinimg.com/originals/e9/cb/73/e9cb7331ff3db6b6de4c8f4d54cf4e8c.jpg",
    "https://i.pinimg.com/originals/87/98/d1/8798d193b5b9ecbc95ccc2cb4d44cd21.jpg",
    "https://i.pinimg.com/originals/53/aa/e6/53aae6ecf350708b40c5348e3b3ba22c.jpg",
    "https://i.pinimg.com/originals/7b/68/a7/7b68a732cab9ac624037875c5f115911.jpg",
    "https://i.pinimg.com/originals/0d/77/21/0d7721be04cd69536f990da413aad566.jpg",
    "https://i.pinimg.com/originals/46/3a/80/463a80e95a2a6d9d2bf92c276beaf4d5.jpg",
    "https://i.pinimg.com/originals/dd/58/c2/dd58c2eb85955aae0752154a69fd87b3.jpg",
    "https://i.pinimg.com/originals/9f/6a/7e/9f6a7e2fc6ef92ead3fce3679e77873d.jpg",
    "https://i.pinimg.com/originals/ea/4c/e2/ea4ce2e008b05791cbb5b95853e1f69d.jpg",
    "https://i.pinimg.com/originals/ee/21/ae/ee21ae36cb3aef666b3209dcc5e61a95.jpg",
    "https://i.pinimg.com/originals/86/36/32/8636322d8e6e3ee86a504f24130f698e.jpg",
    "https://i.pinimg.com/originals/20/77/8d/20778d0e6ede29928a1bf77d39aa5756.jpg",
    "https://i.pinimg.com/originals/9d/a5/c7/9da5c7c7e0f49de6a1e243fd15d040ae.jpg",
]

save_dir = "pinterest_수집_밝은스타일"

# 이미 다운된 파일 수 확인
existing = len([f for f in os.listdir(save_dir) if f.endswith(".jpg")])
print(f"기존 파일: {existing}장")

need = 100 - existing
if need <= 0:
    print("이미 100장 이상 있습니다!")
    exit()

print(f"추가 필요: {need}장")
success = 0

for i, url in enumerate(extra_urls):
    if success >= need:
        break
    filename = f"bright_{existing + success + 1:03d}.jpg"
    filepath = os.path.join(save_dir, filename)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=10).read()
        if len(data) > 5000:
            with open(filepath, "wb") as f:
                f.write(data)
            success += 1
            print(f"  {filename} saved ({len(data)//1024}KB)")
        else:
            print(f"  {filename} too small, skipped")
    except Exception as e:
        print(f"  failed: {e}")
    time.sleep(0.3)

final = len([f for f in os.listdir(save_dir) if f.endswith(".jpg")])
print(f"\n최종 결과: {final}장 저장됨")
