#!/bin/bash
# install-captions.command — klik dua kali: pasang semua bahan live-captions
# di macOS (Python → pustaka → cek BlackHole). Aman diulang: kalau sudah
# terpasang, langkah yang berjalan cuma pemeriksaan.
cd "$(dirname "$0")" || exit 1
echo
echo "============================================"
echo " PEMASANGAN CAPTIONS - macOS"
echo "============================================"
echo

# -- 0) ambil program dari GitHub bila folder masih kosong -----------------
if [ ! -f live-captions.py ]; then
  echo "[0/4] Mengunduh program dari GitHub (sekali saja, butuh internet)..."
  TMPZIP="/tmp/live-captions-repo.zip"
  TMPEXT="/tmp/live-captions-repo"
  curl -L -o "$TMPZIP" https://github.com/arywidos/home_made_live_captions/archive/refs/heads/main.zip \
    || { echo "[!] Unduh gagal - cek koneksi internet, lalu klik lagi file ini."; exit 1; }
  rm -rf "$TMPEXT" && mkdir -p "$TMPEXT"
  unzip -q "$TMPZIP" -d "$TMPEXT" \
    || { echo "[!] Gagal membuka ZIP - coba lagi."; exit 1; }
  tar -C "$TMPEXT/home_made_live_captions-main" --exclude install-captions.command -cf - . | tar -xf - -C .
  rm -rf "$TMPEXT" "$TMPZIP"
  echo "[0/4] Program sudah diunduh ke folder ini."
  echo
fi

# -- 1) cari Python 3 ------------------------------------------------------
if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
  echo "[1/4] Python ada ($(python3 --version 2>&1))."
else
  echo "[!] Python 3 tidak terdeteksi."
  if command -v brew >/dev/null 2>&1; then
    echo "      Mencoba pasang lewat Homebrew (butuh internet, beberapa menit)..."
    brew install python3 || { echo "      [!] Gagal. Pasang manual: https://www.python.org/downloads/macos/"; exit 1; }
  else
    echo "      1. Buka https://www.python.org/downloads/macos/"
    echo "      2. Unduh dan pasang seperti aplikasi Mac biasa"
    echo "      3. Klik lagi file install-captions.command ini"
    exit 1
  fi
fi
echo

# -- 2) pustaka ------------------------------------------------------------
if ! .venv/bin/python3 -c "import faster_whisper, soundcard, numpy, colorama" 2>/dev/null; then
  if [ ! -x ".venv/bin/python3" ]; then
    echo "[2/4] Membuat kotak alat Python khusus..."
    python3 -m venv .venv || { echo "[!] Gagal membuat kotak alat."; exit 1; }
  fi
  echo "[3/4] Memasang pustaka - butuh internet, beberapa menit..."
  .venv/bin/pip install faster-whisper soundcard numpy colorama "av==19.0.0" \
    || { echo "[!] Pemasangan pustaka gagal - cek koneksi internet, lalu klik lagi file ini."; exit 1; }
else
  echo "[2/4] Kotak alat Python siap."
  echo "[3/4] Pustaka sudah lengkap - tidak perlu unduh ulang."
fi
echo

# -- 4) tombol klik dua kali boleh dipakai ---------------------------------
chmod +x install-captions.command 2>/dev/null
chmod +x jalankan-captions.command 2>/dev/null

# -- cek BlackHole (wajib di Mac untuk menangkap suara speaker) -------------
if system_profiler SPAudioDataType 2>/dev/null | grep -qi "BlackHole"; then
  echo "[4/4] BlackHole terpasang."
else
  echo "[4/4] Driver BlackHole belum terpasang - WAJIB untuk caption suara speaker:"
  echo "      1. Buka https://existential.audio/blackhole/  -> unduh BlackHole 2ch"
  echo "         (kalau sudah punya Homebrew, bisa juga: brew install blackhole-2ch)"
  echo "      2. Buka file .pkg -> Install (mungkin diminta password Mac)"
  echo "      3. Audio MIDI Setup -> tombol + -> Create Multi-Output Device ->"
  echo "         centang BlackHole 2ch + MacBook Speakers -> lalu pilih"
  echo "         Multi-Output Device sebagai Sound Output"
  echo "         (detail lengkap: README.md bagian macOS langkah 2-3)"
  echo "      Program tetap bisa dijalankan, tapi teks baru muncul setelah"
  echo "      BlackHole terpasang dan Multi-Output Device diaktifkan."
fi
echo
echo "============================================"
echo " PEMASANGAN SELESAI"
echo "============================================"
echo
echo "Berikutnya: klik dua kali jalankan-captions.command"
echo "(unduhan model suara besar terjadi di RUN PERTAMA - biarkan sampai beres)"
echo
exit 0