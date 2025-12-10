# --- MONKEY PATCH (Fixes Pillow crash) ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# ----------------------------------------------------------

import random
import requests
import os
import time
from gtts import gTTS
from moviepy.editor import *
from moviepy.audio.fx.all import audio_loop

# --- CONFIGURATION ---
THINKING_TIME = 2.5 
FONT = 'Impact'
# Backup prompt (only used if you forget to upload an image)
PROMPT_TEXT = "vertical hyperrealistic mountain nature, dark moody lighting, 8k"

# --- ANIMATION FUNCTIONS ---
def slide_down(t, duration=0.8, start_y=-300, final_y=200):
    if t < duration:
        progress = t / duration
        progress = 1 - (1 - progress) ** 3 
        current_y = start_y + (final_y - start_y) * progress
        return ('center', int(current_y))
    else:
        return ('center', final_y)

def slide_up(t, duration=0.5, start_y=1600, final_y=1400):
    if t < duration:
        progress = t / duration
        progress = 1 - (1 - progress) ** 3
        current_y = start_y + (final_y - start_y) * progress
        return ('center', int(current_y))
    else:
        return ('center', final_y)

# --- 1. ASSET FACTORY ---
def prepare_assets():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # A. BACKGROUND CHECK
    # Check if the user uploaded a file named "background.jpg"
    if os.path.exists("background.jpg") and os.path.getsize("background.jpg") > 5000:
        print("✅ User uploaded background detected. Using it.")
    else:
        print("⚠️ No local background found. Downloading backup from AI...")
        # Fallback: Download AI image if user didn't upload one
        seed = random.randint(1, 99999)
        safe_prompt = PROMPT_TEXT.replace(" ", "%20")
        ai_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1080&height=1920&nologo=true&seed={seed}"
        try:
            r = requests.get(ai_url, headers=headers, timeout=30)
            if r.status_code == 200:
                with open("background.jpg", 'wb') as f:
                    f.write(r.content)
                print("AI Background Downloaded.")
        except Exception as e:
            print(f"Backup download failed: {e}")

    # B. DOWNLOAD TICKING SOUND
    # Only download if it doesn't exist
    if not os.path.exists("ticking.ogg"):
        sfx_url = "https://github.com/rafaelreis-hotmart/Audio-Sample-files/raw/master/sample.ogg"
        try:
            print("Downloading Ticking SFX...")
            r = requests.get(sfx_url, headers=headers, timeout=30)
            with open("ticking.ogg", 'wb') as f:
                f.write(r.content)
        except Exception as e:
            print(f"SFX download failed: {e}")

# --- 2. MATH GENERATOR ---
def generate_viral_problem():
    trap_type = random.choice(['zero_trap', 'div_mult_trap', 'paren_trap'])
    if trap_type == 'zero_trap':
        num = random.randint(5, 12)
        return f"{num} + {num} x 0 + {num}"
    elif trap_type == 'div_mult_trap':
        a, b, c = random.randint(10, 25), random.randint(2, 5), random.randint(2, 4)
        return f"{a} - {b} x {c} + 1"
    elif trap_type == 'paren_trap':
        base = random.randint(2, 5) * 2
        return f"{base} ÷ 2({random.randint(1,2)} + 2)"
    return "5 + 5 x 5 - 5"

# --- 3. VOICE ENGINE ---
def create_voiceover():
    print("Generating TTS...")
    tts_hook = gTTS("Only 1 percent can solve this.", lang='en', tld='com')
    tts_hook.save("audio_hook.mp3")
    
    tts_cta = gTTS("Comment your answer and Subscribe.", lang='en', tld='com')
    tts_cta.save("audio_cta.mp3")

# --- 4. VIDEO ENGINE ---
def create_math_short():
    prepare_assets() 
    problem = generate_viral_problem()
    create_voiceover() 
    
    # --- AUDIO SETUP ---
    clip_hook = AudioFileClip("audio_hook.mp3")
    clip_cta = AudioFileClip("audio_cta.mp3")
    
    clip_tick = AudioClip(lambda t: [0], duration=THINKING_TIME)
    try:
        if os.path.exists("ticking.ogg") and os.path.getsize("ticking.ogg") > 1024:
            print("Loading Ticking Sound...")
            real_tick = AudioFileClip("ticking.ogg")
            real_tick = audio_loop(real_tick, duration=THINKING_TIME)
            clip_tick = real_tick.volumex(0.5)
    except Exception as e:
        print(f"Error loading audio: {e}")

    final_audio = concatenate_audioclips([clip_hook, clip_tick, clip_cta])
    
    start_thinking = clip_hook.duration
    start_cta = clip_hook.duration + THINKING_TIME
    total_duration = final_audio.duration

    # --- VISUAL SETUP ---
    w, h = 1080, 1920
    
    # Background Logic
    if os.path.exists("background.jpg") and os.path.getsize("background.jpg") > 5000:
        bg_img = ImageClip("background.jpg")
        # Resize to fill height, then Center Crop width
        bg = bg_img.resize(height=h)
        bg = bg.crop(x1=bg.w/2 - w/2, y1=0, width=w, height=h)
    else:
        print("Using Emergency Color (Should not happen if you uploaded image).")
        bg = ColorClip(size=(w, h), color=(10, 60, 20))
    
    bg = bg.set_duration(total_duration)
    
    # Dark Layer (0.3 opacity) - Makes text readable
    dark_layer = ColorClip(size=(w, h), color=(0, 10, 30)).set_opacity(0.3).set_duration(total_duration)

    # --- TEXT ANIMATIONS ---
    
    # HOOK
    hook_txt = TextClip("ONLY 1% PASS", fontsize=90, color='yellow', font=FONT, stroke_color='black', stroke_width=3)
    hook_txt = hook_txt.set_position(lambda t: slide_down(t))
    hook_txt = hook_txt.set_duration(total_duration)

    # QUESTION
    question_txt = TextClip(f"{problem} = ?", fontsize=110, color='white', font=FONT, stroke_color='black', stroke_width=4)
    question_txt = question_txt.set_position('center')
    question_txt = question_txt.set_start(start_thinking).set_duration(THINKING_TIME + clip_cta.duration).crossfadein(0.3)

    # CTA
    comment_txt = TextClip("👇 COMMENT ANSWER 👇", fontsize=60, color='cyan', font=FONT, stroke_color='black', stroke_width=2)
    comment_txt = comment_txt.set_position(lambda t: slide_up(t))
    comment_txt = comment_txt.set_start(start_cta).set_duration(clip_cta.duration)

    # --- RENDER ---
    final = CompositeVideoClip([bg, dark_layer, hook_txt, question_txt, comment_txt], size=(w, h))
    final = final.set_audio(final_audio)
    
    print("Rendering Video...")
    final.write_videofile("math_final.mp4", fps=24, preset='ultrafast', codec='libx264')
    
    with open("metadata.txt", "w") as f:
        f.write(f"Only 1% Can Solve This! {problem} #shorts")

if __name__ == "__main__":
    create_math_short()
