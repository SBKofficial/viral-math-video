# --- MONKEY PATCH (Fixes the PIL.Image.ANTIALIAS crash) ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# ----------------------------------------------------------

import random
import requests
import os
from gtts import gTTS
from moviepy.editor import *
from moviepy.audio.fx.all import audio_loop

# --- CONFIGURATION ---
THINKING_TIME = 2.5 
FONT = 'Impact'
POLLINATIONS_PROMPT = "mysterious blackboard with complex mathematical formulas, cinematic lighting, 8k render, dark atmosphere"

# --- 1. ASSET FACTORY ---
def download_assets():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # A. Download AI Background (Timeout increased to 30s)
    seed = random.randint(1, 9999)
    bg_url = f"https://image.pollinations.ai/prompt/{POLLINATIONS_PROMPT} {seed}"
    try:
        print("Downloading Background...")
        r = requests.get(bg_url, headers=headers, timeout=30)
        if r.status_code == 200 and len(r.content) > 1000:
            with open("background.jpg", 'wb') as f:
                f.write(r.content)
            print("Background Downloaded.")
    except Exception as e:
        print(f"Background download failed: {e}")

    # B. Download Ticking Sound
    sfx_url = "https://github.com/rafaelreis-hotmart/Audio-Sample-files/raw/master/sample.ogg"
    
    try:
        print("Downloading Ticking SFX...")
        r = requests.get(sfx_url, headers=headers, timeout=10)
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
    download_assets() 
    problem = generate_viral_problem()
    create_voiceover() 
    
    # --- AUDIO SETUP ---
    clip_hook = AudioFileClip("audio_hook.mp3")
    clip_cta = AudioFileClip("audio_cta.mp3")
    
    # Audio Safety Logic
    clip_tick = AudioClip(lambda t: [0], duration=THINKING_TIME) # Default Silence
    
    try:
        if os.path.exists("ticking.ogg") and os.path.getsize("ticking.ogg") > 1024:
            print("Loading Ticking Sound...")
            real_tick = AudioFileClip("ticking.ogg")
            real_tick = audio_loop(real_tick, duration=THINKING_TIME)
            clip_tick = real_tick.volumex(0.5)
        else:
            print("Ticking file invalid/empty. Using silence.")
    except Exception as e:
        print(f"Error loading audio file: {e}. Using silence.")

    final_audio = concatenate_audioclips([clip_hook, clip_tick, clip_cta])
    
    start_thinking = clip_hook.duration
    start_cta = clip_hook.duration + THINKING_TIME
    total_duration = final_audio.duration

    # --- VISUAL SETUP ---
    w, h = 1080, 1920
    
    # Background Logic
    if os.path.exists("background.jpg") and os.path.getsize("background.jpg") > 1024:
        bg_img = ImageClip("background.jpg")
        bg = bg_img.resize(height=h).crop(x1=0, y1=0, width=w, height=h, x_center=bg_img.w/2, y_center=h/2)
    else:
        bg = ColorClip(size=(w, h), color=(20, 20, 20))
    
    bg = bg.set_duration(total_duration)
    
    # --- THE FIX IS HERE ---
    # We moved .set_opacity() to the end chain
    dark_layer = ColorClip(size=(w, h), color=(0,0,0)).set_opacity(0.6).set_duration(total_duration)

    # Text Elements
    hook_txt = TextClip("ONLY 1% PASS", fontsize=90, color='yellow', font=FONT, stroke_color='black', stroke_width=3)
    hook_txt = hook_txt.set_position(('center', 200)).set_duration(total_duration).crossfadein(0.5)

    question_txt = TextClip(f"{problem} = ?", fontsize=110, color='white', font=FONT, stroke_color='black', stroke_width=4)
    question_txt = question_txt.set_position('center')
    question_txt = question_txt.set_start(start_thinking).set_duration(THINKING_TIME + clip_cta.duration).crossfadein(0.2)

    comment_txt = TextClip("👇 COMMENT ANSWER 👇", fontsize=60, color='cyan', font=FONT, stroke_color='black', stroke_width=2)
    comment_txt = comment_txt.set_position(('center', 1400)).set_start(start_cta).set_duration(clip_cta.duration).crossfadein(0.5)

    # --- RENDER ---
    final = CompositeVideoClip([bg, dark_layer, hook_txt, question_txt, comment_txt], size=(w, h))
    final = final.set_audio(final_audio)
    
    print("Rendering Video...")
    final.write_videofile("math_final.mp4", fps=24, preset='ultrafast', codec='libx264')
    
    with open("metadata.txt", "w") as f:
        f.write(f"Only 1% Can Solve This! {problem} #shorts")

if __name__ == "__main__":
    create_math_short()
