import sys
sys.path.insert(0, 'py')
from pinjamlab.catalog_service import CatalogService

def main():
    svc = CatalogService()
    path = "sample-data/my-catalog.csv"

    print(f"Membaca dataset: {path} ...")
    accepted = svc.load(path)

    print(f"✅ Baris unik diterima (masuk ke Repository): {accepted}")
    print(f"⛔ Baris duplikat ditolak (O(1) Hash Collision): {svc.rejected}")
    print(f"📦 Total aset di dalam sistem saat ini: {len(svc)}\n")

    print("🔍 Uji Kategori Baru ('Networking'):")
    for item in svc.by_category("Networking"):
        print(f"   -> [{item.tag}] {item.model} (Kondisi: {item.condition})")

    print("\n🔍 Uji Fungsi Search O(n) (Query: 'thinkpad'):")
    for item in svc.search("thinkpad"):
        print(f"   -> [{item.tag}] {item.model}")

if __name__ == "__main__":
    main()