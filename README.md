Berikut adalah teks lengkap untuk berkas `README.md` yang siap Anda salin dan gunakan di direktori proyek `praktikum1b/`:

```markdown
# 🗳️ Voting Blockchain Terdistribusi (Praktikum 2)

Proyek ini merupakan implementasi *blockchain* terdistribusi berbasis Python untuk jaringan pemungutan suara (*voting system*) independen tanpa bergantung pada *framework* pihak ketiga maupun koordinator pusat[cite: 3]. Seluruh komunikasi antar-node dikembangkan menggunakan pustaka standar Python (`http.server` & `urllib.request`) guna mensimulasikan mekanisme konsensus terdistribusi, penyebaran suara (*broadcast*), *longest-chain rule*, dan pertahanan *Proof of Work*[cite: 3].

---

## 📁 Struktur Direktori

```text
praktikum1b/
├── node.py            # Program utama node blockchain voting (HTTP server & konsensus)
├── client.py          # Alat bantu CLI untuk interaksi voting, penambangan, & resolve
├── Dockerfile         # Konfigurasi containerization untuk node
└── docker-compose.yml # Orchestration untuk menjalankan jaringan multi-node (3 container)

```

---

## 🚀 Cara Penggunaan

### 1. Menjalankan Node di Terminal Lokal (Bagian 1)

Buka 3 jendela terminal berbeda di dalam direktori `praktikum1b/`:

* **Terminal 1 (Node 1 - Port 5001):**
```bash
python node.py 5001 localhost:5002,localhost:5003

```


* **Terminal 2 (Node 2 - Port 5002):**
```bash
python node.py 5002 localhost:5001,localhost:5003

```


* **Terminal 3 (Node 3 - Port 5003):**
```bash
python node.py 5003 localhost:5001,localhost:5002

```



---

### 2. Menggunakan Client CLI (`client.py`)

Gunakan terminal terpisah untuk mengeksekusi perintah voting:

* **Memasukkan Suara (Voting / Mining):**
```bash
python client.py vote localhost:5001 "Paslon 1" "Voter_001"
python client.py vote localhost:5001 "Paslon 2" "Voter_002"

```


* **Melihat Isi Rantai Blockchain:**
```bash
python client.py chain localhost:5002

```


* **Melihat Rekapitulasi Suara (Tallying):**
```bash
python client.py tally localhost:5002

```


* **Jalankan Longest-Chain Rule (Resolve):**
```bash
python client.py resolve localhost:5003

```


* **Uji Kirim Suara Palsu (Simulasi Serangan):**
```bash
python client.py palsu localhost:5001

```



---

### 3. Menjalankan Menggunakan Docker (Bagian 2)

Pastikan aplikasi **Docker Desktop** sudah aktif, lalu jalankan perintah berikut:

```bash
# Jalankan seluruh jaringan container di latar belakang
docker compose up --build -d

# Cek status container yang sedang berjalan
docker compose ps

# Kirim perintah voting lewat port terpetakan
python client.py vote localhost:5001 "Paslon 1" "Voter_003"
python client.py tally localhost:5002

# Hentikan seluruh jaringan container
docker compose down

```

---

## 🧪 Hasil Eksperimen Konsensus

### 7.1 Data Domain Kelompok (Voting System)

Pengujian data domain menerapkan pencatatan transaksi pemungutan suara pada atribut `vote_data`. Setiap *block* menyimpan nama kandidat dan ID pemilih (*voter_id*) yang terikat secara matematis ke dalam perhitungan *hash* SHA-256.

| Node | Block | Data Voting (`vote_data`) | Nonce | Hash Akhir |
| --- | --- | --- | --- | --- |
| **5001** | 2 | `{kandidat: "Paslon 1", voter_id: "Voter_001"}` | `63.125` | `00002552648082e6455b...` |
| **5001** | 3 | `{kandidat: "Paslon 2", voter_id: "Voter_002"}` | `137.901` | `00001e554d783a5cd688...` |

**Analisis:**
Fungsi `compute_hash()` melakukan serialisasi terhadap isi `vote_data`. Mengubah satu karakter saja pada nama kandidat atau *voter_id* akan mengakibatkan perubahan total nilai *hash* (*avalanche effect*) dan membatalkan keabsahan *Proof of Work*. Hal ini menjamin bahwa suara yang sudah tercatat tidak dapat dimanipulasi.

---

### 7.2 Fork dan Aturan Rantai Terpanjang (*Longest-Chain Rule*)

Simulasi *fork* dilakukan dengan menambang secara independen pada *node* yang terpisah:

1. **Node 1 (Port 5001)** menambang 2 *block* suara, sehingga panjang rantainya menjadi **3 block**.


2. **Node 2 (Port 5002)** menambang 3 *block* suara, sehingga panjang rantainya menjadi **4 block**.


3. Kedua *node* dihubungkan via `POST /peers`, lalu fungsi `resolve_conflicts()` dijalankan.



| Node | Panjang Rantai Awal | Status Penggabungan | Rantai Akhir (Bertahan) | Block yang Dibuang (*Orphaned*) |
| --- | --- | --- | --- | --- |
| **5001** | 3 Block | Rantai Diganti (*Adopted*) | 4 Block | 2 Block (Milik Node 1) |
| **5002** | 4 Block | Rantai Utama (Dipertahankan) | 4 Block | Tidak Ada |

**Analisis:**
Node 1 mendeteksi bahwa rantai milik Node 2 lebih panjang (4 *block* vs 3 *block*) dan seluruh *block*-nya sah. Node 1 secara otomatis membuang rantainya dan mengadopsi rantai terpanjang dari Node 2. Dua *block* suara milik Node 1 yang terbuang dinamakan ***orphaned blocks*** karena gugur dari konsensus utama jaringan.

---

### 7.3 Pengaruh *Difficulty* terhadap Waktu Penambangan

Pengujian dilakukan dengan mengubah konstanta `DIFFICULTY` pada `node.py` dari `"0000"` menjadi `"00000"`:

| Nilai `DIFFICULTY` | Syarat Awalan Hash | Rerata Iterasi *Nonce* | Rerata Waktu Penambangan |
| --- | --- | --- | --- |
| **`"0000"`** (4 nol) | `0000...` | ~60.000 – 150.000 iterasi | **< 1 detik** (Instan) |
| **`"00000"`** (5 nol) | `00000...` | ~1.000.000 – 3.500.000 iterasi | **12 – 25 detik** |

**Analisis Keamanan Rantai:**
Meningkatkan *difficulty* menambah beban komputasi CPU secara eksponensial. Tingkat kesulitan yang tinggi melindungi *blockchain* dari upaya penulisan ulang riwayat voting (*history rewriting*): peretas harus mengeluarkan daya komputasi yang jauh lebih besar daripada gabungan seluruh *node* jujur di jaringan untuk dapat mengubah suara di masa lalu.

```

```