# client.py -- Alat bantu perintah voting UNTAD
import json
import sys
import urllib.error
import urllib.request

PASLON_VALID = ["Paslon 1", "Paslon 2"]

def panggil(url, data=None):
    if data is None:
        permintaan = urllib.request.Request(url)
    else:
        permintaan = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
    with urllib.request.urlopen(permintaan, timeout=30) as balasan:
        return json.loads(balasan.read().decode("utf-8"))

def ringkas(chain):
    for block in chain:
        induk = block.get("parent_hash")
        induk = induk[:12] + "..." if induk else "None"
        v_data = block.get("data") or block.get("vote_data") or {"kandidat": block.get("history", "-"), "voter_id": "-"}
        
        if isinstance(v_data, dict):
            kandidat = v_data.get("kandidat", "-")
            voter = v_data.get("voter_id", "-")
        else:
            kandidat = str(v_data)
            voter = "-"
            
        detail = f"Kandidat: {kandidat} | Voter NIM: {voter}"
        print(f"  Block {block['id']} | nonce: {str(block['nonce']).ljust(8)} | parent_hash: {induk} | {detail}")

if __name__ == "__main__":
    perintah = sys.argv[1]
    alamat = sys.argv[2]

    if perintah == "vote":
        kandidat = sys.argv[3] if len(sys.argv) > 3 else "Paslon 1"
        voter = sys.argv[4].upper().strip() if len(sys.argv) > 4 else "F55125001"

        if kandidat not in PASLON_VALID:
            print(f"Pilihan Gagal! '{kandidat}' tidak terdaftar. Pilihan resmi: {', '.join(PASLON_VALID)}")
            sys.exit(1)

        try:
            hasil = panggil(f"http://{alamat}/mine", {"kandidat": kandidat, "voter_id": voter})
            print(f"{hasil['pesan']}: Block {hasil['block']['id']}")
        except urllib.error.HTTPError as e:
            err_msg = json.loads(e.read().decode("utf-8"))
            print(f"Gagal memilih: {err_msg.get('error')}")

    elif perintah == "chain":
        hasil = panggil(f"http://{alamat}/chain")
        print(f"Panjang rantai suara di {alamat}: {hasil['panjang']} block")
        ringkas(hasil["chain"])

    elif perintah == "tally":
        hasil = panggil(f"http://{alamat}/tally")
        print(f"Total Suara Masuk: {hasil['total_suara']}")
        print("Hasil Rekapitulasi Suara:")
        for k, v in hasil["rekap_suara"].items():
            print(f"  - {k}: {v} suara")

    elif perintah == "resolve":
        hasil = panggil(f"http://{alamat}/resolve")
        if hasil["rantai_diganti"]:
            print(f"Rantai diganti. Panjang sekarang: {hasil['panjang']} block")
        else:
            print(f"Rantai tidak berubah. Panjang: {hasil['panjang']} block")

    elif perintah == "add_peer":
        peer_baru = sys.argv[3]
        hasil = panggil(f"http://{alamat}/peers", {"peer": peer_baru})
        print(f"{hasil['pesan']}")

    elif perintah == "palsu":
        terakhir = panggil(f"http://{alamat}/chain")["chain"][-1]
        block_palsu = {
            "id": terakhir["id"] + 1,
            "data": {"kandidat": "Paslon 1", "voter_id": "F55125999"},
            "parent_id": terakhir["id"],
            "parent_hash": "0" * 64,
            "nonce": 1,
        }
        try:
            panggil(f"http://{alamat}/block", block_palsu)
            print("Block palsu DITERIMA -- validasi node bermasalah.")
        except urllib.error.HTTPError as e:
            print(f"Suara palsu DITOLAK oleh node. Status HTTP: {e.code}")

    else:
        print("Perintah: vote | chain | tally | resolve | add_peer | palsu")