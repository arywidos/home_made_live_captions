# -*- coding: utf-8 -*-
"""uji-kecepatan.py — benchmark medium vs large-v3-turbo di kondisi GPU sekarang."""
import gc
import importlib.util
import time

def muat_modul(nama, jalur):
    spec = importlib.util.spec_from_file_location(nama, jalur)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

ujipb = muat_modul("ujipb", r"C:\DATAS\live-captions\uji-playback.py")
decode = ujipb.decode                    # decode wav sama seperti alat uji
lc = muat_modul("lc", r"C:\DATAS\live-captions\live-captions.py")

audio, _ = decode("uji-tts.wav")
print(f"klip uji: {len(audio)/24000:.1f} detik", flush=True)

for ukuran in ("medium", "large-v3-turbo"):
    t0 = time.time()
    try:
        tx = lc.bikin_transcriber(ukuran, "id")
    except Exception as e:
        print(f"{ukuran}: GAGAL MUAT ({str(e)[:160]})", flush=True)
        continue
    t_muat = time.time() - t0
    tx(audio)                            # pemanasan (cudnn dll.)
    t0 = time.time()
    teks = tx(audio)
    t_trans = time.time() - t0
    print(f"{ukuran}: muat {t_muat:.1f}s | transkrip 8.3s audio jadi {t_trans:.2f}s "
          f"| teks: {teks[:50]!r}", flush=True)
    del tx
    gc.collect()