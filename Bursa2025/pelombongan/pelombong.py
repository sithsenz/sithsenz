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


def simpan_laman(url) -> None:
    '''
    Menyimpan sumber halaman web dari URL yang diberikan ke dalam fail HTML.

    Fungsi ini mengambil URL, memuatkannya menggunakan pemandu web (driver),
    dan menyimpan sumber halaman yang dimuatkan ke dalam fail HTML dengan nama
    yang berdasarkan nombor stok yang diekstrak dari URL. Jika berlaku ralat
    semasa memuatkan atau menyimpan halaman, URL yang bermasalah akan ditambahkan
    ke dalam senarai 'bermasalah'.

    Args:
        indeks (int): Indeks URL semasa dalam senarai URL yang diproses.
        url (str): URL halaman web yang akan disimpan.
        n (int): Jumlah keseluruhan URL yang akan diproses.
        bermasalah (list): Senarai untuk menyimpan URL yang bermasalah.
        pemandu: Objek pemandu web (driver) yang digunakan untuk memuatkan halaman web.

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