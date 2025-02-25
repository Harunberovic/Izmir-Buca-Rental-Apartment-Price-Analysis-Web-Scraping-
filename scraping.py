import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Chrome WebDriver ayarları
chrome_options = Options()
chrome_options.add_argument("--headless")  # Arka planda çalıştırmak için
chrome_service = Service('C:/chromedriver/chromedriver.exe')  # Chromedriver'ın doğru yolu
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# İlanların bulunduğu sayfayı aç
base_url = "https://www.hepsiemlak.com/buca-kiralik"
driver.get(base_url)

# Sayfanın tamamen yüklenmesi için bekle
time.sleep(5)

# İlan detayları listeleri
ilan_basliklari = []
oda_sayisi = []
metrekare = []
bina_yasi = []
kat = []
fiyatlar = []  # Fiyat bilgisi için yeni liste
ilan_tarihleri = []  # İlan tarihleri için yeni liste
mahalleler = []  # Mahalle bilgisi için yeni liste
isinma_tipi = []  # Isınma tipi için yeni liste

def get_ilan_verileri():
    # Sayfanın HTML kodunu al
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    ilanlar = soup.find_all('div', class_='list-view-line')

    for ilan in ilanlar:
        # Başlık
        baslik = ilan.find('h3').text.strip() if ilan.find('h3') else 'N/A'
        ilan_basliklari.append(baslik)

        # Oda Sayısı
        oda = ilan.find('span', class_='celly houseRoomCount').text.strip() if ilan.find('span', class_='celly houseRoomCount') else 'N/A'
        oda_sayisi.append(oda)

        # Metrekare
        m2 = ilan.find('span', class_='celly squareMeter list-view-size').text.strip() if ilan.find('span', class_='celly squareMeter list-view-size') else 'N/A'
        metrekare.append(m2)

        # Bina Yaşı
        yas = ilan.find('span', class_='celly buildingAge').text.strip() if ilan.find('span', class_='celly buildingAge') else 'N/A'
        bina_yasi.append(yas)

        # Kat
        kat_numarasi = ilan.find('span', class_='celly floortype').text.strip() if ilan.find('span', class_='celly floortype') else 'N/A'
        kat.append(kat_numarasi)

        # Fiyat
        fiyat = ilan.find('span', class_='list-view-price').text.strip() if ilan.find('span', class_='list-view-price') else 'N/A'
        fiyatlar.append(fiyat)

        # İlan Tarihi
        tarih = ilan.find('span', class_='list-view-date').text.strip() if ilan.find('span', class_='list-view-date') else 'N/A'
        ilan_tarihleri.append(tarih)

        # Mahalle bilgisi
        mahalle = ilan.find('div', class_='list-view-location')
        if mahalle:
            mahalle_text = mahalle.get_text(strip=True).replace('\n', '')
            mahalleler.append(mahalle_text)
        else:
            mahalleler.append('N/A')

        # Isınma Tipi
        # İlan detay sayfasındaki ısıtma tipini almak için gerekli kod
        try:
            # İlan detayına git
            detay_link = ilan.find('a')['href']
            driver.get(detay_link)
            time.sleep(3)  # Detay sayfasının yüklenmesi için bekle

            # Detay sayfasının HTML'ini al
            detay_soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Isınma tipini bul
            isinma = detay_soup.find('li', class_='spec-item', string=lambda x: 'Isınma Tipi' in x if x else False)
            if isinma and isinma.find('span'):
                isinma_tipi.append(isinma.find('span').text.strip())
            else:
                isinma_tipi.append('N/A')

            # Tarayıcıyı tekrar geri döndür
            driver.back()
            time.sleep(2)  # Geri dönerken sayfanın yüklenmesi için bekle
        except Exception as e:
            print("Isınma tipi alınırken bir hata oluştu:", e)
            isinma_tipi.append('N/A')

# Toplam veri sayısını belirle
target_data_count = 500
current_data_count = 0

# Sayfa döngüsü
for page in range(1, 30):  # 1. sayfadan 29. sayfaya kadar döngü
    if current_data_count >= target_data_count:
        break

    # Sayfanın URL'sini güncelle
    page_url = f"{base_url}?page={page}"
    driver.get(page_url)
    time.sleep(5)  # Sayfanın yüklenmesini bekle

    # İlan verilerini al
    get_ilan_verileri()

    # Toplam verileri kontrol et
    current_data_count = len(ilan_basliklari)

# Verileri DataFrame'e dönüştür
df = pd.DataFrame({
    'İlan Başlıkları': ilan_basliklari,
    'Oda Sayısı': oda_sayisi,
    'Metrekare': metrekare,
    'Bina Yaşı': bina_yasi,
    'Kat': kat,
    'Fiyat': fiyatlar,
    'İlan Tarihi': ilan_tarihleri,
    'Mahalle': mahalleler,  # Mahalle bilgisini ekledik
    'Isınma Tipi': isinma_tipi  # Isınma tipini ekledik
})

# DataFrame'deki veri sayısını kontrol et
if len(df) > target_data_count:
    df = df.head(target_data_count)  # İlk 500 veriyi al

# Excel dosyasına yaz
df.to_excel('ilan_verileri_son.xlsx', index=False)

# Tarayıcıyı kapat
driver.quit()

print("İlan verileri başarıyla Excel dosyasına kaydedildi.")
