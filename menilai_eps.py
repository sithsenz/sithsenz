'''
Sambung ke file ini selepas menyimpan_laman_htm.py .
Sepertimana file menyimpan_laman_htm.py, file ini perlu dikemaskini setiap 3 bulan.
'''

import pandas as pd
import time

from bs4 import BeautifulSoup
from glob import glob
from multiprocessing import Pool
from scipy.stats import linregress, t


class Data:

    def __init__(self, x, y, h):
        g = linregress(x, y)
        self.x = x  # data tahun
        self.y = y  # data eps ataupun dps
        self.h = h  # data harga
        self.cerun = g.slope

        ts = abs(t.ppf(0.05/2, len(x)-2))
        std_error = g.stderr * ts
        self.min = self.cerun - std_error
        self.max = self.cerun + std_error

        if self.min > 0:
            self.tren = "meningkat"
            self.markah_tren = 2
        elif self.max < 0:
            self.tren = "menurun"
            self.markah_tren = 0
        else:
            self.tren = "mendatar"
            self.markah_tren = 1

        self.mid = self.y.median()
        self.pulangan = self.mid / self.h
        if self.pulangan < 5:
            self.markah_pulangan = 0
        elif self.pulangan <= 10:
            self.markah_pulangan = 1
        else:
            self.markah_pulangan = 2

        # julat markah = [0, 1, 2, 4]
        self.markah = self.markah_tren * self.markah_pulangan


def dapatkan_nama_saham(sup) -> tuple:
    _tajuk_saham = sup.find("title")
    _tajuk_saham = _tajuk_saham.text.strip()
    nama: str = _tajuk_saham.split(":")[0]
    _kod = _tajuk_saham.split("(")[-1]
    kod: str = _kod.split(")")[0]

    return nama, kod


def dapatkan_harga_semasa_saham(sup) -> float:
    _harga = sup.find(attrs={"id": "price"})
    harga: float = float(_harga.text.strip())

    return harga


def dapatkan_data_eps_dps(sup) -> pd.DataFrame:
    data: pd.DataFrame = pd.DataFrame(columns=["tahun", "eps", "dps"])

    _jadual = sup.find("table", attrs={"class": "financial_reports table table-hover table-sm table-theme"})

    for baris in _jadual.tbody.find_all("tr"):
        lajur = baris.find_all("td")
        if len(lajur) > 1:
            fy = lajur[7].text.strip()[-4:]
            eps = lajur[0].text.strip()
            dps = lajur[1].text.strip()
            data.loc[len(data)] = (fy, eps, dps)
    
    data = data.astype({"tahun": int, "eps": float, "dps": float})

    data.drop(axis="index", index=data[data["tahun"] >= tahun_ini].index, inplace=True)
    data.drop(axis="index", index=data[data["tahun"] < (tahun_ini - 10)].index, inplace=True)
    data = data.groupby(["tahun"], as_index=False).sum()

    return data


def analisis(laman: str) -> None:
    with open(laman, mode="r", encoding="utf-8") as file:
        kandungan_laman = file.read()
    
    sup = BeautifulSoup(kandungan_laman, "html.parser")

    _nama_saham, _kod_saham = dapatkan_nama_saham(sup)
    nama_saham: str = _nama_saham
    kod_saham: str = _kod_saham

    try:
        harga_semasa: float = dapatkan_harga_semasa_saham(sup)

        data: pd.DataFrame = dapatkan_data_eps_dps(sup)

        data_tahun = data["tahun"]
        data_eps = data["eps"]
        data_dps = data["dps"]

        if len(data) >= 10:
            stats_eps: Data = Data(data_tahun, data_eps, harga_semasa)
            stats_dps: Data = Data(data_tahun, data_dps, harga_semasa)
            
            markah: int = stats_eps.markah * stats_dps.markah

            penilaian: str = "Lulus" if markah > 0 else "Gagal"

            
            data_penilaian: tuple = (
                nama_saham,
                kod_saham,
                harga_semasa,
                stats_eps.mid,
                stats_eps.cerun,
                stats_eps.pulangan,
                stats_dps.mid,
                stats_dps.cerun,
                stats_dps.pulangan,
                markah,
                penilaian
            )
        else:
            data_penilaian: tuple = (
                nama_saham,
                kod_saham,
                None, None, None, None, None, None, None, None,
                "Kurang data"
            )
    except Exception as e:
        data_penilaian: tuple = (
            nama_saham,
            kod_saham,
            None, None, None, None, None, None, None, None,
            "Bermasalah"
        )

    return data_penilaian


