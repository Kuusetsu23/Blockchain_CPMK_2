# Praktikum 1B — Blockchain Voting

Program sederhana untuk simulasi **sistem voting berbasis Blockchain** menggunakan Python. Sistem terdiri dari beberapa node yang saling terhubung melalui HTTP untuk menyimpan data voting, melakukan validasi suara, penambangan block, serta sinkronisasi blockchain menggunakan **Longest-Chain Rule**.

## 📁 Struktur Direktori

```text
praktikum1b/
├── node.py                 # Program utama node blockchain
├── client.py               # CLI untuk voting, mining, tally, dan resolve
├── Dockerfile              # Konfigurasi Docker image
├── docker-compose.yml      # Konfigurasi jaringan multi-node
└── README.md               # Dokumentasi penggunaan
```

---

# 🚀 Cara Penggunaan

## 1. Menjalankan Node di Terminal Lokal

Buka **3 jendela terminal berbeda** di dalam direktori `praktikum1b/`.

### Terminal 1 — Node 1

Menjalankan node pada port `5001` dan menghubungkannya dengan Node 2 dan Node 3.

```powershell
python node.py 5001 localhost:5002,localhost:5003
```

### Terminal 2 — Node 2

Menjalankan node pada port `5002`.

```powershell
python node.py 5002 localhost:5001,localhost:5003
```

### Terminal 3 — Node 3

Menjalankan node pada port `5003`.

```powershell
python node.py 5003 localhost:5001,localhost:5002
```

Setelah ketiga perintah dijalankan, akan terbentuk jaringan yang terdiri dari **3 node blockchain** yang dapat saling berkomunikasi.

---

## 2. Menggunakan Client CLI

Buka **terminal baru** di dalam direktori `praktikum1b/` untuk menjalankan perintah melalui `client.py`.

### A. Memasukkan Suara Sah

Contoh memasukkan suara untuk **Paslon 1**:

```powershell
python client.py vote localhost:5001 "Paslon 1" "F55125001"
```

Contoh memasukkan suara untuk **Paslon 2**:

```powershell
python client.py vote localhost:5001 "Paslon 2" "C10123045"
```

NIM yang digunakan harus memenuhi ketentuan yang telah ditentukan oleh sistem, yaitu mahasiswa **Angkatan 2023–2025 / Semester 3–7**.

---

### B. Uji Penolakan Mahasiswa yang Belum Memenuhi Syarat

Contoh menggunakan NIM mahasiswa Angkatan 2026:

```powershell
python client.py vote localhost:5001 "Paslon 1" "F55126001"
```

Suara akan **DITOLAK** oleh node karena mahasiswa belum memenuhi persyaratan semester/angkatan yang telah ditentukan.

---

### C. Uji Penolakan Double Voting

Gunakan kembali NIM yang sebelumnya sudah melakukan voting:

```powershell
python client.py vote localhost:5001 "Paslon 2" "F55125001"
```

Suara akan **DITOLAK** karena NIM `F55125001` sudah tercatat pernah melakukan voting.

Hal ini digunakan untuk memastikan sistem dapat mencegah **double voting**.

---

### D. Melihat Isi Blockchain

Untuk melihat isi blockchain pada Node 2:

```powershell
python client.py chain localhost:5002
```

Perintah ini digunakan untuk melihat block yang tersimpan, termasuk informasi transaksi voting dan block lainnya.

---

### E. Melihat Rekapitulasi Suara

Untuk melihat hasil perolehan suara:

```powershell
python client.py tally localhost:5002
```

Perintah tersebut akan menampilkan jumlah suara yang diperoleh masing-masing pasangan calon berdasarkan transaksi yang terdapat pada blockchain.

---

### F. Menjalankan Longest-Chain Rule

Untuk melakukan proses sinkronisasi blockchain:

```powershell
python client.py resolve localhost:5003
```

Proses **resolve** digunakan untuk menerapkan aturan **Longest-Chain Rule**, yaitu node akan menggunakan rantai blockchain yang valid dan memiliki panjang paling besar ketika terdapat perbedaan rantai antar-node.

---

### G. Uji Pengiriman Suara Palsu

Untuk melakukan simulasi pengiriman data voting yang tidak valid:

```powershell
python client.py palsu localhost:5001
```

Perintah ini digunakan untuk menguji mekanisme validasi dan keamanan node terhadap transaksi voting palsu.

---

# 🐳 3. Menjalankan Menggunakan Docker

Selain menjalankan node secara langsung menggunakan Python, jaringan blockchain juga dapat dijalankan menggunakan **Docker Compose**.

Pastikan **Docker Desktop** sudah aktif sebelum menjalankan perintah berikut.

### A. Menjalankan Seluruh Node

Jalankan perintah:

```powershell
docker compose up --build -d
```

Perintah tersebut akan:

* Membuat Docker image berdasarkan `Dockerfile`.
* Menjalankan seluruh container node.
* Membentuk jaringan antar-container.
* Menjalankan node di background karena menggunakan opsi `-d`.

---

### B. Mengecek Status Container

Untuk melihat container yang sedang berjalan:

