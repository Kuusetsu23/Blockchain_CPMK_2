# node.py -- Node Voting Blockchain Terdistribusi Universitas Tadulako
import hashlib
import json
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DIFFICULTY = "0000"
PORT = 0
PEERS = []
CHAIN = []

# --- Aturan & Konfigurasi Voting UNTAD ---
PASLON_VALID = ["Paslon 1", "Paslon 2"]
ANGKATAN_VALID = ["23", "24", "25"]  # Angkatan 2023 (Sem 7), 2024 (Sem 5), 2025 (Sem 3)
FAKULTAS_UNTAD = ["A", "B", "C", "D", "E", "F", "G", "K", "L", "N", "P"] 

def validasi_nim_untad(nim):
    """
    Format NIM UNTAD: [Kode Fakultas][3 Digit Prodi][2 Digit Tahun][3 Digit No Urut]
    Contoh: F55125001 -> Fakultas 'F', Angkatan '25'
    """
    nim = nim.upper().strip()
    if len(nim) < 8:
        return False, "Format NIM terlalu pendek!"
    
    kode_fakultas = nim[0]
    if kode_fakultas not in FAKULTAS_UNTAD:
        return False, f"Kode Fakultas '{kode_fakultas}' tidak terdaftar di UNTAD!"
    
    # Mengambil 2 digit angkatan dari NIM
    try:
        angkatan = nim[4:6] if len(nim) >= 9 else nim[1:3]
        if angkatan not in ANGKATAN_VALID:
            return False, f"Angkatan '20{angkatan}' tidak memenuhi syarat (Hanya Semester 3-7 / Angkatan 2023-2025)!"
    except Exception:
        return False, "Format NIM UNTAD tidak valid!"

    return True, "Valid"

def voter_sudah_memilih(chain, voter_id):
    """Mengecek apakah voter_id/NIM sudah pernah memilih di dalam rantai blockchain."""
    for block in chain[1:]:  # Lompati Genesis Block
        v_data = block.get("data") or block.get("vote_data") or {}
        if isinstance(v_data, dict) and v_data.get("voter_id") == voter_id:
            return True
    return False

# --- Logika Blockchain Voting ---

def new_block(id, data, parent_id=None, parent_hash=None):
    return {
        "id": id,
        "data": data,
        "parent_id": parent_id,
        "parent_hash": parent_hash,
        "nonce": None,
    }