if __name__ == "__main__":

    print()
    tahun_ini = int(input("  Tahun ini = "))

    senarai_laman = glob("laman_saham/*.htm")

    bil_saham: int = len(senarai_laman)

    senarai_lajur: list = [
        "Saham",
        "Kod",
        "Harga",
        "Median EPS",
        "Kecerunan EPS",
        "Pulangan EPS (%)",
        "Median DPS",
        "Kecerunan DPS",
        "Pulangan DPS (%)",
        "Markah",
        "Penilaian"
    ]

    masa_mula: time.time = time.time()
    str_masa_mula: str = time.strftime("%H:%M:%S", time.localtime(masa_mula))
    print()
    print(f'  {str_masa_mula} Mula membuat penilaian...')

    with Pool() as p:
        keputusan_analisis: list = p.map(analisis, senarai_laman)

        bilangan: int = 0
        
        for b in keputusan_analisis:
            bilangan += 1
            print(f'  {bilangan} per {bil_saham} = {bilangan/bil_saham:.2%}', end="\r")

    keputusan_penilaian: pd.DataFrame = pd.DataFrame(keputusan_analisis, columns=senarai_lajur)

    data_saham_lulus: pd.DataFrame = keputusan_penilaian[keputusan_penilaian["Penilaian"] == "Lulus"]
    data_saham_gagal: pd.DataFrame = keputusan_penilaian[keputusan_penilaian["Penilaian"] == "Gagal"]
    data_saham_kurang: pd.DataFrame = keputusan_penilaian[keputusan_penilaian["Penilaian"] == "Kurang data"]
    data_saham_bermasalah: pd.DataFrame = keputusan_penilaian[keputusan_penilaian["Penilaian"] == "Bermasalah"]

    saham_lulus: dict = dict(zip(data_saham_lulus["Saham"], data_saham_lulus["Kod"]))

    bil_saham_dianalisa: int = len(keputusan_penilaian)
    bil_saham_lulus: int = len(data_saham_lulus)
    bil_saham_gagal: int = len(data_saham_gagal)
    bil_saham_kurang_data: int = len(data_saham_kurang)
    bil_saham_bermasalah: int = len(data_saham_bermasalah)

    masa_tamat: time.time = time.time()
    str_masa_tamat: str = time.strftime("%H:%M:%S", time.localtime(masa_tamat))
    tempoh_masa: float = masa_tamat - masa_mula
    str_tempoh: str = f'{tempoh_masa//60:.0f}:{tempoh_masa%60:.0f}'


    print(f'''
  Laporan Penilaian Saham Berdasarkan Data EPS dan DPS
  Bil Laman = {bil_saham : >20}
  Bil Saham = {bil_saham_dianalisa : >20}
  Bil Saham Lulus = {bil_saham_lulus : >14}
  Bil Saham Gagal = {bil_saham_gagal : >14}
  Bil Kurang Data = {bil_saham_kurang_data : >14}
  Bil Laman Bermasalah = {bil_saham_bermasalah : >9}

  -----Saham Lulus-----

  {saham_lulus}

  Salin senarai saham yang lulus di atas ke dalam file melatih_mesin_opt_cv.py

  {str_masa_tamat}-----Tamat-----{str_tempoh}-----
''')