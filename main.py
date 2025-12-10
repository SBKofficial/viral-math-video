# --- MONKEY PATCH (Fixes Pillow crash) ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
# ----------------------------------------------------------

import random
import requests
import os
import urllib.parse
from gtts import gTTS
from moviepy.editor import *
from moviepy.audio.fx.all import audio_loop

# --- CONFIGURATION ---
THINKING_TIME = 2.5 
FONT = 'Impact'

# --- ANIMATION FUNCTIONS ---
def slide_down(t, duration=0.8, start_y=-200, final_y=180): # Moved down slightly to y=180
    if t < duration:
        progress = 1 - (1 - t/duration) ** 3 
        current_y = start_y + (final_y - start_y) * progress
        return ('center', int(current_y))
    else:
        return ('center', final_y)

def slide_up(t, duration=0.5, start_y=1800, final_y=1550):
    if t < duration:
        progress = 1 - (1 - t/duration) ** 3
        current_y = start_y + (final_y - start_y) * progress
        return ('center', int(current_y))
    else:
        return ('center', final_y)

# --- 1. ASSET FACTORY ---
def prepare_assets():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 1. Background Check
    if os.path.exists("background.jpg") and os.path.getsize("background.jpg") > 5000:
        print("✅ Local background.jpg detected.")
    else:
        print("⚠️ Downloading Backup Background...")
        try:
            # Using a reliable static nature image (Unsplash Source)
            url = "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?q=80&w=1080&auto=format&fit=crop"
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                with open("background.jpg", 'wb') as f:
                    f.write(r.content)
        except Exception as e:
            print(f"Background download error: {e}")

    # 2. Sound Check
    if not os.path.exists("ticking.ogg"):
        try:
            r = requests.get("https://github.com/rafaelreis-hotmart/Audio-Sample-files/raw/master/sample.ogg", headers=headers, timeout=30)
            with open("ticking.ogg", 'wb') as f:
                f.write(r.content)
        except:
            pass

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
    tts_hook = gTTS("Only 1 percent can solve this.", lang='en', tld='com')
    tts_hook.save("audio_hook.mp3")
    tts_cta = gTTS("Comment your answer and Subscribe.", lang='en', tld='com')
    tts_cta.save("audio_cta.mp3")

# --- 4. VIDEO ENGINE ---
def create_math_short():
    prepare_assets() 
    problem = generate_viral_problem()
    create_voiceover() 
    
    # --- AUDIO ---
    clip_hook = AudioFileClip("audio_hook.mp3")
    clip_cta = AudioFileClip("audio_cta.mp3")
    
    clip_tick = AudioClip(lambda t: [0], duration=THINKING_TIME)
    try:
        if os.path.exists("ticking.ogg"):
            real_tick = AudioFileClip("ticking.ogg")
            real_tick = audio_loop(real_tick, duration=THINKING_TIME)
            clip_tick = real_tick.volumex(0.5)
    except: pass

    final_audio = concatenate_audioclips([clip_hook, clip_tick, clip_cta])
    start_thinking = clip_hook.duration
    start_cta = clip_hook.duration + THINKING_TIME
    total_duration = final_audio.duration

    # --- VISUALS ---
    w, h = 1080, 1920
    
    # LAYER 1: BACKGROUND (The Fix)
    if os.path.exists("background.jpg") and os.path.getsize("background.jpg") > 5000:
        bg_img = ImageClip("background.jpg")
        # FORCE RESIZE to exact screen dimensions (Solves the black bar issue)
        bg = bg_img.resize(newsize=(w, h))
    else:
        print("DEBUG: Using Fallback Color Background")
        bg = ColorClip(size=(w, h), color=(50, 100, 200)) 
    
    bg = bg.set_position(('center', 'center')).set_duration(total_duration)

    # LAYER 2: TEXT HOOK
    # Increased stroke width to 6 for better readability against nature
    hook_txt = TextClip("ONLY 1% PASS", fontsize=80, color='yellow', font=FONT, stroke_color='black', stroke_width=6)
    hook_txt = hook_txt.set_position(lambda t: slide_down(t))
    hook_txt = hook_txt.set_duration(total_duration)

    # LAYER 3: TEXT QUESTION
    question_txt = TextClip(f"{problem} = ?", fontsize=110, color='white', font=FONT, stroke_color='black', stroke_width=6)
    question_txt = question_txt.set_position('center')
    question_txt = question_txt.set_start(start_thinking).set_duration(THINKING_TIME + clip_cta.duration).crossfadein(0.3)

    # LAYER 4: TEXT CTA
    comment_txt = TextClip("👇 COMMENT ANSWER 👇", fontsize=55, color='cyan', font=FONT, stroke_color='black', stroke_width=5)
    comment_txt = comment_txt.set_position(lambda t: slide_up(t))
    comment_txt = comment_txt.set_start(start_cta).set_duration(clip_cta.duration)

    # --- RENDER ---
    final = CompositeVideoClip([bg, hook_txt, question_txt, comment_txt], size=(w, h))
    final = final.set_audio(final_audio)
    
    print("Rendering Video with YUV420P...")
    final.write_videofile("math_final.mp4", fps=24, preset='ultrafast', codec='libx264', ffmpeg_params=['-pix_fmt', 'yuv420p'])
    
    with open("metadata.txt", "w") as f:
        f.write(f"Only 1% Can Solve This! {problem} #shorts")

if __name__ == "__main__":
    create_math_short()
