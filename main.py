import random
import asyncio
import requests
import os
import edge_tts
from moviepy.editor import *
from moviepy.audio.fx.all import audio_loop

# --- CONFIGURATION ---
BACKGROUND_COLOR = (20, 20, 20) # Dark Charcoal
TEXT_COLOR = 'white'
FONT = 'Impact' # Standard thick font
THINKING_TIME = 4 # Seconds allowed for them to think

# --- 1. ASSET DOWNLOADER ---
def download_assets():
    # Google's Open Sound Library - Mechanical Clock
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

# --- 2. MATH TRAP GENERATOR ---
def generate_viral_problem():
    trap_type = random.choice(['zero_trap', 'div_mult_trap', 'paren_trap'])
    
    if trap_type == 'zero_trap':
        # 10 + 10 x 0 + 10
        num = random.randint(5, 12)
        return f"{num} + {num} x 0 + {num}"
        
    elif trap_type == 'div_mult_trap':
        # 20 - 5 x 2 + 1
        a, b, c = random.randint(10, 25), random.randint(2, 5), random.randint(2, 4)
        return f"{a} - {b} x {c} + 1"
        
    elif trap_type == 'paren_trap':
        # 8 / 2(2 + 2)
        base = random.randint(2, 5) * 2
        return f"{base} ÷ 2({random.randint(1,2)} + 2)"
        
    return "5 + 5 x 5 - 5" # Fallback

# --- 3. VOICE GENERATOR ---
async def create_voiceover():
    # Hook
    t1 = edge_tts.Communicate("Only 1 percent can solve this question.", "en-US-EricNeural")
    await t1.save("audio_hook.mp3")
    
    # CTA (Outro)
    text = "Comment your answer. Subscribe for more such questions, and like if you think this is tricky."
    t2 = edge_tts.Communicate(text, "en-US-EricNeural")
    await t2.save("audio_cta.mp3")

# --- 4. VIDEO ENGINE ---
def create_math_short():
    print("Starting Video Generation...")
    download_assets() 
    problem = generate_viral_problem()
    asyncio.run(create_voiceover())
    
    # --- AUDIO ASSEMBLY ---
    clip_hook = AudioFileClip("audio_hook.mp3")
    clip_cta = AudioFileClip("audio_cta.mp3")
    
    # Handle Ticking Sound
    if os.path.exists("ticking.ogg"):
        clip_tick = AudioFileClip("ticking.ogg")
        # Loop ticking to fit thinking time exactly
        clip_tick = audio_loop(clip_tick, duration=THINKING_TIME)
        clip_tick = clip_tick.volumex(0.6) # Lower volume to 60%
    else:
        clip_tick = AudioClip(lambda t: [0], duration=THINKING_TIME)

    # Sequence: Hook -> Ticking -> CTA
    final_audio = concatenate_audioclips([clip_hook, clip_tick, clip_cta])
    
    # Timings
    start_thinking = clip_hook.duration
    start_cta = clip_hook.duration + THINKING_TIME
    total_duration = final_audio.duration

    # --- VISUAL ASSEMBLY ---
    w, h = 1080, 1920
    
    # Background
    bg = ColorClip(size=(w, h), color=BACKGROUND_COLOR).set_duration(total_duration)
    
    # 1. Hook Text (Top)
    hook_txt = TextClip("ONLY 1% PASS", fontsize=90, color='yellow', font=FONT, stroke_color='black', stroke_width=3)
    hook_txt = hook_txt.set_position(('center', 150)).set_duration(total_duration)
    
    # 2. The Question (Appears when Ticking starts)
    question_txt = TextClip(f"{problem} = ?", fontsize=110, color=TEXT_COLOR, font=FONT)
    question_txt = question_txt.set_position('center')
    # It stays visible during thinking AND the CTA
    question_txt = question_txt.set_start(start_thinking).set_duration(THINKING_TIME + clip_cta.duration)
    
    # 3. Comment Arrow (Appears at CTA start)
    comment_txt = TextClip("👇 COMMENT ANSWER 👇", fontsize=60, color='cyan', font=FONT)
    comment_txt = comment_txt.set_position(('center', 1300)).set_start(start_cta).set_duration(clip_cta.duration)
    
    # 4. Subscribe/Like Text (Delays slightly for effect)
    sub_txt = TextClip("SUBSCRIBE & LIKE 👍", fontsize=70, color='red', font=FONT, stroke_color='white', stroke_width=2)
    sub_txt = sub_txt.set_position(('center', 1500)).set_start(start_cta + 1.5).set_duration(clip_cta.duration - 1.5)

    # --- RENDER ---
    final = CompositeVideoClip([bg, hook_txt, question_txt, comment_txt, sub_txt], size=(w, h))
    final = final.set_audio(final_audio)
    
    # Write file
    final.write_videofile("math_final.mp4", fps=24, preset='ultrafast', codec='libx264')
    
    # Generate Metadata text file
    with open("metadata.txt", "w") as f:
        f.write(f"Title: Only 1% Pass! {problem} #shorts\n\nDesc:\nCan you solve this?\n{problem} = ?\n\nComment your answer! 👇")

if __name__ == "__main__":
    create_math_short()
