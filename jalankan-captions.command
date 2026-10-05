#!/bin/bash
# jalankan-captions.command — klik dua kali di Finder untuk mulai caption live (macOS)
# Boleh juga dijalankan dari Terminal: ./jalankan-captions.command --mic
# Argumen diteruskan ke live-captions.py, mis.: ./jalankan-captions.command --lang en
cd "$(dirname "$0")" || exit 1

if [ ! -x ".venv/bin/python3" ]; then
  echo ""
  echo "  [!] Kotak alat Python (.venv) belum ada."
  echo "      Baca README.md bagian \"Instalasi di MacBook\" langkah 1-5 dulu."
  echo ""
  read -n 1 -s -r -p "Tekan tombol apa saja untuk menutup jendela ini..."
  exit 1
fi

.venv/bin/python3 -X utf8 live-captions.py "$@"

echo ""
echo "  Program ditutup. Log percakapan ada di file live-captions_*.txt"
read -n 1 -s -r -p "Tekan tombol apa saja untuk menutup jendela ini..."