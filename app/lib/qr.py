import segno
from io import BytesIO

def generate_qr(uri):
    img = segno.make(uri)
    img_io = BytesIO()
    img.save(img_io, kind="png", scale=10)
    img_io.seek(0)
    return img_io