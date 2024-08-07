import barcode
from barcode.writer import ImageWriter
from django.core.files import File
from io import BytesIO

def generate_barcode(data):
    CODE128 = barcode.get_barcode_class('code128')
    code128 = CODE128(data, writer=ImageWriter())

    buffer = BytesIO()
    code128.write(buffer)

    return File(buffer, name=f'{data}.png')
