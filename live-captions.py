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
import warnings
from datetime import datetime

import numpy as np

# warning "data discontinuity" dari soundcard/Windows MediaFoundation itu
# benign (transkrip tetap benar — terverifikasi saat uji); senyapkan biar
# layar bersih untuk pengguna awam
warnings.filterwarnings("ignore", message="data discontinuity")

HR = 16000          # sample rate whisper
CHUNK = 1600        # 0.1 s per potongan loopback
TAIL_NDAGU = 800    # hening ekor 0.5 s dianggap kalimat selesai
PANJANG_MAKS = int(HR * 20)   # potong paksa segmen bicara > 20 s
PANJANG_MIN = int(HR * 0.4)   # bicara < 0.4 s diabaikan

# ---------------------------------------------------------------- warna ----
try:
    import colorama
    colorama.just_fix_windows_console()
    HIJAU, KUNING, CYAN, KELUAR = "\033[92m", "\033[93m", "\033[96m", "\033[0m"
    # konsol Windows lama tetap aman
    pass
except Exception:
    HIJAU = KUNING = CYAN = KELUAR = ""
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
    kw = {} if bahasa == "auto" else {"language": bahasa}

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
        segs, info = model.transcribe(audio, beam_size=1, **kw)
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


def cari_mic(nama=None):
    """Mic sungguhan (bukan loopback) untuk opsi --mic: merekam suara pemakai
    sendiri saat bicara di meeting, diberi label (saya)."""
    import soundcard as sc
    kandidat = sc.all_microphones(include_loopback=False)
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
        pilih = sc.default_microphone()
    print(f"  mic: {pilih.name} (label: saya)", flush=True)
    return pilih


def thread_rekam(device, antre, sumber):
    """Ambil audio terus-menerus (16k mono), taruh tiap potongan di antrean
    berlabel sumber ('lawan' utk loopback / 'saya' utk mic).
    Di Mac, CoreAudio kadang menolak 16 kHz → fallback 48k/44.1k lalu
    di-resample ke 16k (np.interp, cukup untuk speech ASR)."""
    global BERJALAN, SR_DEV
    # Python 3.14: filter warnings top-level TIDAK didengar thread rekaman
    # (filter jalan di thread utama, lolos di thread) → pasang ulang di sini
    warnings.filterwarnings("ignore", message="data discontinuity")
    try:
        try:
            rec = device.recorder(samplerate=HR)
            SR_DEV = HR
        except Exception:
            for coba in (48000, 44100):
                try:
                    rec = device.recorder(samplerate=coba)
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
                antre.put((sumber, data))
    except Exception as e:
        import traceback
        print(f"\n{KUNING}  [ERROR rekam ({sumber})] {e}{KELUAR}", flush=True)
        traceback.print_exc()
        BERJALAN = False


# ------------------------------------------------------------------ VAD ----
VAD_OPSI = None  # diisi di main (import lambat biar pesan error jelas)


# ---------------------------------------------------------------- config ---
def baca_config():
    """Baca file config.txt di folder program (yang diedit user dengan Notepad).
    Isi baris format:  kunci = nilai   (baris # awal dianggap komentar).
    Kunci yang dikenal: folder_log, lang, model."""
    jalur = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.txt")
    setelan = {}
    try:
        if os.path.isfile(jalur):
            with open(jalur, encoding="utf-8") as f:
                for baris in f:
                    baris = baris.split("#", 1)[0].strip()   # buang komentar
                    if not baris or "=" not in baris:
                        continue
                    kunci, nilai = baris.split("=", 1)
                    setelan[kunci.strip().lower()] = nilai.strip()
    except Exception as e:
        print(f"  (config.txt tidak terbaca: {e} — dipakai default)", flush=True)
    return setelan