```powershell
docker compose ps
```

Pastikan seluruh node yang dikonfigurasi pada `docker-compose.yml` berada dalam status **running**.

---

### C. Mengirim Suara Melalui Docker

Walaupun node berjalan di dalam container, client tetap dapat digunakan melalui terminal lokal.

Contoh:

```powershell
python client.py vote localhost:5001 "Paslon 1" "A11124012"
```

Kemudian untuk melihat rekapitulasi suara:

```powershell
python client.py tally localhost:5002
```

---

### D. Menghentikan Seluruh Container

Setelah selesai melakukan praktikum, hentikan seluruh jaringan Docker dengan:

```powershell
docker compose down
```

Perintah ini akan menghentikan dan menghapus container yang dibuat oleh Docker Compose.

---

# 📌 Ringkasan Perintah

| Perintah                                            | Fungsi                                 |
| --------------------------------------------------- | -------------------------------------- |
| `python node.py 5001 localhost:5002,localhost:5003` | Menjalankan Node 1                     |
| `python node.py 5002 localhost:5001,localhost:5003` | Menjalankan Node 2                     |
| `python node.py 5003 localhost:5001,localhost:5002` | Menjalankan Node 3                     |
| `python client.py vote ...`                         | Memasukkan suara                       |
| `python client.py chain ...`                        | Melihat blockchain                     |
| `python client.py tally ...`                        | Melihat rekapitulasi suara             |
| `python client.py resolve ...`                      | Sinkronisasi dengan Longest-Chain Rule |
| `python client.py palsu ...`                        | Menguji transaksi/suara palsu          |
| `docker compose up --build -d`                      | Menjalankan jaringan Docker            |
| `docker compose ps`                                 | Melihat status container               |
| `docker compose down`                               | Menghentikan jaringan Docker           |

---

# 📝 Catatan

* Jalankan seluruh node sebelum menggunakan `client.py`.
* Setiap node harus menggunakan **port yang berbeda**.
* Pastikan tidak ada aplikasi lain yang sedang menggunakan port `5001`, `5002`, atau `5003`.
* Untuk pengujian double voting, gunakan NIM yang sama dengan transaksi sebelumnya.
* Untuk pengujian validasi, gunakan NIM sesuai dengan kondisi yang ingin diuji.
* Docker Desktop harus aktif ketika menggunakan metode Docker Compose.

# 🌐 4. Pengujian Blockchain Voting Menggunakan 2 Laptop

Bagian ini digunakan untuk menguji sistem blockchain voting secara **terdistribusi menggunakan 2 laptop** yang terhubung melalui hotspot dalam satu jaringan lokal.

Pada skenario ini:

* **Laptop A (Teman)** bertindak sebagai Node 1 dan membagikan hotspot.
* **Laptop B (Kamu)** terhubung ke hotspot Laptop A dan bertindak sebagai Node 2.

### Topologi Jaringan

```text
┌──────────────────────────────┐
│       Laptop A (Teman)       │
│                              │
│  Hotspot                     │
│  IP: 192.168.137.1           │
│                              │
│  Node 1                      │
│  Port: 5001                  │
└──────────────┬───────────────┘
               │
               │ Hotspot / Wi-Fi
               │
┌──────────────▼───────────────┐
│        Laptop B (Kamu)       │
│                              │
│  IP: 192.168.137.161         │
│                              │
│  Node 2                      │
│  Port: 5002                  │
└──────────────────────────────┘
```

## 4.1 Persiapan Jaringan

Pastikan **Laptop B terhubung ke hotspot yang dibuat oleh Laptop A**.

Konfigurasi jaringan yang digunakan:

| Perangkat        | Peran            | IP Address        | Port   |
| ---------------- | ---------------- | ----------------- | ------ |
| Laptop A (Teman) | Node 1 / Hotspot | `192.168.137.1`   | `5001` |
| Laptop B (Kamu)  | Node 2 / Client  | `192.168.137.161` | `5002` |

### Mengecek IP Address

Pada masing-masing laptop, buka **PowerShell** atau **Command Prompt**, kemudian jalankan:

```powershell
ipconfig
```

Pada Laptop A, pastikan IPv4 Address adalah:

```text
192.168.137.1
```

Pada Laptop B, pastikan IPv4 Address adalah:

```text
192.168.137.161
```

> Jika alamat IP berubah setelah hotspot dibuat ulang, gunakan alamat IP terbaru yang ditampilkan oleh `ipconfig`.

---

# 4.2 Pengaturan Windows Firewall

Karena kedua laptop saling berkomunikasi melalui jaringan hotspot, Windows Firewall harus mengizinkan koneksi masuk ke port yang digunakan.

Port yang digunakan:

```text
Laptop A → TCP 5001
Laptop B → TCP 5002
```

### Opsi A — Menonaktifkan Firewall Sementara

Untuk pengujian praktikum, Windows Defender Firewall pada jaringan **Private** dapat dinonaktifkan sementara.

Setelah pengujian selesai, **aktifkan kembali Windows Defender Firewall**.

