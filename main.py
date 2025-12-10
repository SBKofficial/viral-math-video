import random
import requests
import os
from gtts import gTTS # standard google tts
from moviepy.editor import *
from moviepy.audio.fx.all import audio_loop

# --- CONFIGURATION ---
BACKGROUND_COLOR = (20, 20, 20) 
TEXT_COLOR = 'white'
FONT = 'Impact'
THINKING_TIME = 4 

# --- 1. ASSET DOWNLOADER ---
def download_assets():
    # Google's Open Sound Library
    sfx_url = "https://actions.google.com/sounds/v1/alarms/mechanical_clock_ticking.ogg"
    if not os.path.exists("ticking.ogg"):
        try:
            print("Downloading Ticking Sound...")
            r = requests.get(sfx_url)
            with open("ticking.ogg", 'wb') as f:
                f.write(r.content)
            print("Download Complete.")
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

# --- 3. GOOGLE VOICE GENERATOR (Fixed) ---
def create_voiceover():
    print("Generating Audio...")
    
    # Hook
    # tld='com' uses the standard US accent. 
    # tld='co.uk' would be British, 'co.in' for Indian accent if preferred.
    tts_hook = gTTS("Only 1 percent can solve this question.", lang='en', tld='com')
    tts_hook.save("audio_hook.mp3")
    
    # CTA
    text = "Comment your answer. Subscribe for more such questions, and like if you think this is tricky."
    tts_cta = gTTS(text, lang='en', tld='com')
    tts_cta.save("audio_cta.mp3")

# --- 4. VIDEO ENGINE ---
def create_math_short():
    print("Starting Video Generation...")
    download_assets() 
    problem = generate_viral_problem()
    
    # No asyncio needed for gTTS
    create_voiceover() 
    
    # --- AUDIO ASSEMBLY ---
    clip_hook = AudioFileClip("audio_hook.mp3")
    clip_cta = AudioFileClip("audio_cta.mp3")
    
    if os.path.exists("ticking.ogg"):
        clip_tick = AudioFileClip("ticking.ogg")
        clip_tick = audio_loop(clip_tick, duration=THINKING_TIME)
        clip_tick = clip_tick.volumex(0.6)
    else:
        clip_tick = AudioClip(lambda t: [0], duration=THINKING_TIME)

    final_audio = concatenate_audioclips([clip_hook, clip_tick, clip_cta])
    
    start_thinking = clip_hook.duration
    start_cta = clip_hook.duration + THINKING_TIME
    total_duration = final_audio.duration

    # --- VISUAL ASSEMBLY ---
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

    final = CompositeVideoClip([bg, hook_txt, question_txt, comment_txt, sub_txt], size=(w, h))
    final = final.set_audio(final_audio)
    
    final.write_videofile("math_final.mp4", fps=24, preset='ultrafast', codec='libx264')
    
    with open("metadata.txt", "w") as f:
        f.write(f"Title: Only 1% Pass! {problem} #shorts\n\nDesc:\nCan you solve this?\n{problem} = ?\n\nComment your answer! 👇")

if __name__ == "__main__":
    create_math_short()
