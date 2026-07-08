"""Synthesize a soft, romantic background loop for the invitation.

Gentle felt-piano-style arpeggios over a warm sustained pad, progression
I-V-vi-IV in D major, slow and dreamy. Written to a WAV so it needs no
external encoder and autoplays/loops in every browser.
"""
import numpy as np
from scipy.io import wavfile

SR = 32000

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)

# Note names -> midi numbers we need
NOTE = {
    "D3": 50, "A3": 57, "B3": 59, "G3": 55,
    "D4": 62, "E4": 64, "Fs4": 66, "G4": 67, "A4": 69, "B4": 71,
    "Cs5": 73, "D5": 74, "E5": 76, "Fs5": 78, "A5": 81,
}

def tone(freq, dur, amp=0.2, attack=0.02, release=None, partials=(1.0, 0.28, 0.12)):
    n = int(dur * SR)
    t = np.arange(n) / SR
    wave = np.zeros(n)
    for k, a in enumerate(partials, start=1):
        wave += a * np.sin(2 * np.pi * freq * k * t)
    wave /= sum(partials)
    # soft attack + long exponential decay (felt-piano/bell-ish)
    env = np.ones(n)
    a = int(attack * SR)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    decay = np.exp(-t * (2.6 if release is None else release))
    env *= decay
    return wave * env * amp

def pad(freqs, dur, amp=0.06):
    """Soft sustained chord pad with gentle swell."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    wave = np.zeros(n)
    for f in freqs:
        wave += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)
    wave /= len(freqs) * 1.3
    swell = 0.5 - 0.5 * np.cos(2 * np.pi * t / dur)  # 0..1..0 over the bar
    env = 0.4 + 0.6 * swell
    return wave * env * amp

# --- Arrange -----------------------------------------------------------
BAR = 3.0  # seconds per chord
# progression pass 1 (gentle, mid register)
pass1 = [
    ("D", ["D3", "A3", "Fs4"], ["Fs4", "A4", "D5", "A4", "Fs4", "E4"]),
    ("A", ["A3", "E4", "Cs5"], ["E4", "A4", "Cs5", "A4", "E4", "Fs4"]),
    ("Bm", ["B3", "Fs4", "D5"], ["Fs4", "B4", "D5", "B4", "Fs4", "A4"]),
    ("G", ["G3", "D4", "B4"], ["G4", "B4", "D5", "B4", "G4", "Fs4"]),
]
# progression pass 2 (a touch brighter, higher melody peaks for variation)
pass2 = [
    ("D", ["D3", "A3", "Fs4"], ["A4", "D5", "Fs5", "D5", "A4", "Fs4"]),
    ("A", ["A3", "E4", "Cs5"], ["Cs5", "E5", "A5", "E5", "Cs5", "A4"]),
    ("Bm", ["B3", "Fs4", "D5"], ["D5", "Fs5", "B4", "Fs5", "D5", "B4"]),
    ("G", ["G3", "D4", "B4"], ["B4", "D5", "G4", "D5", "B4", "A4"]),
]
sequence = pass1 + pass2

cycle_len = int(BAR * len(sequence) * SR)
buf = np.zeros(cycle_len + SR)  # a little tail room

pos = 0
for _, padnotes, arp in sequence:
    # pad under the whole bar
    p = pad([midi(NOTE[x]) for x in padnotes], BAR, amp=0.075)
    buf[pos:pos + len(p)] += p
    # arpeggio: notes spread across the bar
    step = BAR / len(arp)
    for j, name in enumerate(arp):
        start = pos + int(j * step * SR)
        note = tone(midi(NOTE[name]), step * 1.9, amp=0.17, attack=0.012, release=2.2)
        end = min(start + len(note), len(buf))
        buf[start:end] += note[:end - start]
        # sparkle harmony a 12th up, very soft, on the downbeats
        if j % 3 == 0:
            hi = tone(midi(NOTE[name]) * 2, step * 1.4, amp=0.045, attack=0.01, release=3.0)
            e2 = min(start + len(hi), len(buf))
            buf[start:e2] += hi[:e2 - start]
    pos += int(BAR * SR)

# --- Simple reverb (a few soft taps) -----------------------------------
rev = np.zeros_like(buf)
for delay_ms, gain in [(70, 0.25), (130, 0.18), (210, 0.12), (330, 0.07)]:
    d = int(delay_ms / 1000 * SR)
    rev[d:] += buf[:-d] * gain
buf = buf + rev

# fold the tail back to the start so the loop seam is smooth
tail = buf[cycle_len:]
buf = buf[:cycle_len].copy()
buf[:len(tail)] += tail

# gentle fade at both ends of the loop to avoid clicks
fade = int(0.12 * SR)
buf[:fade] *= np.linspace(0.4, 1, fade)
buf[-fade:] *= np.linspace(1, 0.4, fade)

# normalise softly (keep it quiet / background level)
peak = np.max(np.abs(buf)) or 1.0
buf = buf / peak * 0.5

audio = np.int16(buf * 32767)
wavfile.write("music.wav", SR, audio)
print("wrote music.wav", round(len(buf) / SR, 2), "s", audio.nbytes // 1024, "KB")
