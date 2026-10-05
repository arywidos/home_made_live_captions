@echo off
rem caption-auto.bat — caption suara SPEAKER, deteksi otomatis
rem  (tanpa mic: percakapan lawan / video, tidak ada label (saya))
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo.
  echo  [!] Kotak alat Python belum ada. Baca README.md langkah 1-3 dulu.
  echo.
  pause
  exit /b 1
)
echo.
rem — pangatkan kusut: matikan instansi live-captions yang masih hidup.
rem GPU muat model Whisper medium SEKALI saja; dua instansi = yang kedua macet.
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'live-captions' } | ForEach-Object { Write-Host ('  [x] mematikan sesi lama pid ' + $_.ProcessId); Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
echo  ============================================
echo   Caption SUARA SPEAKER aktif — deteksi otomatis
echo  ============================================
echo.
.venv\Scripts\python.exe -X utf8 live-captions.py --partial --lang auto
echo.
echo  Program ditutup. Log percakapan ada di file live-captions_*.txt
pause