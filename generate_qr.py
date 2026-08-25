import qrcode

# IMPORTANT:
# Replace this with the IP shown by your app.py
url = "http://192.168.1.10:5000/"

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4
)

qr.add_data(url)
qr.make(fit=True)

img = qr.make_image()

img.save("ecovision_qr.png")

print("QR Code generated successfully!")
print("URL:", url)
print("File: ecovision_qr.png")