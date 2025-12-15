import os
import random
import requests # We need this to talk to Telegram
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
BACKGROUND_FILE = "background.mp4" 
FONT_FILE = "font.ttf"
OUTPUT_FILE = "daily_short.mp4"

# --- STEP 1: MATH LOGIC ENGINE ---
def generate_problem():
    if random.random() > 0.5:
        # Multiplication Trap
        a = random.randint(5, 15); b = random.randint(5, 10); c = random.randint(2, 5)
        equation_visual = f"{a} + {b} x {c} = ?"
        correct = a + (b * c)
        trap = (a + b) * c
    else:
        # Division Trap
        b = random.randint(2, 5)
        sum_cd = random.randint(2, 5)
        a = b * random.randint(2, 6)
        c = random.randint(1, sum_cd - 1); d = sum_cd - c
        
        equation_visual = f"{a} ÷ {b}({c} + {d}) = ?"
        correct = (a // b) * sum_cd
        if (b * sum_cd) != 0 and a % (b * sum_cd) == 0: trap = a // (b * sum_cd)
        else: trap = correct - random.choice([1, 10, 5])

    if random.random() > 0.5:
        return equation_visual, str(correct), str(trap), "A"
    else:
        return equation_visual, str(trap), str(correct), "B"

# --- STEP 2: METADATA & TELEGRAM SENDER ---
def get_metadata_text(equation, correct_letter):
    titles = [
        f"Can you solve {equation} 🧠 #math #shorts",
        f"Most Adults Fail: {equation} 😱 #puzzle",
        f"Calculators get this WRONG! {equation} 🚫",
        f"Blue Pill or Red Pill? {equation} 💊"
    ]
    title = random.choice(titles)
    
    tags = (
        f"math, maths, pemdas, bodmas, iq test, brain teaser, puzzle, "
        f"viral, shorts, {equation.replace(' ', '')}"
    )

    # This is the message you will receive on Telegram
    caption = f"{title}\n\n👇 DESCRIPTION:\n🧠 Daily Math Challenge!\nCan you solve: {equation}\n\n👇 VOTE: Team Blue (Left) or Red (Right)?\n\nCorrect Answer: Option {correct_letter}\n\n👇 TAGS:\n{tags}"
    return caption

def send_to_telegram(video_path, caption):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram keys not found. Skipping upload.")
        return

    url = f"https://api.telegram.org/bot{token}/sendVideo"
    
    print("Sending video to Telegram...")
    with open(video_path, "rb") as video:
        payload = {"chat_id": chat_id, "caption": caption}
        files = {"video": video}
        try:
            r = requests.post(url, data=payload, files=files)
            if r.status_code == 200:
                print("✅ Sent to Telegram successfully!")
            else:
                print(f"❌ Telegram Error: {r.text}")
        except Exception as e:
            print(f"❌ Failed to send: {e}")

# --- STEP 3: VISUAL ENGINE ---
def create_placed_text(text, bg_w, bg_h, target_x, target_y, font_size):
    img = Image.new('RGBA', (bg_w, bg_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype(FONT_FILE, font_size)
    except: font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = target_x - (text_w / 2)
    y = target_y - (text_h / 2)
    
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            draw.text((x+dx, y+dy), text, font=font, fill="black")
    draw.text((x, y), text, font=font, fill="white")
    
    filename = f"temp_{random.randint(1, 99999)}.png"
    img.save(filename)
    return filename

# --- MAIN EXECUTION ---
def main():
    equation, opt_left, opt_right, correct_loc = generate_problem()
    caption = get_metadata_text(equation, correct_loc)
    print(f"Generated: {equation}")

    # Load Background
    bg_clip = VideoFileClip(BACKGROUND_FILE)
    w, h = bg_clip.size
    
    # Visuals
    eq_x, eq_y = (w * 0.5), (h * 0.15)
    blue_x, blue_y = (w * 0.25), (h * 0.60)
    red_x, red_y = (w * 0.75), (h * 0.60)

    eq_img = create_placed_text(equation, w, h, eq_x, eq_y, 110)
    blue_img = create_placed_text(opt_left, w, h, blue_x, blue_y, 130)
    red_img = create_placed_text(opt_right, w, h, red_x, red_y, 130)

    eq_clip = ImageClip(eq_img).set_duration(bg_clip.duration)
    blue_clip = ImageClip(blue_img).set_duration(bg_clip.duration)
    red_clip = ImageClip(red_img).set_duration(bg_clip.duration)

    final = CompositeVideoClip([bg_clip, eq_clip, blue_clip, red_clip])
    final.audio = bg_clip.audio

    final.write_videofile(OUTPUT_FILE, fps=24, codec='libx264', audio_codec='aac')

    # Cleanup Images
    for f in [eq_img, blue_img, red_img]:
        if os.path.exists(f): os.remove(f)

    # SEND TO TELEGRAM
    send_to_telegram(OUTPUT_FILE, caption)

if __name__ == "__main__":
    main()
