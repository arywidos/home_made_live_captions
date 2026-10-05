# -*- coding: utf-8 -*-
"""live-captions.py — caption live untuk audio sistem (Windows + macOS).

Menangkap audio yang KELUAR di komputer (semua aplikasi: call WhatsApp, Zoom,
Google Meet, YouTube, media player, apa pun), lalu transkrip dengan
faster-whisper lokal.

Cara mengambil audio berbeda per OS:
- Windows : LOOPBACK speaker (bawaan WASAPI) — tanpa perlu software tambahan.
- macOS   : tidak ada loopback bawaan → audio harus diarahkan ke driver
            gratis "BlackHole" (device audio virtual). Setup ada di README
            bagian macOS (Multi-Output Device + izin microphone).

Pola VAD/transcriber dipinjam dari voice-claude (Silero VAD + Whisper).

Pakai (Windows, venv voice-claude):
  C:\\DATAS\\voice-claude\\.venv\\Scripts\\python.exe -X utf8 live-captions.py
Pakai (macOS):
  python3 live-captions.py            # butuh BlackHole terpasang (README)
"""

import argparse
import os
import sys
import time
import threading
from datetime import datetime

import numpy as np

HR = 16000          # sample rate whisper
CHUNK = 1600        # 0.1 s per potongan loopback
TAIL_NDAGU = 800    # hening ekor 0.5 s dianggap kalimat selesai
PANJANG_MAKS = int(HR * 20)   # potong paksa segmen bicara > 20 s
PANJANG_MIN = int(HR * 0.4)   # bicara < 0.4 s diabaikan

# ---------------------------------------------------------------- warna ----
try:
    import colorama
    colorama.just_fix_windows_console()
    HIJAU, KUNING, KELUAR = "\033[92m", "\033[93m", "\033[0m"
    # konsol Windows lama tetap aman
    pass
except Exception:
    HIJAU = KUNING = KELUAR = ""
    colorama = None

# ------------------------------------------------------------- whisper -----
WHISPER_SIZE_DEFAULT = "medium"


def _daftarkan_dll_cuda():
    """Sama dengan voice-claude: CTranslate2 memuat cublas/cudnn via LoadLibraryW
    polos yang hanya menghormati PATH — inject PATH sebelum import ctranslate2."""
    try:
        import nvidia
        base = list(nvidia.__path__)[0]   # namespace package: __file__ None
        dirs = [os.path.join(base, sub, "bin")
                for sub in ("cublas", "cudnn", "cuda_nvrtc")]
        dirs = [d for d in dirs if os.path.isdir(d)]
        os.environ["PATH"] = ";".join(dirs) + ";" + os.environ["PATH"]
    except Exception:
        pass
    os.environ.setdefault("MKL_NUM_THREADS", "4")
    os.environ.setdefault("OMP_NUM_THREADS", "4")


def bikin_transcriber(ukuran, bahasa):
    _daftarkan_dll_cuda()
    from faster_whisper import WhisperModel

    model = None
    dev_aktif = None
    # macOS: tanpa CUDA → langsung CPU int8 (ctranslate2 arm64)
    rencana = (("cpu", "int8"),) if sys.platform == "darwin" \
        else (("cuda", "float16"), ("cpu", "int8"))
    for dev, dt in rencana:
        try:
            model = WhisperModel(ukuran, device=dev, compute_type=dt)
            dev_aktif = f"{dev.upper()} {dt}"
            break
        except Exception as e:
            if dev == rencana[-1][0]:
                raise
            print(f"  (CUDA gagal: {str(e)[:120]} — fallback CPU)", flush=True)

    print(f"  Whisper '{ukuran}' jalan di {dev_aktif} | bahasa '{bahasa}'", flush=True)

    def transcribe(audio):
        # loopback dari soundcard sudah float -1..1; pastikan 1D mono
        # (2D memicu error mkl_malloc yang menyesatkan — pelajaran voice-claude)
        audio = np.asarray(audio, dtype=np.float32).reshape(-1)
        segs, info = model.transcribe(audio, beam_size=1, language=bahasa)
        return " ".join(s.text for s in segs).strip()

    return transcribe


# --------------------------------------------------------------- loopback --
SR_DEV = HR   # sample rate device yang benar-benar terbuka (bisa != 16k di Mac)


