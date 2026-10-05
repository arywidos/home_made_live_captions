# Live Captions — Teks Otomatis dari Semua Suara di Komputer

Program ini menampilkan **teks langsung dari suara yang keluar di komputer Anda**
— bukan cuma dari satu aplikasi. Semua jenis meeting dan call bisa:
**WhatsApp Desktop, Zoom, Google Meet, Discord, Telegram call**, bahkan video
YouTube. Anda buka programnya, jalankan call, dan percakapan otomatis
muncul sebagai teks di layar (dan tersimpan ke file log).

Tidak perlu internet saat dipakai — semua diproses di komputer sendiri
(komputer tidak mengirim rekaman anda ke mana-mana).

Bisa dipakai di **Windows** maupun **MacBook (macOS)** — instalasi di Mac
ada langkah tambahan (driver BlackHole), lihat bagian **"Instalasi di MacBook"**.

---

## Sebelum mulai — apa yang dibutuhkan

| Kebutuhan | Keterangan |
|---|---|
| Windows 10/11, atau MacBook Apple Silicon (M1/M2/M3/M4) | macOS Intel belum diuji |
| Python (gratis) | langkah 1 di bawah mengajarkannya |
| Internet | hanya untuk instalasi pertama — **unduhan model suara cukup besar**, lihat peringatan di bawah |
| Kartu grafis NVIDIA (opsional, Windows) | kalau ada, teks keluar jauh lebih cepat & akurat. Tidak punya? Tidak apa-apa — tetap bisa jalan lewat CPU dengan aturan di bawah. Di Mac, CPU-nya sendiri (chip M) sudah cukup. |

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

## Instalasi di MacBook (macOS)

> ### ⚠️ Kenapa di Mac ada langkah tambahan?
> Apple tidak menyediakan cara resmi untuk "merekam suara yang keluar dari
> Mac" (beda dengan Windows). Solusinya pakai driver gratis **BlackHole** —
> semacam tabung virtual tempat suara sistem mengalir, dan program ini
> menampungnya dari tabung itu. Pasangnya sekali saja (~3 menit).

### 1. Pasang Python

Buka **Terminal** (klik Spotlight 🔍 di pojok atas, ketik `terminal`, Enter):

```
python3 --version
```

Kalau muncul versi 3.10 atau lebih tinggi — langsung langkah 2.
Kalau tidak, unduh dari <https://www.python.org/downloads/macos/> dan pasang
seperti aplikasi Mac biasa, atau (kalau sudah punya Homebrew) cukup:

```
brew install python3
```

### 2. Pasang driver BlackHole

1. Buka <https://existential.audio/blackhole/> → unduh **BlackHole 2ch**
2. Buka file `.pkg` hasil unduhan → Install (mungkin diminta password Mac)
3. Restart aplikasi yang memutar suara jika perlu

(Alternatif kalau sudah punya Homebrew: `brew install blackhole-2ch`)

### 3. Set "Multi-Output Device" — biarkan suara tetap ke speaker

Tanpa langkah ini, suara diarahkan ke BlackHole dan **kamu tidak akan
mendengar apa-apa**. Begini solusinya (satu kali setup):

1. Buka aplikasi **Audio MIDI Setup**: Spotlight 🔍 → ketik `audio midi`
2. Di jendela itu klik tombol **+** di kiri bawah → **Create Multi-Output Device**
3. Daftarkan (centang) dua device: **BlackHole 2ch** dan **MacBook Pro Speakers**
4. Klik kanan Multi-Output Device tadi → **Use This Device For Sound Output**
5. (Sekalian di daftar kiri itu, klik kanan → centang "Playthrough" TIDAK perlu)

Sekarang semua suara Mac mengalir ke speaker **sekaligus ke BlackHole**.

> Catatan kecil: tombol volume keyboard hanya mengatur speaker Mac di setup
> ini (kelemahan macOS, bukan program ini). Kalau mengganggu, atur volume
> dari aplikasi (Spotify/Zoom/VLC) atau System Settings → Sound.

### 4. Izinkan Terminal mengakses Microphone

Saat program pertama dijalankan, Mac akan bertanya
**"Terminal wants to access the microphone"** → klik **Allow**.
Bila tertinggal: **System Settings → Privacy & Security → Microphone** →
centang Terminal.

### 5. Ambil program ini & pasang bahan-bahannya

Di Terminal:

```
cd ~/Downloads
git clone https://github.com/arywidos/home_made_live_captions.git live-captions
cd live-captions
python3 -m venv .venv
.venv/bin/pip install faster-whisper soundcard numpy colorama "av==19.0.0"
```

(Tidak punya `git`? Mac biasanya sudah punya — kalau diminta pasang
"Command Line Developer Tools", klik saja Install. Kalau tidak juga bisa:
unduh ZIP dari halaman GitHub repo ini → tombol hijau Code → Download ZIP,
lalu buka dan masuk foldernya.)

(Bagian `nvidia-cublas-cu12 nvidia-cudnn-cu12` di Windows tidak diperlukan
di Mac — Mac tidak punya GPU itu.)

