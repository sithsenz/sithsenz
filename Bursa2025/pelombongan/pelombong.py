import pandas as pd


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def dapatkan_semua_url(laman_screener: str) -> set:
    '''
    Mendapatkan semua URL yang sepadan daripada file laman_screener.html .

    Fungsi ini membaca kandungan file laman_screener.html yang diberikan,
    mencari semua tag 'a', menapis URL yang mengandungi rentetan tertentu,
    sepertimana dalam sbhgn_href dan mengembalikan set URL unik.

    Args:
        laman_screener (str): Alamat file laman_screener.html .

    Returns:
        set: Set URL unik yang sepadan dengan kriteria penapisan.

    Contoh:
        Jika file 'screener.html' mengandungi pautan seperti:
        <a href="https://www.klsescreener.com/v2/stocks/view/ABC">ABC</a>
        <a href="https://www.example.com/page">Page</a>
        <a href="https://www.klsescreener.com/v2/stocks/view/XYZ">XYZ</a>

        maka, memanggil dapatkan_semua_url('screener.html') akan mengembalikan:
        {'https://www.klsescreener.com/v2/stocks/view/ABC',
        'https://www.klsescreener.com/v2/stocks/view/XYZ'}
    '''
    with open(laman_screener, "r") as laman:
        kandungan_laman = laman.read()
    
    sup = BeautifulSoup(kandungan_laman, "html.parser")

# dapatkan semua url daripada semua tag a.
    semua_a: list = sup.find_all("a")
    semua_href: list = [str(l.get("href")) for l in semua_a]

# simpan hanya url yang sepadan sahaja.
    sbhgn_href: str = "https://www.klsescreener.com/v2/stocks/view/"
    semua_url: list = [h for h in semua_href if sbhgn_href in h]    
    semua_url_yang_unik: set = set(semua_url)

    return semua_url_yang_unik


def simpan_laman(indeks, url, jumlah_url) -> None:
    '''
    Menyimpan sumber halaman web dari URL yang diberikan ke dalam fail HTML.

    Fungsi ini mengambil URL, memuatkannya menggunakan pemandu web (driver),
    dan menyimpan sumber halaman yang dimuatkan ke dalam fail HTML dengan nama
    yang berdasarkan nombor stok yang diekstrak dari URL.

    Args:
        indeks (int): Indeks URL semasa dalam senarai URL yang diproses.
        url (str): URL halaman web yang akan disimpan.
        n (int): Jumlah keseluruhan URL yang akan diproses.

    Returns:
        None: Fungsi ini tidak mengembalikan nilai.

    Contoh:
        Jika url = "https://www.klsescreener.com/v2/stocks/view/1234/ABC",
        maka fail yang disimpan akan bernama "1234.htm" di dalam folder "laman_saham".

    Catatan:
        Fungsi ini juga mencetak kemajuan pemprosesan ke konsol.
    '''
    nombor_stok: str = url.split("view/")[1].split("/")[0]
    
    servis = Service(ChromeDriverManager().install())
    pemandu_chrome = webdriver.Chrome(service=servis)

    pemandu_chrome.get(url)

    nama_file_laman: str = f'laman_saham/{nombor_stok}.htm'

    with open(nama_file_laman, "w") as halaman:
        halaman.write(pemandu_chrome.page_source)
    
    print(f'   {indeks+1} / {jumlah_url} = {(indeks+1) / jumlah_url:.2%}', end="\r")


def dapatkan_nama_saham(sup: BeautifulSoup) -> tuple:
    '''
    Mengekstrak nama saham dan kod saham daripada objek BeautifulSoup.

    Fungsi ini mengambil objek BeautifulSoup yang mewakili laman sesawang dan
    mengambil tajuk halaman untuk mengekstrak nama saham dan kod saham.
    Tajuk halaman dijangka dalam format "Nama Saham: (Kod Saham)".

    Args:
        sup (BeautifulSoup): Objek BeautifulSoup yang mengandungi kandungan laman sesawang.

    Returns:
        tuple: Tuple yang mengandungi nama saham (str) dan kod saham (str).

    Contoh:
        Jika tajuk halaman ialah "ABC Berhad: (1234)", maka fungsi ini akan mengembalikan
        ("ABC Berhad", "1234").
    '''
    _tajuk: str = sup.find("title")
    _tajuk = _tajuk.text.strip()
    nama: str = _tajuk.split(":")[0]
    _kod: str = _tajuk.split("(")[-1]
    kod: str = _kod.split(")")[0]

    return nama, kod


def dapatkan_harga(sup: BeautifulSoup) -> float:
    '''
    Mengekstrak harga saham daripada objek BeautifulSoup.

    Fungsi ini mencari elemen HTML dengan ID "price" dalam objek BeautifulSoup
    dan mengembalikan harga saham sebagai nilai float.

    Args:
        sup (BeautifulSoup): Objek BeautifulSoup yang mengandungi kandungan laman sesawang.

    Returns:
        float: Harga saham yang diekstrak.

    Contoh:
        Jika elemen dengan ID "price" mengandungi teks "12.34", maka fungsi ini akan
        mengembalikan 12.34.
    '''
    _harga: str = sup.find(attrs={"id": "price"})
    harga: float = float(_harga.text.strip())

    return harga


def dapatkan_data_eps_dps(sup: BeautifulSoup) -> list:
    df_data: pd.DataFrame = pd.DataFrame(columns=["fy", "eps", "dps"])

    _jadual = sup.find("table", attrs={"class": "financial_reports table table-hover table-sm table-theme"})

    for baris in _jadual.tbody.find_all("tr"):
        lajur= baris.find_all("td")

        if len(lajur) > 1:
            f = eval(lajur[7].text.strip()[-4:])
            e = eval(lajur[0].text.strip())
            d = eval(lajur[1].text.strip())

            df_data.loc[len(df_data)] = (f, e, d)
    
    data = df_data.groupby(["fy"], as_index=False).sum()
    
    return data