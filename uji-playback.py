# -*- coding: utf-8 -*-
"""uji-playback.py — putar file MP3 ke speaker utk menguji loopback live-captions.
Decode via av (sama dengan decode_audio_lokal voice-claude), play via soundcard.
"""
import sys
import numpy as np


def decode(path):
    import av
    from av.audio.resampler import AudioResampler
    cont = av.open(path)
    res = AudioResampler(format="s16", rate=24000, layout="mono")
    chunks = []
    for fr in cont.decode(streams=0):
        for out in res.resample(fr):
            arr = np.atleast_2d(out.to_ndarray())
            if arr.shape[0] < arr.shape[1]:
                arr = arr.T
            chunks.append(arr.mean(axis=1).astype(np.int16))
    cont.close()
    y = np.concatenate(chunks).astype(np.float32)
    y = y / 32768.0          # int16 WAJIB dinormalisasi /32768 (gotcha voice-claude)
    return y, 24000


def main():
    src = sys.argv[1]
    audio, rate = decode(src)
    print(f"{src}: {len(audio)/rate:.2f}s @ {rate}Hz, puncak {abs(audio).max():.3f}")
    import soundcard as sc
    spk = sc.default_speaker()
    print("play ke:", spk.name)
    with spk.player(samplerate=rate) as p:
        p.play(np.asarray(audio, dtype=np.float32).reshape(-1, 1))


if __name__ == "__main__":
    main()