### Opsi B — Membuat Inbound Rule

Alternatif yang lebih aman adalah membuat **Inbound Rule** pada Windows Defender Firewall with Advanced Security untuk mengizinkan koneksi TCP pada port:

```text
5001
5002
```

---

# 4.3 Menjalankan Node pada Masing-Masing Laptop

## Laptop A — Node 1

Laptop A merupakan laptop teman yang membagikan hotspot.

IP Laptop A:

```text
192.168.137.1
```

Jalankan pada Laptop A:

```powershell
python node.py 5001 192.168.137.161:5002
```

Node 1 berjalan pada:

```text
192.168.137.1:5001
```

dan menggunakan Laptop B sebagai peer:

```text
192.168.137.161:5002
```

---

## Laptop B — Node 2

Laptop B merupakan laptop yang menerima koneksi hotspot.

IP Laptop B:

```text
192.168.137.161
```

Jalankan pada Laptop B:

```powershell
python node.py 5002 192.168.137.1:5001
```

Node 2 berjalan pada:

```text
192.168.137.161:5002
```

dan menggunakan Laptop A sebagai peer:

```text
192.168.137.1:5001
```

Setelah kedua perintah dijalankan, kedua laptop akan membentuk jaringan blockchain yang saling terhubung.

---

# 4.4 Skenario Pengujian Voting

## Skenario 1 — Laptop B Mengirim Suara ke Laptop A

Dari Laptop B, jalankan:

```powershell
python client.py vote 192.168.137.1:5001 "Paslon 1" "F55125001"
```

Alur transaksi:

```text
Laptop B
192.168.137.161:5002
        │
        │ Mengirim transaksi voting
        ▼
Laptop A
192.168.137.1:5001
        │
        │ Validasi + Mining
        ▼
     Block Baru
        │
        │ Broadcast
        ▼
Laptop B
192.168.137.161:5002
```

**Hasil yang diharapkan:** transaksi diterima, divalidasi, ditambang menjadi block, kemudian block disebarkan ke node lainnya.

---

## Skenario 2 — Laptop A Mengirim Suara ke Laptop B

Dari Laptop A, jalankan:

```powershell
python client.py vote 192.168.137.161:5002 "Paslon 2" "C10123045"
```

Pada skenario ini, transaksi dikirim dari Laptop A menuju Node 2 yang berjalan pada Laptop B.

**Hasil yang diharapkan:** transaksi diterima, divalidasi, ditambang menjadi block, kemudian hasilnya disebarkan ke Laptop A.

---

## Skenario 3 — Mengecek Rekapitulasi Suara

Dari Laptop B, jalankan:

```powershell
python client.py tally 192.168.137.1:5001
```

Perintah tersebut meminta hasil tally dari Node 1 pada Laptop A.

Hasil akan menampilkan jumlah suara yang tercatat untuk masing-masing pasangan calon.

---

## Skenario 4 — Menguji Double Voting Antar-Laptop

Gunakan kembali NIM yang sebelumnya sudah melakukan voting.

Contoh:

```powershell
python client.py vote 192.168.137.1:5001 "Paslon 2" "F55125001"
```

Karena `F55125001` sebelumnya telah memberikan suara, transaksi tersebut seharusnya:

```text
DITOLAK
```

Pengujian ini menunjukkan bahwa sistem dapat mencegah **double voting** meskipun transaksi berasal dari laptop yang berbeda.

---

# 4.5 Mengecek Isi Blockchain

Untuk melihat blockchain pada Laptop A:

```powershell
python client.py chain 192.168.137.1:5001
```

Untuk melihat blockchain pada Laptop B:

```powershell
python client.py chain 192.168.137.161:5002
```

Kedua node seharusnya memiliki data blockchain yang sama setelah proses sinkronisasi berhasil.

---

# 4.6 Pengujian Longest-Chain Rule

Jika terdapat perbedaan blockchain antara kedua node, jalankan proses resolve.

Dari Laptop A:

```powershell
python client.py resolve 192.168.137.1:5001
```

atau dari Laptop B:

```powershell
python client.py resolve 192.168.137.161:5002
```

Proses ini menggunakan **Longest-Chain Rule** untuk memilih rantai blockchain yang valid dengan panjang paling besar.

---

# 4.7 Catatan Penting

* Laptop A menggunakan IP `192.168.137.1`.
* Laptop B menggunakan IP `192.168.137.161`.
* Laptop A bertindak sebagai hotspot dan Node 1.
* Laptop B menerima hotspot dan bertindak sebagai Node 2.
* Kedua laptop harus tetap terhubung selama pengujian.
* Pastikan port `5001` dan `5002` tidak digunakan aplikasi lain.
* Pastikan Windows Firewall mengizinkan koneksi pada port yang digunakan.
* Jalankan `node.py` terlebih dahulu sebelum menjalankan `client.py`.
* Jika IP berubah setelah hotspot dimatikan/dinyalakan kembali, cek kembali menggunakan `ipconfig`.
* Setelah selesai pengujian, aktifkan kembali Windows Defender Firewall jika sebelumnya dinonaktifkan.