def main():
    cfg = baca_config()

    parse = argparse.ArgumentParser(description="Caption live dari audio sistem (loopback) + Whisper")
    parse.add_argument("--device", default=None, help="nama device (substring): Windows=speaker (mis. 'soundcore'), macOS=mic BlackHole/mic lain")
    parse.add_argument("--lang", default=None,
                       help="kode bahasa Whisper (default id; 'en' utk Inggris; "
                            "'auto' = tebak tiap kalimat, sering salah utk klip pendek)")
    parse.add_argument("--model", default=None, help="ukuran Whisper (medium/small/large-v3)")
    parse.add_argument("--folder-log", default=None,
                       help="folder penyimpanan file log; default: dari config.txt (folder_log=) "
                            "atau folder program ini")
    parse.add_argument("--partial", action="store_true", help="tampilkan teks parsial saat orang bicara")
    parse.add_argument("--durasi", type=float, default=0, help="detik sampai berhenti sendiri (0 = terus)")
    parse.add_argument("--mic", action="store_true",
                       help="juga rekam mic → suara pemakai tercaption berlabel (saya). "
                            "Pakai headset supaya suara lawan dari speaker tidak terdeteksi dobel!")
    parse.add_argument("--mic-device", default=None, help="nama mic (substring) kalau bukan mic default")
    args = parse.parse_args()

    # urutan: flag CLI > config.txt > default
    folder_log = args.folder_log or cfg.get("folder_log") or ""
    lang = args.lang or cfg.get("lang") or "auto"   # default: biarkan Whisper menebak
    model_ukuran = args.model or cfg.get("model") or WHISPER_SIZE_DEFAULT
    if folder_log:
        os.makedirs(folder_log, exist_ok=True)
    dari_config = {k: v for k, v in (("folder_log", folder_log), ("lang", lang), ("model", model_ukuran))
                   if k in cfg or (k == "folder_log" and folder_log)}
    if dari_config:
        print(f"  setelan diterapkan: {dari_config}", flush=True)

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
    sumber_suluh = []   # (device, label, warna)
    lb = cari_loopback(args.device)
    sumber_suluh.append((lb, "lawan", HIJAU))
    if args.mic:
        sumber_suluh.append((cari_mic(args.mic_device), "saya", CYAN))
        print(f"{KUNING}  ⚠ PERINGATAN: pakai HEADSET saat --mic!{KELUAR}", flush=True)
        print(f"{KUNING}    Tanpa headset, mic ikut menangkap suara lawan yang keluar dari{KELUAR}", flush=True)
        print(f"{KUNING}    speaker → percakapan lawan tercatat DOBEL (label lawan + saya).{KELUAR}", flush=True)
    transcribe = bikin_transcriber(model_ukuran, lang)

    nama_log = datetime.now().strftime("live-captions_%Y%m%d_%H%M%S.txt")
    if folder_log:
        nama_log = os.path.join(folder_log, nama_log)
    else:
        # default: folder tempat live-captions.py berada (bukan cwd utk aman)
        nama_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), nama_log)
    path_log = os.path.abspath(nama_log)
    print("")
    print("  " + "=" * 66)
    print("  CATATAN PERCAKAPAN AKAN TERSIMPAN DI FILE INI:")
    print(f"    {path_log}")
    print("  (terisi otomatis selama program jalan — dibuka pakai Notepad)")
    print("  Untuk berhenti program: tekan Ctrl+C di jendela ini")
    print("  " + "=" * 66)
    print("", flush=True)

    import queue
    antre = queue.Queue()
    BERJALAN = True
    for dev, label, _warna in sumber_suluh:
        threading.Thread(target=thread_rekam, args=(dev, antre, label), daemon=True).start()

    # keadaan per sumber: buffer audio + penghitung sampel baru + tick parsial
    state = {label: {"audio": np.zeros(0, dtype=np.float32), "baru": 0, "tick": 0.0}
             for _dev, label, _w in sumber_suluh}
    dua_sumber = len(sumber_suluh) > 1     # label (lawan)/(saya) hanya saat --mic
    f_log = open(nama_log, "a", encoding="utf-8")

    def segmen_baru(ts):
        """Daftar speech timestamps dari pustaka, terjemah ke interval (a, b)."""
        return [(int(s["start"]), int(s["end"])) for s in ts]

    def proses_sumber(label, warna):
        """VAD + transkripsi untuk buffer satu sumber. Dipanggil per tick."""
        st = state[label]
        audio = st["audio"]
        if st["baru"] < CHUNK:
            return
        st["baru"] = 0

        ts = get_speech_timestamps(audio, VAD_OPSI, sampling_rate=HR)
        segs = segmen_baru(ts)
        if not segs:
            # tak ada bicara sama sekali → buang buffer (hening) biar hemat
            if len(audio) > HR * 3:
                st["audio"] = audio[len(audio) - HR * 1:]
            return

        mulai, akhir = segs[0]   # cek segmen yang sedang berlangsung
        # segmen "selesai" = ekornya hening TAIL_NDAGU sampel, atau sudah mentok panjang maks
        masih_bicara = akhir >= len(audio) - TAIL_NDAGU
        panjang = min(akhir, len(audio)) - mulai

        if masih_bicara:
            if args.partial and panjang > PANJANG_MIN and panjang - st["tick"] > HR // 2:
                uji = audio[mulai:min(akhir, len(audio))]
                st["tick"] = panjang
                teks = transcribe(uji)
                if teks:
                    etiket = f"{label}) " if dua_sumber else ""
                    sys.stdout.write(f"\r{warna}[...]  ({etiket}{teks}{KELUAR}   ")
                    sys.stdout.flush()
            # segmen terlalu panjang → potong paksa biar caption keluar
            if panjang >= PANJANG_MAKS:
                masih_bicara = False
                akhir = mulai + PANJANG_MAKS
        if masih_bicara:
            return

        if panjang < PANJANG_MIN:
            uji = None
        else:
            uji = audio[mulai:min(akhir, len(audio))]
            teks = transcribe(uji).strip()
            jam = datetime.now().strftime("%H:%M:%S")
            if teks:
                sys.stdout.write("\r" + " " * 120 + "\r")   # bersihkan baris parsial
                etiket = f"({label}) " if dua_sumber else ""
                print(f"[{jam}] {warna}{etiket}{teks}{KELUAR}", flush=True)
                f_log.write(f"[{jam}] {etiket}{teks}\n")
                f_log.flush()

        # buang semua audio sampai akhir segmen: kalau sisakan "konteks"
        # yang memuat ekor bicara, VAD mendeteksi ulang segmen sama tiap
        # tick → teks kembar (bug dedup yang sudah diperbaiki)
        st["audio"] = audio[min(akhir, len(audio)):]
        st["tick"] = 0.0

    t_mulai = time.time()
    try:
        from faster_whisper.vad import get_speech_timestamps
        while BERJALAN:
            if args.durasi and time.time() - t_mulai > args.durasi:
                break
            time.sleep(0.15)
            # masukkan tiap potongan dari antrean ke buffer sumbernya
            while not antre.empty():
                sumber, data = antre.get()
                st = state[sumber]
                st["audio"] = np.concatenate([st["audio"], data]) if len(st["audio"]) else data
                st["baru"] += len(data)

            for _dev, label, warna in sumber_suluh:
                proses_sumber(label, warna)
    except KeyboardInterrupt:
        pass
    finally:
        BERJALAN = False
        try:
            f_log.close()
        except Exception:
            pass
        print(f"\n  Selesai. Catatan percakapan lengkap tersimpan di:\n    {path_log}\n  (buka pakai Notepad: klik kanan file → open with → Notepad)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass