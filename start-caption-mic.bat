@echo off
rem start-caption-mic.bat — klik dua kali untuk mulai caption live dari MIC
rem  (pakai HEADSET supaya suara speaker tidak ikut terekam!)
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
rem GPU muat model Whisper medium SEKALI saja; dua instansi = yang kedua macet,
rem mic pun terdiam (ini penyebab program "hung").
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'live-captions' } | ForEach-Object { Write-Host ('  [x] mematikan sesi lama pid ' + $_.ProcessId); Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
echo  ============================================
echo   ^|  PASTIKAN PAKAI HEADSET!  ^|
echo   Tanpa headset, suara speaker ikut terekam
echo   dan caption jadi berulang-ulang.
echo  ============================================
echo.
.venv\Scripts\python.exe -X utf8 live-captions.py --mic --partial
echo.
echo  Program ditutup. Log percakapan ada di file live-captions_*.txt
pause