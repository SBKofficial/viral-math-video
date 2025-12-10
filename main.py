import random
import requests
import os
from gtts import gTTS
from moviepy.editor import *
from moviepy.audio.fx.all import audio_loop

# --- CONFIGURATION ---
BACKGROUND_COLOR = (20, 20, 20) 
TEXT_COLOR = 'white'
FONT = 'Impact'
THINKING_TIME = 4 

# --- 1. ASSET DOWNLOADER (Fixed with Headers & Validation) ---
def download_assets():
    # We use a User-Agent to prevent 403 Forbidden errors
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    sfx_url = "https://actions.google.com/sounds/v1/alarms/mechanical_clock_ticking.ogg"
    
    try:
        # Check if file exists and has content
        if not os.path.exists("ticking.ogg") or os.path.getsize("ticking.ogg") == 0:
            print("Downloading Ticking Sound...")
            r = requests.get(sfx_url, headers=headers, timeout=10)
            
            if r.status_code == 200:
                with open("ticking.ogg", 'wb') as f:
                    f.write(r.content)
                print("Download Complete.")
            else:
                print(f"Download failed with status: {r.status_code}")
    except Exception as e:
        print(f"Error downloading SFX: {e}")

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

# --- 3. VOICE GENERATOR ---
def create_voiceover():
    print("Generating Audio...")
    tts_hook = gTTS("Only 1 percent can solve this question.", lang='en', tld='com')
    tts_hook.save("audio_hook.mp3")
    
    text = "Comment your answer. Subscribe for more such questions, and like if you think this is tricky."
    tts_cta = gTTS(text, lang='en', tld='com')
    tts_cta.save("audio_cta.mp3")

# --- 4. VIDEO ENGINE ---
def create_math_short():
    print("Starting Video Generation...")
    
    # 1. Prepare Assets
    download_assets() 
    problem = generate_viral_problem()
    create_voiceover() 
    
    # 2. Load Audio Clips
    clip_hook = AudioFileClip("audio_hook.mp3")
    clip_cta = AudioFileClip("audio_cta.mp3")
    
    # 3. Robust Ticking Sound Loader
    # If the file is broken/empty, we fallback to silence instead of crashing
    try:
        if os.path.exists("ticking.ogg") and os.path.getsize("ticking.ogg") > 100:
            clip_tick = AudioFileClip("ticking.ogg")
            clip_tick = audio_loop(clip_tick, duration=THINKING_TIME)
            clip_tick = clip_tick.volumex(0.6)
            print("Ticking sound loaded successfully.")
        else:
            raise Exception("File invalid or empty")
    except Exception as e:
        print(f"Skipping ticking sound due to error: {e}")
        # Create silent audio for the duration of thinking time
        clip_tick = AudioClip(lambda t: [0], duration=THINKING_TIME)

    # 4. Assemble Audio
    final_audio = concatenate_audioclips([clip_hook, clip_tick, clip_cta])
    
    # Timings
    start_thinking = clip_hook.duration
    start_cta = clip_hook.duration + THINKING_TIME
    total_duration = final_audio.duration

    # 5. Visuals
    w, h = 1080, 1920
    bg = ColorClip(size=(w, h), color=BACKGROUND_COLOR).set_duration(total_duration)
    
    hook_txt = TextClip("ONLY 1% PASS", fontsize=90, color='yellow', font=FONT, stroke_color='black', stroke_width=3)
    hook_txt = hook_txt.set_position(('center', 150)).set_duration(total_duration)
    
    question_txt = TextClip(f"{problem} = ?", fontsize=110, color=TEXT_COLOR, font=FONT)
    question_txt = question_txt.set_position('center')
    question_txt = question_txt.set_start(start_thinking).set_duration(THINKING_TIME + clip_cta.duration)
    
    comment_txt = TextClip("👇 COMMENT ANSWER 👇", fontsize=60, color='cyan', font=FONT)
    comment_txt = comment_txt.set_position(('center', 1300)).set_start(start_cta).set_duration(clip_cta.duration)
    
    sub_txt = TextClip("SUBSCRIBE & LIKE 👍", fontsize=70, color='red', font=FONT, stroke_color='white', stroke_width=2)
    sub_txt = sub_txt.set_position(('center', 1500)).set_start(start_cta + 1.5).set_duration(clip_cta.duration - 1.5)

    # 6. Render
    final = CompositeVideoClip([bg, hook_txt, question_txt, comment_txt, sub_txt], size=(w, h))
    final = final.set_audio(final_audio)
    
    final.write_videofile("math_final.mp4", fps=24, preset='ultrafast', codec='libx264')
    
    with open("metadata.txt", "w") as f:
        f.write(f"Title: Only 1% Pass! {problem} #shorts\n\nDesc:\nCan you solve this?\n{problem} = ?\n\nComment your answer! 👇")

if __name__ == "__main__":
    create_math_short()
