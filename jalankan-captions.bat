@echo off
rem jalankan-captions.bat — klik dua kali untuk mulai caption live
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo.
  echo  [!] Kotak alat Python belum ada. Baca README.md langkah 1-3 dulu.
  echo.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -X utf8 live-captions.py %*
echo.
echo  Program ditutup. Log percakapan ada di file live-captions_*.txt
pause