def compute_hash(block):
    payload = json.dumps(block, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def mine_block(block, difficulty=DIFFICULTY, max_try=500000):
    for i in range(max_try):
        block["nonce"] = i
        hasil = compute_hash(block)
        if hasil.startswith(difficulty):
            return i, hasil
    block["nonce"] = None
    return None, None

def genesis_block():
    block = new_block(1, {"kandidat": "System", "voter_id": "Genesis Block"})
    block["nonce"] = 0
    return block

def is_chain_valid(chain, difficulty=DIFFICULTY):
    if not chain or chain[0]["parent_hash"] is not None:
        return False
    
    voters_seen = set()
    for i in range(1, len(chain)):
        induk = chain[i - 1]
        blok = chain[i]
        
        if blok["parent_id"] != induk["id"]:
            return False
        if blok["parent_hash"] != compute_hash(induk):
            return False
        if blok["nonce"] is None:
            return False
        if not compute_hash(blok).startswith(difficulty):
            return False
            
        # Validasi kecurangan double voting di dalam rantai
        v_data = blok.get("data") or blok.get("vote_data") or {}
        if isinstance(v_data, dict):
            voter = v_data.get("voter_id")
            if voter in voters_seen:
                return False
            voters_seen.add(voter)
            
    return True

# --- Komunikasi Antar Node ---

def kirim_json(url, isi):
    data = json.dumps(isi).encode("utf-8")
    permintaan = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(permintaan, timeout=5) as balasan:
        return json.loads(balasan.read().decode("utf-8"))

def ambil_json(url):
    with urllib.request.urlopen(url, timeout=5) as balasan:
        return json.loads(balasan.read().decode("utf-8"))

def broadcast_block(block):
    for peer in PEERS:
        try:
            kirim_json(f"http://{peer}/block", block)
            print(f" -> block {block['id']} dikirim ke {peer}")
        except Exception as e:
            print(f" !! gagal mengirim ke {peer} ({e})")

def resolve_conflicts():
    global CHAIN
    terpanjang = CHAIN
    for peer in PEERS:
        try:
            kandidat = ambil_json(f"http://{peer}/chain")["chain"]
            if len(kandidat) > len(terpanjang) and is_chain_valid(kandidat):
                terpanjang = kandidat
                print(f" -> rantai lebih panjang di {peer} ({len(kandidat)} block)")
        except Exception as e:
            print(f" !! gagal menghubungi {peer} ({e})")
    
    if terpanjang is not CHAIN:
        CHAIN = terpanjang
        return True
    return False

# --- Antarmuka HTTP Node ---

class NodeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _balas(self, kode, isi):
        badan = json.dumps(isi, indent=2).encode("utf-8")
        self.send_response(kode)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(badan)))
        self.end_headers()
        self.wfile.write(badan)

    def do_GET(self):
        if self.path == "/chain":
            self._balas(200, {"panjang": len(CHAIN), "chain": CHAIN})
        elif self.path == "/resolve":
            print(f"[{PORT}] menjalankan longest-chain rule")
            berubah = resolve_conflicts()
            self._balas(200, {"rantai_diganti": berubah, "panjang": len(CHAIN)})
        elif self.path == "/tally":
            rekap = {p: 0 for p in PASLON_VALID}
            for block in CHAIN[1:]:
                v_data = block.get("data") or block.get("vote_data") or {}
                kandidat = v_data.get("kandidat") if isinstance(v_data, dict) else None
                if kandidat in rekap:
                    rekap[kandidat] += 1
            self._balas(200, {"total_suara": len(CHAIN) - 1, "rekap_suara": rekap})
        else:
            self._balas(404, {"error": "endpoint tidak dikenal"})

    def do_POST(self):
        panjang = int(self.headers.get("Content-Length", 0))
        isi = json.loads(self.rfile.read(panjang) or b"{}")

        if self.path == "/mine":
            induk = CHAIN[-1]
            kandidat_input = isi.get("kandidat", "")
            voter_input = str(isi.get("voter_id", "")).upper().strip()
            
            # 1. Validasi Paslon Resmi
            if kandidat_input not in PASLON_VALID:
                print(f"[{PORT}] DITOLAK: Paslon '{kandidat_input}' tidak terdaftar!")
                self._balas(400, {
                    "error": f"Kandidat '{kandidat_input}' tidak valid. Pilihan resmi: {', '.join(PASLON_VALID)}"
                })
                return

            # 2. Validasi Format & Semester NIM UNTAD
            nim_valid, pesan_err = validasi_nim_untad(voter_input)
            if not nim_valid:
                print(f"[{PORT}] DITOLAK: NIM '{voter_input}' -> {pesan_err}")
                self._balas(400, {"error": f"NIM '{voter_input}' ditolak: {pesan_err}"})
                return

            # 3. Validasi Cegah Double Voting
            if voter_sudah_memilih(CHAIN, voter_input):
                print(f"[{PORT}] DITOLAK: NIM '{voter_input}' sudah pernah memilih!")
                self._balas(400, {"error": f"NIM '{voter_input}' sudah menggunakan hak pilihnya!"})
                return

            vote_data = {
                "kandidat": kandidat_input,
                "voter_id": voter_input
            }
            block = new_block(
                induk["id"] + 1,
                vote_data,
                parent_id=induk["id"],
                parent_hash=compute_hash(induk)
            )
            nonce, hasil = mine_block(block)
            if nonce is None:
                self._balas(500, {"error": "gagal menambang block"})
                return
            CHAIN.append(block)
            print(f"[{PORT}] block {block['id']} ditambang, nonce {nonce}, hash {hasil[:20]}...")
            broadcast_block(block)
            self._balas(201, {"pesan": "suara berhasil masuk ke blockchain", "block": block})

        elif self.path == "/block":
            block = isi
            induk = CHAIN[-1]
            v_data = block.get("data") or block.get("vote_data") or {}
            kandidat_block = v_data.get("kandidat") if isinstance(v_data, dict) else None
            voter_block = v_data.get("voter_id") if isinstance(v_data, dict) else None
            
            nim_valid, _ = validasi_nim_untad(str(voter_block))
            sah = (
                block.get("parent_id") == induk["id"]
                and block.get("parent_hash") == compute_hash(induk)
                and block.get("nonce") is not None
                and compute_hash(block).startswith(DIFFICULTY)
                and kandidat_block in PASLON_VALID
                and nim_valid
                and not voter_sudah_memilih(CHAIN, voter_block)
            )
            if sah:
                CHAIN.append(block)
                print(f"[{PORT}] block {block['id']} diterima dari peer")
                self._balas(200, {"pesan": "block diterima"})
            else:
                print(f"[{PORT}] block {block.get('id')} DITOLAK (tidak valid/double vote)")
                self._balas(409, {"pesan": "block ditolak"})

        elif self.path == "/peers":
            peer_baru = isi.get("peer")
            if peer_baru and peer_baru not in PEERS:
                PEERS.append(peer_baru)
                print(f"[{PORT}] peer baru ditambahkan: {peer_baru}")
                self._balas(200, {"pesan": f"peer {peer_baru} berhasil ditambahkan", "peers": PEERS})
            else:
                self._balas(400, {"error": "peer tidak valid atau sudah ada"})
        else:
            self._balas(404, {"error": "endpoint tidak dikenal"})

if __name__ == "__main__":
    PORT = int(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2]:
        PEERS = sys.argv[2].split(",")

    CHAIN.append(genesis_block())
    print(f"Node Voting UNTAD aktif di port {PORT}")
    print("Peers  : " + (", ".join(PEERS) if PEERS else "(belum ada)"))
    print(f"Genesis: {compute_hash(CHAIN[0])[:20]}...")

    ThreadingHTTPServer(("0.0.0.0", PORT), NodeHandler).serve_forever()