def cari_loopback(nama=None):
    """macOS : cari mic 'BlackHole' (device audio virtual tempat audio sistem
                diarahkan — lihat README bagian macOS). `--device` untuk nama
                lain kalau sengaja pakai setup berbeda.
    Windows : loopback mic dari speaker (bawaan WASAPI, tanpa software);              `--device` untuk substring nama speaker (mis. headset Bluetooth)."""
    import soundcard as sc

    if sys.platform == "darwin":
        kandidat = sc.all_microphones()
        pilih = None
        if nama:
            for m in kandidat:
                if nama.lower() in m.name.lower():
                    pilih = m
                    break
            if pilih is None:
                sys.exit(f"  mic dengan nama '{nama}' tidak ditemukan. "
                         f"Yang ada: {[m.name for m in kandidat[:12]]}")
        else:
            for m in kandidat:
                if "blackhole" in m.name.lower():
                    pilih = m
                    break
        if pilih is None:
            sys.exit(
                "  macOS: device 'BlackHole' tidak ketemu.\n"
                "  1) Pasang BlackHole 2ch — https://existential.audio/blackhole/\n"
                "     (atau di Terminal: brew install blackhole-2ch)\n"
                "  2) Buat Multi-Output Device — lihat README bagian macOS,\n"
                "     supaya suaranya tetap ke speaker sambil masuk BlackHole\n"
                "  3) Izinkan akses microphone: System Settings → Privacy &\n"
                "     Security → Microphone → centang Terminal/iTerm\n"
                f"  Mic yang ada sekarang: {[m.name for m in kandidat[:12]]}"
            )
        print(f"  input: {pilih.name} (via BlackHole)", flush=True)
        return pilih

    # ------------------------- Windows -------------------------
    jika_semua = [s for s in sc.all_speakers()]
    pilih = None
    if nama:
        for s in jika_semua:
            if nama.lower() in s.name.lower():
                pilih = s
                break
        if pilih is None:
            sys.exit(f"  speaker dengan nama '{nama}' tidak ditemukan. "
                     f"Tersedia: {[s.name for s in jika_semua]}")
    else:
        pilih = sc.default_speaker()
    lb = sc.get_microphone(pilih.id, include_loopback=True)
    print(f"  loopback: {pilih.name}", flush=True)
    return lb