### 6. Jalankan pertama kali

```
.venv/bin/python3 -X utf8 live-captions.py
```

**Peringatan unduhan tetap berlaku di Mac:** unduh model whisper medium
**±1,5 GB**, lama tergantung internet (3–30 menit ke atas) — biarkan sampai
beres, cukup sekali saja.

Kalau sukses, muncul:

```
  input: BlackHole 2ch (via BlackHole)
  Whisper 'medium' jalan di CPU int8 | bahasa 'id'
```

Uji: putar video YouTube yang ada bicara — teks harus muncul.
Untuk **keluar**: `Ctrl+C` di Terminal.

### 7. (Sekali saja) Siapkan tombol klik-dukali

Sama seperti Windows punya `jalankan-captions.bat`, di Mac ada
**`jalankan-captions.command`** — klik dua kali di Finder, otomatis buka
Terminal dan mulai. Aktifkan sekali dari Terminal:

```
chmod +x jalankan-captions.command
```

Catatan: kalau repo ini diunduh sebagai ZIP (bukan git clone), macOS mungkin
"kunci" file itu karena berasal dari internet — kalau muncul itu, klik kanan
file-nya → **Open** sekali saja (macOS akan mempercayainya).

Tambahan argumen juga bisa, mis. klik dua kali tidak fleksibel — dari
Terminal: `./jalankan-captions.command --mic` atau `--lang en`.

> **Trik Mac yang nyaman:** karena semua suara (termasuk percakapan yang kamu
> ikut di meeting) lewat tempat yang sama, tak ada pengaturan tambahan per
> aplikasi. WhatsApp Desktop, Zoom, Meet di browser — semua otomatis.

---

## Cara pakai saat meeting / call

**Windows:** klik dua kali `jalankan-captions.bat`
**Mac:** klik dua kali `jalankan-captions.command` di Finder (aktifkan dulu sekali: lihat bagian macOS langkah 7), atau dari Terminal: `./jalankan-captions.command`

1. Tunggu hingga muncul `Whisper 'medium' jalan di ...`
2. Buka WhatsApp Desktop / Zoom / whatever — mulai call
3. Suara lawan bicara tampil jadi baris `[10:23:41] kalimatnya ...`
   Isi percakapan juga tersimpan di file `live-captions_tanggal-jam.txt`
4. Setelah selesai → `Ctrl+C` di jendela program

> **Mic Anda sendiri TIDAK direkam** — hanya suara yang keluar dari speaker
> (suara lawan bicara). Itu biasanya justru diinginkan demi privasi.
> Kalau suara Anda sendiri juga ingin jadi caption: tambah `--mic`
> (lihat tabel opsi di bawah).

---

## Suara Anda sendiri juga jadi caption (opsi `--mic`)

Secara default program hanya menangkap **suara yang keluar dari speaker**
(tersirat: suara lawan bicara). Kalau Anda ingin *apa yang Anda ucapkan juga*
tampil jadi teks — untuk jadwal hasil rapat, catatan, atau aksesibilitas —

```
Windows : .venv\Scripts\python.exe -X utf8 live-captions.py --mic
Mac     : .venv/bin/python3 -X utf8 live-captions.py --mic
```

Hasilnya otomatis berlabel biar tahu siapa bicara:

```
[10:23:41] (lawan) jadi besok kita review design-nya ya
[10:24:02] (saya)  oke, saya kirim draft malam ini
[10:24:15] (lawan) siap, terima kasih
```

- hijau `(lawan)` = suara keluar dari speaker  ·  biru `(saya)` = suara dari mic Anda
- mic mana yang dipakai bisa diganti: tambah `--mic-device "Headset"`
  (ganti sesuai nama mic yang muncul ketika mic tidak tampil di info program)
- pakai `--mic` tanpa argumen = mic default komputer

### ⚠️ Kenapa disarankan pakai headset saat `--mic`

Tanpa headset, mic laptop ikut menangkap **suara lawan yang keluar dari
speaker** — akibatnya percakapan lawan tercatat dobel: sekali berlabel
`(lawan)`, sekali lagi berlabel `(saya)`. Ini kami buktikan sendiri saat
pengujian (mic laptop menangkap siaran uji terang-terang). Dengan headset — earphone kabel maupun Bluetooth — suara
lawan tidak bocor ke mic, jadi label tetap bersih.

---

## Opsi yang sering dipakai

Windows — ketik di PowerShell dari folder `C:\DATAS\live-captions`;
Mac — ketik di Terminal dari folder repo, dengan pengganti
`.venv\Scripts\python.exe` = `.venv/bin/python3`.

