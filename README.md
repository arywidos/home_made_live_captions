# Live Captions — Teks Otomatis dari Semua Suara di Komputer

Program ini menampilkan **teks langsung dari suara yang keluar di komputer Anda**
— bukan cuma dari satu aplikasi. Semua jenis meeting dan call bisa:
**WhatsApp Desktop, Zoom, Google Meet, Discord, Telegram call**, bahkan video
YouTube. Anda buka programnya, jalankan call, dan percakapan otomatis
muncul sebagai teks di layar (dan tersimpan ke file log).

Tidak perlu internet saat dipakai — semua diproses di komputer sendiri
(komputer tidak mengirim rekaman anda ke mana-mana).

---

## Sebelum mulai — apa yang dibutuhkan

| Kebutuhan | Keterangan |
|---|---|
| Komputer Windows 10 / 11 | program ini khusus Windows |
| Python (gratis) | langkah 1 di bawah mengajarkannya |
| Internet | hanya untuk instalasi pertama — **unduhan model suara cukup besar**, lihat peringatan di bawah |
| Kartu grafis NVIDIA (opsional) | kalau ada, teks keluar jauh lebih cepat & akurat. Tidak punya? Tidak apa-apa — tetap bisa jalan lewat CPU dengan aturan di bawah |

> ### ⚠️ PERINGATAN: unduhan pertama bisa lama
> Saat pertama kali dijalankan, program **mengunduh "model whisper medium"
> sekitar 1,5 GB** dari internet. Waktunya **tergantung kecepatan internet
> Anda** — bisa 3 menit sampai lebih dari 30 menit. Selama itu layar mungkin
> terlihat diam/di angka persen — **biarkan saja, jangan ditutup**.
> Unduh cukup **satu kali saja**; berikutnya langsung pakai tanpa unduh ulang.
>
> Internet lambat dan tidak sabar? Jalankan dengan model kecil (480 MB):
> lihat bagian **"Internet lambat?"** di bawah. Kualitasnya agak kurang, tapi
> langsung terunduh cepat.

---

## Langkah instalasi

Buka program **PowerShell** (klik Start, ketik `powershell`, Enter), lalu
salin-tempel perintah satu per satu (perintah yang berwarna abu).

### 1. Pasang Python

1. Buka halaman <https://www.python.org/downloads/windows/>
2. Unduh dan pasang. **PENTING:** di layar pemasang (installer) centang
   **"Add Python to PATH"** sebelum klik Install.
3. Pastikan jalan, ketik di PowerShell:

   ```
   python --version
   ```

   Kalau muncul angka versi (mis. `Python 3.13.x`) — lanjut.
   Kalau bilang "program tidak dikenal" — ulangi langkah 2 dan jangan lupa
   centang "Add Python to PATH".

### 2. Masuk ke folder program

```
cd C:\DATAS\live-captions
```

### 3. Buat "kotak alat" Python khusus program ini

(Kotak ini untuk menjaga program lain tidak terganggu)

```
python -m venv .venv
```

Jalankan **hanya pada pemasangan pertama** — di berikutnya tidak perlu ulang.

### 4. Pasang bahan-bahan program (butuh internet, ±beberapa menit)

```
.venv\Scripts\pip install faster-whisper soundcard numpy colorama nvidia-cublas-cu12 nvidia-cudnn-cu12 "av==19.0.0"
```

### 5. Jalankan program pertama kali

```
.venv\Scripts\python.exe -X utf8 live-captions.py
```

**Di sinilah unduhan 1,5 GB terjadi** (lihat peringatan di atas — biarkan
sampai selesai). Kalau sudah selesai, muncul tulisan seperti:

```
  loopback: Speakers (Realtek(R) Audio)
  Whisper 'medium' jalan di CUDA float16 | bahasa 'id'
  log: live-captions_20261005_173421.txt | Ctrl+C untuk keluar
```

Mulai detik itu, **suara apa pun yang keluar dari speaker otomatis jadi teks**.
Uji dengan memutar video berbicara di YouTube — teksnya harus muncul.

- Untuk **keluar**: tekan `Ctrl+C` di jendela PowerShell.

### 6. (Sekali saja) Bikin tombol klik-dukali

Tutup PowerShell-nya, berikutnya tinggal klik dua kali **`jalankan-captions.bat`**
yang ada di folder `C:\DATAS\live-captions` (boleh dibuatkan pintasan di
Desktop dengan klik kanan → Kirim ke → shortcut).

---

## Cara pakai saat meeting / call

1. Klik dua kali `jalankan-captions.bat`
2. Tunggu hingga muncul `Whisper 'medium' jalan di ...`
3. Buka WhatsApp Desktop / Zoom / whatever — mulai call
4. Suara lawan bicara tampil jadi baris `[10:23:41] kalimatnya ...`
   Isi percakapan juga tersimpan di file `live-captions_tanggal-jam.txt`
5. Setelah selesai, ke jendela hitam tadi → `Ctrl+C`

> **Mic Anda sendiri TIDAK direkam** — hanya suara yang keluar dari speaker
> (suara lawan bicara). Itu biasanya justru diinginkan demi privasi.

---

## Opsi yang sering dipakai

Ketik ini di PowerShell dari folder `C:\DATAS\live-captions`:

| Butuh apa | Perintah |
|---|---|
| Meeting bahasa Inggris | `.venv\Scripts\python.exe -X utf8 live-captions.py --lang en` |
| Teks muncul *semata bicara masih berlangsung* | tambah `--partial` |
| Suara keluar lewat **headset Bluetooth** | `--device soundcore` (ganti sesuai nama headset — contoh: `--device Sony`, `--device JBL`) |
| Cuma pilih 1 file mp3 utk uji tanpa call | `.venv\Scripts\python.exe -X utf8 uji-playback.py namamp3.mp3` |

### Internet lambat?

Ganti model yang kecil (unduh hanya ~480 MB):

```
.venv\Scripts\python.exe -X utf8 live-captions.py --model small
```

Ini **wajib dipakai** jika komputer Anda TIDAK punya kartu grafis NVIDIA —
di CPU saja model `medium` terasa lambat, `small` lebih muat.

---

## Solusi masalah umum

| Masalah | Solusi |
|---|---|
| "python tidak dikenal" | Ulang langkah 1; centang "Add Python to PATH" |
| Teks tidak muncul | Pastikan call/video **berbunyi lewat yang sama** dengan `loopback:` di info program. Kalau pakai headset BT, tambahkan `--device` nama headset |
| Teks muncul tapi lambat muncul | Komp Anda tanpa GPU: pakai `--model small` |
| Perintah `pip` error | Pastikan langkah 3 sudah sukses; ulangi langkah 4 |
| Unduh model berhenti di tengah | Jalankan lagi — unduhan lanjut dari tempat berhenti |
| Tulisan aneh/simbol kotak di PowerShell | Klik kanan header jendela → Properties → Font pilih *Consolas* atau *Lucida Console* |

Masih ada yang kurang jelas? Tanyakan saja — program ini memang buatan sendiri.