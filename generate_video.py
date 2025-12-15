import os
import random
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
BACKGROUND_FILE = "background.mp4" # Your Canva video (Visuals + Phonk Audio)
FONT_FILE = "font.ttf"             # Your bold font file
OUTPUT_FILE = "daily_short.mp4"

# --- STEP 1: MATH LOGIC ENGINE (Viral PEMDAS Traps) ---
def generate_problem():
    # 50% Multiplication Trap, 50% Division Trap
    if random.random() > 0.5:
        # Format: A + B x C
        a = random.randint(5, 15); b = random.randint(5, 10); c = random.randint(2, 5)
        equation = f"{a} + {b} x {c} = ?"
        correct = a + (b * c)
        trap = (a + b) * c # Common Left-to-Right Mistake
    else:
        # Format: A ÷ B ( C + D )
        b = random.randint(2, 5)
        sum_cd = random.randint(2, 5)
        a = b * random.randint(2, 6) # Ensure clean division
        
        # Split sum_cd into c and d
        c = random.randint(1, sum_cd - 1); d = sum_cd - c
        
        equation = f"{a} ÷ {b}({c} + {d}) = ?"
        correct = (a // b) * sum_cd
        
        # Smart Trap logic
        if (b * sum_cd) != 0 and a % (b * sum_cd) == 0: 
            trap = a // (b * sum_cd)
        else: 
            trap = correct - random.choice([1, 10, 5])

    # Shuffle Options (A=Left Hand, B=Right Hand)
    if random.random() > 0.5:
        return equation, str(correct), str(trap) # Left is Correct
    else:
        return equation, str(trap), str(correct) # Right is Correct

# --- STEP 2: PRECISION TEXT ENGINE ---
def create_placed_text(text, bg_w, bg_h, target_x, target_y, font_size):
    # Create transparent image
    img = Image.new('RGBA', (bg_w, bg_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try: font = ImageFont.truetype(FONT_FILE, font_size)
    except: font = ImageFont.load_default()

    # Calculate text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Center exact coordinates
    x = target_x - (text_w / 2)
    y = target_y - (text_h / 2)
    
    # Draw Thick Black Outline (For readability)
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            draw.text((x+dx, y+dy), text, font=font, fill="black")
            
    # Draw White Text
    draw.text((x, y), text, font=font, fill="white")
    
    filename = f"temp_{random.randint(1, 99999)}.png"
    img.save(filename)
    return filename

# --- MAIN EXECUTION ---
def main():
    equation, opt_left, opt_right = generate_problem()
    print(f"Generated: {equation} | L:{opt_left} | R:{opt_right}")

    # 1. Load Background & Detect Duration
    if not os.path.exists(BACKGROUND_FILE):
        raise FileNotFoundError(f"Missing {BACKGROUND_FILE}!")
        
    bg_clip = VideoFileClip(BACKGROUND_FILE)
    w, h = bg_clip.size
    duration = bg_clip.duration
    print(f"Video Duration Detected: {duration}s")

    # 2. Coordinates (Optimized for your screenshot)
    # Question: High up, but below YouTube Search bar (15% down)
    eq_x, eq_y = (w * 0.5), (h * 0.15)
    
    # Hands: Lower, resting on the palms (60% down)
    blue_x, blue_y = (w * 0.25), (h * 0.60) # Left
    red_x, red_y = (w * 0.75), (h * 0.60)   # Right

    # 3. Create Visual Layers
    eq_img = create_placed_text(equation, w, h, eq_x, eq_y, 110)
    blue_img = create_placed_text(opt_left, w, h, blue_x, blue_y, 130)
    red_img = create_placed_text(opt_right, w, h, red_x, red_y, 130)

    # 4. Create Clips
    eq_clip = ImageClip(eq_img).set_duration(duration)
    blue_clip = ImageClip(blue_img).set_duration(duration)
    red_clip = ImageClip(red_img).set_duration(duration)

    # 5. Render Final Video
    final = CompositeVideoClip([bg_clip, eq_clip, blue_clip, red_clip])
    final.audio = bg_clip.audio # KEEP THE PHONK MUSIC!

    final.write_videofile(OUTPUT_FILE, fps=24, codec='libx264', audio_codec='aac')

    # Cleanup
    for f in [eq_img, blue_img, red_img]:
        if os.path.exists(f): os.remove(f)
    print("Video Created Successfully!")

if __name__ == "__main__":
    main()
