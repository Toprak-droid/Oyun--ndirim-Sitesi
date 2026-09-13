from flask import Flask, render_template, send_from_directory
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json
import time

app = Flask(__name__)

@app.route('/googlefd59a7711b881762.html')
def google_verify():
    return send_from_directory('static', 'googlefd59a7711b881762.html')

# API'yi her sayfa yenilemede tekrar çağırmamak için 5 dakika önbellek
veri_onbellek = {
    "zaman": 0,
    "oyunlar": []
}


def indirimleri_getir():
    simdi = time.time()

    if simdi - veri_onbellek["zaman"] < 300:
        return veri_onbellek["oyunlar"]

    oyunlar = []

    # CheapShark mağaza kodları:
    # 1 = Steam
    # 25 = Epic Games
    magaza_listesi = [
        ("1", "Steam"),
        ("25", "Epic Games")
    ]

    for magaza_kodu, magaza_adi in magaza_listesi:
        parametreler = urlencode({
            "storeID": magaza_kodu,
            "pageSize": 100,
            "page": 0
        })

        adres = f"https://www.cheapshark.com/api/1.0/deals?{parametreler}"

        try:
            istek = Request(
                adres,
                headers={
                    "User-Agent": "OyunIndirimSitesi/1.0"
                }
             )

            with urlopen(istek, timeout=15) as cevap:
                veriler = json.loads(cevap.read().decode("utf-8"))

            for oyun in veriler:
                oyunlar.append({
                    "ad": oyun.get("title", "İsimsiz oyun"),
                    "magaza": magaza_adi,
                    "eski_fiyat": f"${oyun.get('normalPrice', '0')}",
                    "yeni_fiyat": f"${oyun.get('salePrice', '0')}",
                    "indirim": f"%{float(oyun.get('savings', 0)):.0f} indirim",
                    "resim": oyun.get("thumb", ""),
                    "link": (
                        "https://www.cheapshark.com/redirect"
                        f"?dealID={oyun.get('dealID', '' )}"
                    )
                })

        except Exception as hata:
            print(f"{magaza_adi} verisi alınamadı: {hata}")

    # En yüksek indirim oranı üstte görünsün
    oyunlar.sort(
        key=lambda oyun: float(
            oyun["indirim"].replace("%", "").replace(" indirim", "")
        ),
        reverse=True
    )

    veri_onbellek["zaman"] = simdi
    veri_onbellek["oyunlar"] = oyunlar

    return oyunlar


@app.route("/")
def ana_sayfa():
    oyunlar = indirimleri_getir()
    return render_template("index.html", oyunlar=oyunlar)


if __name__ == "__main__":
    app.run(debug=True)
