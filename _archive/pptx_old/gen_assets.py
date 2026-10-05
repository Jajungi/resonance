"""Generate PNG assets for presentation (PIL)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent / "assets"
ACCENT = (44, 95, 110)
INK = (26, 26, 26)
SOFT = (244, 244, 244)
WAVE = (110, 212, 204)


def font(size):
    for name in ("malgun.ttf", "Malgun Gothic.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def logo():
    im = Image.new("RGB", (512, 512), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for r, w, a in ((160, 10, 60), (110, 12, 120), (55, 14, 255)):
        # approximate opacity by blend
        overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        color = (*ACCENT, a if a < 255 else 255)
        od.ellipse([256 - r, 256 - r, 256 + r, 256 + r], outline=color, width=w)
        im = Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB")
        d = ImageDraw.Draw(im)
    d.ellipse([238, 238, 274, 274], fill=ACCENT)
    d.arc([80, 200, 200, 312], 200, 340, fill=INK, width=6)
    d.arc([180, 200, 300, 312], 20, 160, fill=INK, width=6)
    d.arc([280, 200, 400, 312], 200, 340, fill=INK, width=6)
    d.arc([360, 200, 480, 312], 20, 160, fill=INK, width=6)
    out = BASE / "logo" / "logo.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    print("wrote", out)


def booth():
    im = Image.new("RGB", (800, 500), SOFT)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 60, 760, 440], radius=8, fill=(232, 236, 238), outline=(197, 206, 210))
    d.text((80, 80), "Community Center Lobby · 2035", fill=(138, 150, 155), font=font(20))
    d.rounded_rectangle([280, 120, 520, 400], radius=14, fill=(255, 255, 255), outline=ACCENT, width=3)
    d.rounded_rectangle([300, 145, 500, 285], radius=8, fill=(13, 26, 28))
    d.ellipse([364, 179, 436, 251], outline=WAVE, width=3)
    d.ellipse([384, 199, 416, 231], fill=(*WAVE, ))
    # chair
    d.rectangle([355, 350, 445, 364], fill=INK)
    d.rectangle([370, 310, 430, 350], outline=INK, width=3)
    d.text((330, 415), "공명 스테이션 · 1인 부스", fill=ACCENT, font=font(18))
    out = BASE / "temple" / "booth.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    print("wrote", out)


def bridge():
    im = Image.new("RGB", (512, 512), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.ellipse([186, 110, 326, 250], outline=ACCENT, width=8)
    d.arc([140, 280, 372, 420], 200, 340, fill=ACCENT, width=8)
    d.line([80, 430, 432, 430], fill=(197, 206, 210), width=4)
    d.arc([120, 390, 392, 470], 200, 340, fill=ACCENT, width=5)
    d.text((140, 460), "AI Bridge · 경청의 매개", fill=(90, 90, 90), font=font(20))
    out = BASE / "guide" / "bridge.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    print("wrote", out)


def flow():
    im = Image.new("RGB", (900, 220), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((360, 20), "내려놓음의 대화", fill=ACCENT, font=font(22))
    labels = ["앉기", "말하기", "침묵", "위로", "연대", "휘발"]
    x = 20
    for i, lab in enumerate(labels):
        w = 110 if lab == "휘발" else 120
        d.rounded_rectangle([x, 70, x + w, 140], radius=12, fill=SOFT, outline=ACCENT, width=2)
        d.text((x + w // 2 - 20, 95), lab, fill=INK, font=font(18))
        if i < len(labels) - 1:
            d.line([x + w + 2, 105, x + w + 18, 105], fill=ACCENT, width=3)
        x += w + 30
    out = BASE / "ritual" / "flow.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    print("wrote", out)


def music():
    im = Image.new("RGB", (512, 512), SOFT)
    d = ImageDraw.Draw(im)
    d.ellipse([150, 230, 250, 330], outline=ACCENT, width=8)
    d.ellipse([188, 268, 212, 292], fill=ACCENT)
    d.line([250, 280, 250, 140], fill=ACCENT, width=8)
    d.line([250, 140, 370, 110], fill=ACCENT, width=8)
    d.line([370, 110, 370, 250], fill=ACCENT, width=8)
    d.ellipse([330, 210, 410, 290], outline=ACCENT, width=8)
    d.ellipse([360, 240, 380, 260], fill=ACCENT)
    d.text((150, 400), "의례 음악 · Ambient", fill=(90, 90, 90), font=font(22))
    out = BASE / "music" / "ambient.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    print("wrote", out)


def mock_screens():
    """Fallback UI mocks if live screenshots unavailable."""
    shots = BASE / "screenshots"
    shots.mkdir(parents=True, exist_ok=True)

    # idle / start
    im = Image.new("RGB", (1280, 720), (7, 13, 15))
    d = ImageDraw.Draw(im)
    d.ellipse([540, 220, 740, 420], outline=WAVE, width=3)
    d.ellipse([590, 270, 690, 370], fill=(110, 212, 204, ))
    d.text((480, 480), "공명 스테이션", fill=(247, 250, 249), font=font(36))
    d.text((420, 540), "말해도 된다. 여기는 들어준다.", fill=(240, 194, 106), font=font(22))
    d.rounded_rectangle([460, 600, 820, 660], radius=12, outline=WAVE, width=2)
    d.text((520, 615), "자리 앉기 · 시작", fill=(247, 250, 249), font=font(22))
    im.save(shots / "01_start.png")

    # listening
    im = Image.new("RGB", (1280, 720), (7, 13, 15))
    d = ImageDraw.Draw(im)
    d.ellipse([500, 160, 780, 440], outline=WAVE, width=4)
    d.text((560, 80), "듣고 있어요", fill=WAVE, font=font(28))
    d.text((200, 500), "아들이… 전화가 많이 줄었어요. 무릎도 밤에…", fill=(247, 250, 249), font=font(26))
    d.text((200, 560), "아무한테나 이런 말 하기가… 폐가 될까 봐…", fill=(183, 196, 192), font=font(22))
    im.save(shots / "02_listen.png")

    # comfort
    im = Image.new("RGB", (1280, 720), (7, 13, 15))
    d = ImageDraw.Draw(im)
    d.text((560, 80), "응답", fill=(240, 194, 106), font=font(28))
    lines = [
        "아들이 멀어지는 것 같고, 밤마다 몸도 마음도",
        "힘드셨군요. 그 섭섭함과 그리움이 잘못이 아닙니다.",
        "",
        "그 말씀을, 여기 두고 가셔도 됩니다.",
        "오늘은 그 말을 꺼낸 것만으로도 충분합니다.",
    ]
    y = 220
    for line in lines:
        d.text((160, y), line, fill=(247, 250, 249), font=font(28))
        y += 48
    im.save(shots / "03_comfort.png")

    # resonance
    im = Image.new("RGB", (1280, 720), (7, 13, 15))
    d = ImageDraw.Draw(im)
    d.text((480, 100), "익명 연대", fill=WAVE, font=font(28))
    d.rounded_rectangle([180, 220, 1100, 420], radius=16, outline=WAVE, width=2)
    d.text((220, 280), "밤마다 다리가 저려서… 잠이 안 와요.", fill=(247, 250, 249), font=font(26))
    d.text((220, 340), "그래도 오늘… 여기 와서… 말했습니다.", fill=(183, 196, 192), font=font(24))
    d.text((220, 500), "나만… 그런 게 아니구나…", fill=(240, 194, 106), font=font(24))
    im.save(shots / "04_resonance.png")
    print("wrote mock screenshots")


if __name__ == "__main__":
    logo()
    booth()
    bridge()
    flow()
    music()
    mock_screens()
