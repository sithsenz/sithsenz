'''
Mula dari file ini.
Kod dalam file ini perlu dilaksanakan setiap 3 bulan, pada hari Sabtu antara 8-14hb.
Kod ini akan memuatturun semua laman saham dalam klsescreener.
Data daripada laman saham ini akan diekstrak dan digunakan dalam file seterusnya.
'''


import os


from glob import glob


from modulam import pencatit_masa
from pelombongan import pelombong


if __name__ == "__main__":
    with pencatit_masa.mencatit_masa():
# hapuskan semula laman.html yang lama dalam folder laman_saham
        semua_laman_htm_lama: list = glob("laman_saham/*.htm")    
        for h in semua_laman_htm_lama: os.remove(h)

# laman screener disimpan sebagai Screener.html
        laman_screener: str = "screener_htm/Screener.html"

# dapatkan set semua url.
        semua_url: set = pelombong.dapatkan_semua_url(laman_screener)
        jumlah_url: int = len(semua_url)

# simpan semua laman.
        for url in semua_url: pelombong.simpan_laman(url)

        semua_laman_baharu: list = glob("laman_saham/*.htm")
        jumlah_laman_baharu: int = len(semua_laman_baharu)
        bil_laman_stok_bermasalah: int = jumlah_url - jumlah_laman_baharu

    print(f'''
Terdapat {bil_laman_stok_bermasalah} laman stok bermasalah.
Semua {jumlah_laman_baharu} / {jumlah_url} laman stok selesai disimpan.
Sila teruskan ke file menilai_eps.py .
    ''')
