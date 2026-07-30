import requests
import config

def send_email(tren_adi, binis_tarih, vagon_no, seat_no):
    message = (
        f"🚄 Boş koltuk bulundu!\n\n"
        f"Tren: {tren_adi}\n"
        f"Tarih: {binis_tarih}\n"
        f"Vagon: {vagon_no}\n"
        f"Koltuk: {seat_no}"
    )

    url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": config.telegram_chat_id,
        "text": message
    }
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        print(f"Telegram bildirimi gönderildi: Koltuk {seat_no}, Vagon {vagon_no}, {tren_adi}")
    else:
        print(f"Telegram bildirimi gönderilemedi: {response.text}")
