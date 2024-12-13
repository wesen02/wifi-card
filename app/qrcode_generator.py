import qrcode
import hashlib
import bcrypt
from database import hash_text

def qr_shop(shop_info):
    shop_name = shop_info['shop_name']
    wifi_name = shop_info['wifi_name']
    wifi_sec = shop_info['security_type']
    wifi_password = shop_info['wifi_password']
    shop_code = hash_text(shop_name + wifi_name)[:6]

    wifi = f"WIFI:S:{wifi_name};T:{wifi_sec};P:{wifi_password};"

    wifi_link = f"https://401f-121-122-34-137.ngrok-free.app/scan?qr={shop_code}"

    wifi_qr = qrcode.make(wifi)
    wifi_dir = f"./static/assets/wifi_qr/{shop_code}.png"

    qr_img = qrcode.make(wifi_link)
    qr_dir = f"./static/assets/shop_qr/{shop_code}.png"
    
    if qr_img:
        qr_img.save(qr_dir)
        wifi_qr.save(wifi_dir)

    return qr_dir