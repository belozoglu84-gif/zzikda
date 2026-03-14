import urllib.request
import os
import time

urls = [
    "https://i.pinimg.com/originals/2d/74/b9/2d74b9e7ceaf43e917d612171eace687.jpg",
    "https://i.pinimg.com/originals/2b/33/89/2b3389acbe5f7228c98ba85d5e63b785.jpg",
    "https://i.pinimg.com/originals/df/0d/6a/df0d6adcce79a70370a5e356e88b3ef1.jpg",
    "https://i.pinimg.com/originals/76/ec/68/76ec6819ddbcb91aafa2f25a308c2a54.jpg",
    "https://i.pinimg.com/originals/f8/84/ea/f884eaad66d865593465676ee791eedf.jpg",
    "https://i.pinimg.com/originals/9c/c1/ff/9cc1ff0761064167d624c7229a8690a6.jpg",
    "https://i.pinimg.com/originals/a0/fe/12/a0fe120599e72286171d732a78d14317.jpg",
    "https://i.pinimg.com/originals/ee/62/58/ee625861b44cc99cccda2d65072717d9.jpg",
    "https://i.pinimg.com/originals/df/15/14/df1514f5db3e1c2588506fe01a67e720.jpg",
    "https://i.pinimg.com/originals/4a/c5/2a/4ac52a2adb804156be33df5e85b5e2cb.jpg",
    "https://i.pinimg.com/originals/c9/3a/d0/c93ad0c0ad647b38ad2c8ec4ac1ea269.jpg",
    "https://i.pinimg.com/originals/af/5c/91/af5c91e676077f6ddd335e29f949f666.jpg",
    "https://i.pinimg.com/originals/b2/d6/2a/b2d62a92b89fdf4a11f7038719aa566c.jpg",
    "https://i.pinimg.com/originals/c8/b6/01/c8b601d6ee37a1c52073835ab2962aef.jpg",
    "https://i.pinimg.com/originals/23/06/25/23062585d7b0b6e15e8c3873eaa9b0be.jpg",
    "https://i.pinimg.com/originals/60/58/9e/60589e6d272150096024c133cb7be11e.jpg",
    "https://i.pinimg.com/originals/c8/71/00/c8710043090f3e08f11e2cba3372df53.jpg",
    "https://i.pinimg.com/originals/1e/9d/07/1e9d07cb1bf74ae8e4da616e17a579d8.jpg",
    "https://i.pinimg.com/originals/35/11/68/35116884d117438413b6100fe8ac4e8e.jpg",
    "https://i.pinimg.com/originals/d5/3e/df/d53edfba5ab82bb6024195cb99b249fc.jpg",
    "https://i.pinimg.com/originals/f2/99/57/f2995715037d6bc6938fe81cda0ae639.jpg",
    "https://i.pinimg.com/originals/2d/12/ad/2d12ad26a944eb80482bbd8b13b5af08.jpg",
    "https://i.pinimg.com/originals/c0/75/05/c07505ead38b02be579ef717f5a2f37a.jpg",
    "https://i.pinimg.com/originals/ea/4c/e2/ea4ce2e008b05791cbb5b95853e1f69d.jpg",
    "https://i.pinimg.com/originals/46/3a/80/463a80e95a2a6d9d2bf92c276beaf4d5.jpg",
    "https://i.pinimg.com/originals/dd/58/c2/dd58c2eb85955aae0752154a69fd87b3.jpg",
    "https://i.pinimg.com/originals/4a/56/94/4a569441852b204582702879a51dd2be.jpg",
    "https://i.pinimg.com/originals/9f/6a/7e/9f6a7e2fc6ef92ead3fce3679e77873d.jpg",
    "https://i.pinimg.com/originals/f4/09/22/f40922d22d2578d15c84197f523b5fd8.jpg",
    "https://i.pinimg.com/originals/d4/19/51/d41951f742357d6ce251384103068084.jpg",
    "https://i.pinimg.com/originals/ee/21/ae/ee21ae36cb3aef666b3209dcc5e61a95.jpg",
    "https://i.pinimg.com/originals/a3/de/e7/a3dee7975fd71431a518c1bee3cd1032.jpg",
    "https://i.pinimg.com/originals/86/36/32/8636322d8e6e3ee86a504f24130f698e.jpg",
    "https://i.pinimg.com/originals/20/77/8d/20778d0e6ede29928a1bf77d39aa5756.jpg",
    "https://i.pinimg.com/originals/87/cf/9c/87cf9cea68d42ddc97c819ee8c444ccc.jpg",
    "https://i.pinimg.com/originals/a9/61/31/a961318dcb0a00847b19be2a6a216fe7.jpg",
    "https://i.pinimg.com/originals/d1/56/4f/d1564fd698d4fc093dc1022ae1a0d527.jpg",
    "https://i.pinimg.com/originals/fa/02/d9/fa02d923bf5e1862a39f7669ed3cbe76.jpg",
    "https://i.pinimg.com/originals/9d/a5/c7/9da5c7c7e0f49de6a1e243fd15d040ae.jpg",
    "https://i.pinimg.com/originals/6c/13/50/6c1350181f25b39f7bd7133cd0af4498.jpg",
    "https://i.pinimg.com/originals/52/fd/33/52fd33861940e1f854569f6c2a8114c1.jpg",
    "https://i.pinimg.com/originals/4c/85/e4/4c85e47a67b1517520f6cb6aab5784e8.jpg",
    "https://i.pinimg.com/originals/c4/2e/c8/c42ec8cf4de414605a0b634528c8a3b3.jpg",
    "https://i.pinimg.com/originals/f9/6d/60/f96d6018db10b8e6386581102ba3624a.jpg",
    "https://i.pinimg.com/originals/1e/cc/5e/1ecc5e5cc0fbf47179b3a56fabdf9606.jpg",
    "https://i.pinimg.com/originals/34/d0/a0/34d0a0e8dfa8cd0087b1471ae49c92dc.jpg",
    "https://i.pinimg.com/originals/e2/30/eb/e230ebc5b72fecfb8d5d6e4d4a4d55f6.jpg",
    "https://i.pinimg.com/originals/16/0e/cb/160ecb21a99181e26abdaf5e11699cc1.jpg",
    "https://i.pinimg.com/originals/02/8a/fa/028afa361e514092d8bf6c17db8098a8.jpg",
    "https://i.pinimg.com/originals/bd/64/a6/bd64a664e647262f6b6acca1a9ee11d7.jpg",
    "https://i.pinimg.com/originals/95/f7/b0/95f7b014fa2a800605a1867ba823d644.jpg",
    "https://i.pinimg.com/originals/3b/be/94/3bbe9427c5ff24cfc8ef09db69276e4e.jpg",
    "https://i.pinimg.com/originals/42/33/22/423322b025d0423d9a40559c64d481d5.jpg",
    "https://i.pinimg.com/originals/4a/95/dd/4a95dda58b7d9eaafb241d43d959d140.jpg",
    "https://i.pinimg.com/originals/ac/59/de/ac59de90612ceebaade18729d29a9a3b.jpg",
    "https://i.pinimg.com/originals/9e/93/9c/9e939c3b7cdc3f9b70cc4157b7df8707.jpg",
    "https://i.pinimg.com/originals/0c/91/97/0c919713f159b8fdbd8b72aafdeff8b8.jpg",
    "https://i.pinimg.com/originals/4a/a0/5e/4aa05e26284660da4a87a26393949cb0.jpg",
    "https://i.pinimg.com/originals/cd/bf/53/cdbf53fd40e46fc352d3d6130fc60de1.jpg",
    "https://i.pinimg.com/originals/f8/de/c5/f8dec5f8e9ea30b2f1e2c033efb9512e.jpg",
    "https://i.pinimg.com/originals/17/25/df/1725dfef017ece00f518dbb53288a135.jpg",
    "https://i.pinimg.com/originals/bd/7d/11/bd7d11c88b87589ed06eb7da03b2a341.jpg",
    "https://i.pinimg.com/originals/47/58/2b/47582b039374642ba8aa11be3203a58f.jpg",
    "https://i.pinimg.com/originals/7e/07/cd/7e07cd6ec4344a24f0a474f782053bd9.jpg",
    "https://i.pinimg.com/originals/8d/c4/1a/8dc41a73c20c8df37f848a7bb592dafc.jpg",
    "https://i.pinimg.com/originals/7f/a7/9d/7fa79dd27bfb395d15fbe0ee377b8b64.jpg",
    "https://i.pinimg.com/originals/7c/57/28/7c5728d851d6edbae4c8648092ccab22.jpg",
    "https://i.pinimg.com/originals/c5/89/26/c589263c6ca52f724a21181e729ef471.jpg",
    "https://i.pinimg.com/originals/e9/9e/03/e99e03dfb64bec5a1a3b639b78ffa938.jpg",
    "https://i.pinimg.com/originals/94/52/ca/9452caf58a7497f7d13f8db1ccd5416e.jpg",
    "https://i.pinimg.com/originals/9a/9f/24/9a9f244214fc2bf70b9662edac34ca3a.jpg",
    "https://i.pinimg.com/originals/9d/6e/5a/9d6e5a7bfd40ca3737b8ae0f0abd88fe.jpg",
    "https://i.pinimg.com/originals/1a/48/19/1a4819e8671336b3a6bb9b722d772637.jpg",
    "https://i.pinimg.com/originals/57/74/fb/5774fba287530d68d565690f4f1b81c3.jpg",
    "https://i.pinimg.com/originals/2e/f6/eb/2ef6eb586f9b058a15b916f923a0f552.jpg",
    "https://i.pinimg.com/originals/34/7f/98/347f9846f86d0d448b96e6fa5aa84ae1.jpg",
    "https://i.pinimg.com/originals/f8/bc/9b/f8bc9b97e7ec53014d575f525f81d745.jpg",
    "https://i.pinimg.com/originals/0a/64/66/0a6466045522e5b7274ff795f21d0832.jpg",
    "https://i.pinimg.com/originals/64/b1/7c/64b17c3658c198ed633a0e4dbbd68663.jpg",
    "https://i.pinimg.com/originals/cf/db/31/cfdb31cd2115848946677ae37a3a0982.jpg",
    "https://i.pinimg.com/originals/38/6b/3a/386b3ad57b10549e7ace3b5856ac23ec.jpg",
    "https://i.pinimg.com/originals/2b/b0/7f/2bb07f178dd40db9fd6e8d22200f3ec6.jpg",
    "https://i.pinimg.com/originals/1c/7e/51/1c7e514061506b4488ec28c32a652244.jpg",
    "https://i.pinimg.com/originals/23/3f/1a/233f1ae1f7f99405706b9091d67ec438.jpg",
    "https://i.pinimg.com/originals/b5/7f/83/b57f830e07b65725108f2420a5cec382.jpg",
    "https://i.pinimg.com/originals/7d/5e/1f/7d5e1f2abb8374c50d27fc12fd6010bc.jpg",
    "https://i.pinimg.com/originals/82/c6/4c/82c64cd34997af90b9438df5f5337891.jpg",
    "https://i.pinimg.com/originals/48/fc/66/48fc66158ff6e7a6af0c4312ee692d78.jpg",
    "https://i.pinimg.com/originals/f7/00/ea/f700ea05cf78a4b82176f432acf96a98.jpg",
    "https://i.pinimg.com/originals/1a/2a/47/1a2a47997d2898eebff37552ea904055.jpg",
    "https://i.pinimg.com/originals/7d/96/8a/7d968ad06351ddd97a462966f4869b93.jpg",
    "https://i.pinimg.com/videos/thumbnails/originals/7d/6f/f9/7d6ff95f924b5388f224eab1e0741fb8.0000000.jpg",
    "https://i.pinimg.com/originals/b8/9e/01/b89e01ca8b07945be63b7fa0e5f24a09.jpg",
    "https://i.pinimg.com/originals/e0/3b/18/e03b188e99013bfd3e5de02b41377787.jpg",
    "https://i.pinimg.com/originals/e4/67/cc/e467ccc6849a9a9fc5ad7068de6c04c4.jpg",
    "https://i.pinimg.com/originals/fe/b1/99/feb199aa0236407769a97cbba9ff41d2.jpg",
    "https://i.pinimg.com/originals/07/bc/d8/07bcd84bb82b30354025eb9881d4f048.jpg",
    "https://i.pinimg.com/originals/21/36/6e/21366e1c08a32a59f61727e1c2536f13.jpg",
    "https://i.pinimg.com/originals/b3/3e/24/b33e244bbfc547d63f70968c849941f5.jpg",
    "https://i.pinimg.com/originals/b6/26/45/b626457c17cbce0d55d1447eed75cf8b.jpg",
]

save_dir = "pinterest_수집_밝은스타일"
os.makedirs(save_dir, exist_ok=True)

success = 0
fail = 0

for i, url in enumerate(urls, 1):
    filename = f"bright_{i:03d}.jpg"
    filepath = os.path.join(save_dir, filename)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=10).read()
        if len(data) > 5000:
            with open(filepath, "wb") as f:
                f.write(data)
            success += 1
            if i % 10 == 0:
                print(f"{i}/100 done... ({success} saved)")
        else:
            fail += 1
            print(f"{i}: too small ({len(data)} bytes), skipped")
    except Exception as e:
        fail += 1
        print(f"{i}: failed - {e}")
    time.sleep(0.3)

print(f"\nComplete: {success} saved, {fail} failed")
