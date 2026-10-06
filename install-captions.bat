@echo off
rem install-captions.bat - klik dua kali: pasang semua bahan live-captions
rem di Windows (Python, kotak alat venv, pustaka, CUDA). Aman diulang:
rem kalau sudah terpasang, langkah yang berjalan cuma pemeriksaan.
cd /d "%~dp0"
title Pasang live-captions
echo.
echo  ============================================
echo   PEMASANGAN CAPTIONS - WINDOWS
echo  ============================================
echo.

rem -- 1) cari Python -----------------------------------------------------
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
  where python >nul 2>nul && set "PY=python"
)
if not defined PY goto :tanpa_python
%PY% --version
if errorlevel 1 goto :tanpa_python
echo  [1/4] Python ada.
echo.

rem -- 2) kotak alat (venv) ------------------------------------------------
if exist ".venv\Scripts\python.exe" goto :venv_ada
echo  [2/4] Membuat kotak alat Python khusus...
%PY% -m venv .venv
if errorlevel 1 (
  echo   [!] Gagal membuat kotak alat. Laporkan pesan di atas ke pembuat program.
  pause
  exit /b 1
) else goto :venv_ada
:venv_ada
echo  [2/4] Kotak alat Python siap.
echo.

rem -- 3) pustaka ----------------------------------------------------------
.venv\Scripts\python.exe -c "import faster_whisper, soundcard, numpy, colorama" >nul 2>nul
if not errorlevel 1 (
  echo  [3/4] Pustaka sudah lengkap - tidak perlu unduh ulang.
) else (
  echo  [3/4] Memasang pustaka - butuh internet, beberapa menit...
  .venv\Scripts\python.exe -m pip install faster-whisper soundcard numpy colorama "av==19.0.0"
  if errorlevel 1 (
    echo   [!] Pemasangan pustaka gagal - cek koneksi internet, lalu klik lagi file ini.
    pause
    exit /b 1
  )
)
echo.

rem -- 4) percepat GPU bila ada kartu NVIDIA --------------------------------
where nvidia-smi >nul 2>nul
if errorlevel 1 if not exist "C:\Windows\System32\nvidia-smi.exe" goto :tanpa_nvidia
echo  [4/4] Kartu NVIDIA terdeteksi - memasang CUDA untuk kecepatan penuh...
.venv\Scripts\python.exe -m pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
if errorlevel 1 echo   (CUDA gagal dipasang - program tetap jalan, sedikit lebih lambat)
goto :selesai
:tanpa_nvidia
echo  [4/4] Tidak ada kartu NVIDIA - program jalan lewat CPU, cukup untuk caption.
echo        Unduhan model pertama kali masih terjadi di langkah uji nanti.
:selesai
echo.
echo  ============================================
echo   PEMASANGAN SELESAI
echo  ============================================
echo.
echo  Berikutnya: klik dua kali jalankan-captions.bat
echo  (unduhan model suara besar terjadi di RUN PERTAMA - biarkan sampai beres)
echo  Kalau mau langsung diuji sekarang, jalankan dari PowerShell:
echo    .venv\Scripts\python.exe -X utf8 live-captions.py
echo.
pause
exit /b 0

:tanpa_python
echo  [!] Python tidak terdeteksi.
echo      1. Buka https://www.python.org/downloads/windows/
echo      2. Pasang Python, CENTANG "Add Python to PATH" di pemasang
echo      3. Setelah terpasang, klik lagi file install-captions.bat ini
echo.
pause
exit /b 1