def thread_rekam(lb, antre):
    """Ambil audio terus-menerus (16k mono), taruh tiap potongan di antrean.
    Di Mac, CoreAudio kadang menolak 16 kHz → fallback 48k/44.1k lalu
    di-resample ke 16k (np.interp, cukup untuk speech ASR)."""
    global BERJALAN, SR_DEV
    try:
        try:
            rec = lb.recorder(samplerate=HR)
            SR_DEV = HR
        except Exception:
            for coba in (48000, 44100):
                try:
                    rec = lb.recorder(samplerate=coba)
                    SR_DEV = coba
                    break
                except Exception:
                    continue
            else:
                raise RuntimeError("device tak mau buka di 16k/48k/44.1k")
        if SR_DEV != HR:
            print(f"  (device {SR_DEV} Hz → di-resample ke {HR} Hz)", flush=True)
        with rec:
            while BERJALAN:
                data = rec.record(numframes=CHUNK if SR_DEV == HR else SR_DEV // 10)
                if data.ndim == 2 and data.shape[1] > 1:
                    data = data.mean(axis=1)   # soundcard float -1..1 → mono
                data = np.asarray(data, dtype=np.float32).reshape(-1)
                if SR_DEV != HR:
                    n_baru = int(round(len(data) * HR / SR_DEV))
                    x_lama = np.arange(len(data)) / SR_DEV
                    x_baru = np.arange(n_baru) / HR
                    data = np.interp(x_baru, x_lama, data).astype(np.float32)
                antre.put(data)
    except Exception as e:
        print(f"\n{KUNING}  [ERROR rekam] {e} — capture berhenti.{KELUAR}", flush=True)
        BERJALAN = False


# ------------------------------------------------------------------ VAD ----
VAD_OPSI = None  # diisi di main (import lambat biar pesan error jelas)


def main():
    parse = argparse.ArgumentParser(description="Caption live dari audio sistem (loopback) + Whisper")
    parse.add_argument("--device", default=None, help="nama device (substring): Windows=speaker (mis. 'soundcore'), macOS=mic BlackHole/mic lain")
    parse.add_argument("--lang", default="id", help="kode bahasa Whisper (default id)")
    parse.add_argument("--model", default=WHISPER_SIZE_DEFAULT, help="ukuran Whisper (medium/small/large-v3)")
    parse.add_argument("--partial", action="store_true", help="tampilkan teks parsial saat orang bicara")
    parse.add_argument("--durasi", type=float, default=0, help="detik sampai berhenti sendiri (0 = terus)")
    args = parse.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    global VAD_OPSI, BERJALAN
    try:
        from faster_whisper.vad import VadOptions
        # chunk kalimat: hening 0.6 s memisahkan; pad 60 ms biar huruf awal utuh
        VAD_OPSI = VadOptions(threshold=0.55, min_speech_duration_ms=180,
                              min_silence_duration_ms=600, speech_pad_ms=60)
    except Exception as e:
        sys.exit(f"  faster-whisper tidak ditemukan: {e}")

    print(__doc__ or "")
    lb = cari_loopback(args.device)
    transcribe = bikin_transcriber(args.model, args.lang)

    nama_log = datetime.now().strftime("live-captions_%Y%m%d_%H%M%S.txt")
    print(f"  log: {nama_log} | Ctrl+C untuk keluar\n", flush=True)

    import queue
    antre = queue.Queue()
    BERJALAN = True
    th = threading.Thread(target=thread_rekam, args=(lb, antre), daemon=True)
    th.start()

    audio = np.zeros(0, dtype=np.float32)   # buffer utuh
    baru = 0                                 # sampel baru sejak VAD terakhir
    tick_parsial = 0.0
    f_log = open(nama_log, "a", encoding="utf-8")

    def segmen_baru(ts):
        """Daftar speech timestamps dari pustaka, terjemah ke interval (a, b)."""
        return [(int(s["start"]), int(s["end"])) for s in ts]

    t_mulai = time.time()
    try:
        from faster_whisper.vad import get_speech_timestamps
        while BERJALAN:
            if args.durasi and time.time() - t_mulai > args.durasi:
                break
            time.sleep(0.15)
            # masukkan tiap potongan dari antrean ke buffer
            potongan = []
            while not antre.empty():
                potongan.append(antre.get())
            if potongan:
                audio = np.concatenate([audio] + potongan) if len(audio) else np.concatenate(potongan)
                baru += sum(len(p) for p in potongan)

            if baru < CHUNK:
                continue
            baru = 0

            ts = get_speech_timestamps(audio, VAD_OPSI, sampling_rate=HR)
            segs = segmen_baru(ts)
            if not segs:
                # tak ada bicara sama sekali → buang buffer (hening) biar hemat
                if len(audio) > HR * 3:
                    audio = audio[len(audio) - HR * 1:]
                continue

            mulai, akhir = segs[0]   # cek segmen yang sedang berlangsung
            # segmen "selesai" = ekornya hening TAIL_NDAGU sampel, atau sudah mentok panjang maks
            masih_bicara = akhir >= len(audio) - TAIL_NDAGU
            panjang = min(akhir, len(audio)) - mulai

            if masih_bicara:
                if args.partial and panjang > PANJANG_MIN and panjang - tick_parsial > HR // 2:
                    uji = audio[mulai:min(akhir, len(audio))]
                    tick_parsial = panjang
                    teks = transcribe(uji)
                    if teks:
                        sys.stdout.write(f"\r{HIJAU}[...]  {teks}{KELUAR}   ")
                        sys.stdout.flush()
                # segmen terlalu panjang → potong paksa biar caption keluar
                if panjang >= PANJANG_MAKS:
                    masih_bicara = False
                    akhir = mulai + PANJANG_MAKS
            if masih_bicara:
                continue

            if panjang < PANJANG_MIN:
                uji = None
            else:
                uji = audio[mulai:min(akhir, len(audio))]
                teks = transcribe(uji).strip()
                jam = datetime.now().strftime("%H:%M:%S")
                if teks:
                    sys.stdout.write("\r" + " " * 120 + "\r")   # bersihkan baris parsial
                    print(f"[{jam}] {HIJAU}{teks}{KELUAR}", flush=True)
                    f_log.write(f"[{jam}] {teks}\n")
                    f_log.flush()

            # buang semua audio sampai akhir segmen: kalau sisakan "konteks"
            # yang memuat ekor bicara, VAD mendeteksi ulang segmen sama tiap
            # tick → teks kembar (bug dedup yang sudah diperbaiki)
            audio = audio[min(akhir, len(audio)):]
            tick_parsial = 0.0
    except KeyboardInterrupt:
        pass
    finally:
        BERJALAN = False
        try:
            f_log.close()
        except Exception:
            pass
        print(f"\n  selesai. log: {nama_log}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass