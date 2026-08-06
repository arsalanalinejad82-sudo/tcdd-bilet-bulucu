from .api import post_request
from .mail import send_email
from .util import load_stations, format_date
import config
import datetime

stations = load_stations()

sefer_url = "https://api-yebsp.tcddtasimacilik.gov.tr/sefer/seferSorgula"
vagon_url = "https://api-yebsp.tcddtasimacilik.gov.tr/vagon/vagonHaritasindanYerSecimi"


def fetch_and_filter_journeys():
    for binis_istasyon_adi, inis_istasyon_adi in config.routes:
        binis_istasyon_id = stations.get(binis_istasyon_adi)
        inis_istasyon_id = stations.get(inis_istasyon_adi)

        for date in config.dates:
            formatted_date = format_date(date)

            body = {
                "kanalKodu": 3,
                "dil": 0,
                "seferSorgulamaKriterWSDVO": {
                    "satisKanali": 3,
                    "binisIstasyonu": binis_istasyon_adi,
                    "inisIstasyonu": inis_istasyon_adi,
                    "binisIstasyonId": binis_istasyon_id,
                    "inisIstasyonId": inis_istasyon_id,
                    "binisIstasyonu_isHaritaGosterimi": False,
                    "inisIstasyonu_isHaritaGosterimi": False,
                    "seyahatTuru": 1,
                    "gidisTarih": f"{formatted_date} 00:00:00 AM",
                    "bolgeselGelsin": False,
                    "islemTipi": 0,
                    "yolcuSayisi": 1,
                    "aktarmalarGelsin": True,
                }
            }

            print(f"Checking {binis_istasyon_adi} -> {inis_istasyon_adi} for date: {formatted_date}")
            response = post_request(sefer_url, body)
            data = response.json()

            if data['cevapBilgileri']['cevapKodu'] == '000':
                for sefer in data['seferSorgulamaSonucList']:
                    sefer_time = datetime.datetime.strptime(sefer['binisTarih'], "%b %d, %Y %I:%M:%S %p")
                    end_time = datetime.datetime.strptime(f"{date} {config.end_hour}", "%Y-%m-%d %H:%M")
                    if sefer_time.time() <= end_time.time():
                        check_sefer(sefer, binis_istasyon_adi, inis_istasyon_adi)


def check_sefer(sefer, binis_istasyon_adi, inis_istasyon_adi):
    print(f"Checking for time: {sefer['binisTarih']}")
    for vagon in sefer['vagonTipleriBosYerUcret']:
        for vagon_detail in vagon['vagonListesi']:
            vagon_sira_no = vagon_detail['vagonSiraNo']
            print(f"Checking for vagon: {vagon_sira_no}")
            check_specific_seats(
                sefer['seferId'], vagon_sira_no, sefer['trenAdi'], sefer['binisTarih'],
                binis_istasyon_adi, inis_istasyon_adi
            )


def check_specific_seats(seferId, vagon_sira_no, tren_adi, binis_tarih, binis_istasyon_adi, inis_istasyon_adi):
    body = {
        "kanalKodu": "3",
        "dil": 0,
        "seferBaslikId": seferId,
        "vagonSiraNo": vagon_sira_no,
        "binisIst": binis_istasyon_adi,
        "InisIst": inis_istasyon_adi
    }

    response = post_request(vagon_url, body)
    data = response.json()

    if data['cevapBilgileri']['cevapKodu'] == '000':
        for seat in data['vagonHaritasiIcerikDVO']['koltukDurumlari']:
            if seat['durum'] == 0:
                if not seat['koltukNo'].endswith('h'):
                    print(f"Available seat: {seat['koltukNo']} in Wagon {vagon_sira_no}")
                    send_email(tren_adi, binis_tarih, vagon_sira_no, seat['koltukNo'])
                else:
                    print(f"Available handicapped seat: {seat['koltukNo']} in Wagon {vagon_sira_no}")
