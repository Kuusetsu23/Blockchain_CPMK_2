
# 🗳️ Voting Blockchain Terdistribusi (Praktikum 2)

Proyek ini merupakan implementasi *blockchain* terdistribusi berbasis Python untuk jaringan pemungutan suara (*voting system*) independen tanpa bergantung pada *framework* pihak ketiga maupun koordinator pusat[cite: 3]. Seluruh komunikasi antar-node dikembangkan menggunakan pustaka standar Python (`http.server` & `urllib.request`) guna mensimulasikan mekanisme konsensus terdistribusi, penyebaran suara (*broadcast*), *longest-chain rule*, dan pertahanan *Proof of Work*[cite: 3].

---

## 📁 Struktur Direktori

text
praktikum1b/
├── node.py            # Program utama node blockchain voting (HTTP server & konsensus)
├── client.py          # Alat bantu CLI untuk interaksi voting, penambangan, & resolve
├── Dockerfile         # Konfigurasi containerization untuk node
└── docker-compose.yml # Orchestration untuk menjalankan jaringan multi-node (3 container)



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



```