| Butuh apa | Perintah |
|---|---|
| Meeting bahasa Inggris | ... `--lang en` |
| Teks muncul *meski bicara masih berlangsung* | tambah `--partial` |
| **Suara saya sendiri juga jadi caption** | tambah `--mic`. Hasil jadi berlabel: hijau `(lawan)`, biru `(saya)` — contoh `[10:23:41] (saya) oke saya kirim malam ini`. **Pakai headset!** tanpa headset, mic ikut menangkap suara lawan dari speaker → baris lawan dobel |
| Mic yang dipakai bukan mic default (Windows/`--mic`) | tambah `--mic-device` nama mic, mis. `--mic-device "Headset"` |
| Windows: suara lewat **headset Bluetooth** | `--device soundcore` (ganti sesuai nama headset — contoh: `--device Sony`, `--device JBL`) |
| Mac: pilih input selain BlackHole | `--device BlackHole` (default) atau nama mic lain |
| Cuma pilih 1 file mp3 utk uji tanpa call | ... `uji-playback.py namamp3.mp3` |

### Bahasa Indonesia, Inggris, atau campuran?

Bahasanya diketik lewat `--lang` (contoh ada di tabel opsi di atas):

| Rapat/call Anda | Yang dipakai | Alasan |
|---|---|---|
| Bahasa Indonesia | **tidak perlu apa-apa** (default = `id`) | Whisper sering salah menebak bahasa kalau ditanyakan tiap kalimat — jadi kami kunci Indonesia |
| Bahasa Inggris | `--lang en` | kunci Inggris |
| **Campuran Indonesia-English** ("gimana hasil benchmark-nya?") | tetap **default saja** (`id`) | kata Inggris yang diselingi tetap ditulis benar meski bahasa utama dikunci Indonesia — sudah dites; ini lebih akurat daripada `auto` |
| Bahasa sungguhan sangat tidak pasti (beda-beda tiap orang) | `--lang auto` | Whisper menebak tiap kalimat. Untuk kalimat pendek tebakannya sering salah (pernah salah duga bahasa Indonesia jadi Tagalog) — pakai hanya kalau memang terpaksa |

> Jadi jawaban singkatnya: **mix Indonesia-English tidak perlu opsi apa pun** —
> default `id` sudah menangani istilah Inggris yang diselingi.

### Internet lambat?

Ganti model yang kecil (unduh hanya ~480 MB):

```
live-captions.py --model small
```

Ini disarankan juga kalau komputer **tanpa kartu grafis NVIDIA** (Windows)
atau Mac lama — di CPU, model `medium` lebih lambat dari `small`.
Di MacBook M1/M2 ke atas, `medium` biasanya masih nyaman.

### Mengubah lokasi penyimpanan catatan (config.txt)

Setiap mulai, program membuat file log baru. Mau disimpan ke tempat lain
(mis. folder Documents)? Edit file **`config.txt`** di dalam folder program
(buka dengan Notepad / TextEdit):

1. Cari baris yang ditulis `#   folder_log = C:\Users\NamaAnda\Documents\catatan-rapat`
2. **Hapus tanda `#` dan `spasi` di depannya** (itu yang berarti "sudah aktif")
3. Ganti dengan folder yang Anda mau, lalu simpan file
4. Jalankan ulang program — di info awal akan muncul
   `setelan diterapkan: {'folder_log': ...}` sebagai konfirmasi

Folder yang belum ada akan dibuat otomatis. Di file yang sama juga bisa
disimpan **bahasa** (`lang = en`) dan **ukuran model** (`model = small`)
supaya tak perlu diketik tiap mulai.

---

## Solusi masalah umum

| Masalah | Solusi |
|---|---|
| Baris `(saya)` tidak pernah muncul (meski `--mic`) | Cek mic tidak tumpang/mute di Windows (tombol +volume) atau di call Zoom/WhatsApp. Cek juga **Settings → Privacy → Microphone → allow desktop apps**. Mic lain? tambahkan `--mic-device` nama mic |
| Percakapan lawan tercatat dobel (juga berlabel `(saya)`) | Mic menangkap suara speaker — pakai headset, atau jangan pakai `--mic` |
| "python tidak dikenal" (Windows) | Ulang langkah 1; centang "Add Python to PATH" |
| Teks tidak muncul | Pastikan call/video **berbunyi lewat device yang sama** dengan `loopback:`/`input:` di info program. Headset BT di Windows? tambahkan `--device` nama headset. Mac: pastikan Multi-Output Device aktif |
| Mac: "device 'BlackHole' tidak ketemu" | Pasang BlackHole (bagian macOS langkah 2) — kalau sudah pasang, keluar-masuk atau restart agar device terbaca |
| Mac: program minta izin microphone lama berhenti | System Settings → Privacy & Security → Microphone → centang Terminal |
| Mac: suara tidak terdengar tapi teks jalan | Lupa buat Multi-Output Device — bagian macOS langkah 3 |
| Teks muncul tapi lambat muncul | Tanpa GPU / Mac lama: pakai `--model small` |
| Perintah `pip` error | Pastikan langkah venv sudah sukses; ulangi langkah pemasangan bahan |
| Unduh model berhenti di tengah | Jalankan lagi — unduhan lanjut dari tempat berhenti |
| Tulisan aneh/simbol kotak di PowerShell | Klik kanan header jendela → Properties → Font pilih *Consolas* atau *Lucida Console* |

Masih ada yang kurang jelas? Tanyakan saja — program ini memang buatan sendiri.