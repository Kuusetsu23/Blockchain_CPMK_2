# client.py -- Alat bantu perintah voting
import json
import sys
import urllib.error
import urllib.request

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
        induk = block["parent_hash"]
        induk = induk[:12] + "..." if induk else "None"
        v_data = block["vote_data"]
        detail = f"Kandidat: {v_data.get('kandidat')} | Voter: {v_data.get('voter_id')}"
        print(f"  Block {block['id']} | nonce: {str(block['nonce']).ljust(8)} | parent_hash: {induk} | {detail}")

if __name__ == "__main__":
    perintah = sys.argv[1]
    alamat = sys.argv[2]

    if perintah == "vote":
        kandidat = sys.argv[3] if len(sys.argv) > 3 else "Kandidat A"
        voter = sys.argv[4] if len(sys.argv) > 4 else "Voter123"
        hasil = panggil(f"http://{alamat}/mine", {"kandidat": kandidat, "voter_id": voter})
        print(f"{hasil['pesan']}: Block {hasil['block']['id']}")

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
            print(f"Rantai suara diganti. Panjang sekarang: {hasil['panjang']} block")
        else:
            print(f"Rantai suara tidak berubah. Panjang: {hasil['panjang']} block")

    elif perintah == "palsu":
        terakhir = panggil(f"http://{alamat}/chain")["chain"][-1]
        block_palsu = {
            "id": terakhir["id"] + 1,
            "vote_data": {"kandidat": "Kandidat Palsu", "voter_id": "Hacker"},
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
        print("Perintah: vote | chain | tally | resolve | palsu")