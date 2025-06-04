import barcode
from barcode.writer import ImageWriter
from django.core.files import File
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def generate_barcode(data, localizacao, descricao):
    CODE128 = barcode.get_barcode_class('code128')
    
    # Configurar tamanho da etiqueta e outras opções
    options = {
    'module_width': 0.2,
    'module_height': 3.0,
    'font_size': 8,
    'text_distance': 4.0,
    'quiet_zone': 0.5,
    }

    code128 = CODE128(data, writer=ImageWriter())
    buffer_barcode = BytesIO()
    code128.write(buffer_barcode, options=options)
    buffer_barcode.seek(0)
    barcode_img = Image.open(buffer_barcode)

    etiqueta_width = 500
    etiqueta_height = 170
    etiqueta = Image.new("RGB", (etiqueta_width, etiqueta_height), "white")
    draw = ImageDraw.Draw(etiqueta)

    font_title = ImageFont.load_default()
    font_text = ImageFont.load_default()

    logo = Image.open(r'C:\Users\rm0038\OneDrive - NSG\Documentos\Manutencao\PlataformaManutencao\app\static\nsg.png').convert("RGBA")
    logo = logo.resize((40, 20))
    etiqueta.paste(logo, (10, 10), logo)

    font_title = ImageFont.truetype("arialbd.ttf", 20)
    font_text = ImageFont.truetype("arialbd.ttf", 16)
    text1 = localizacao
    text1_size = draw.textbbox((0, 0), text1, font=font_title)
    text1_width = text1_size[2] - text1_size[0]
    draw.text(((etiqueta_width - text1_width) // 2, 10), text1, font=font_title, fill="black")

    text2 = descricao
    text2_size = draw.textbbox((0, 0), text2, font=font_text)
    text2_width = text2_size[2] - text2_size[0]
    draw.text(((etiqueta_width - text2_width) // 2, 40), text2, font=font_text, fill="black")
    

    barcode_resized = barcode_img.resize((300, 120))
    etiqueta.paste(barcode_resized, (100, 80))

    border_size = 15
    etiqueta_com_borda = Image.new(
        "RGB",
        (etiqueta_width + 2 * border_size, etiqueta_height + 2 * border_size),
        "#0094C8"
    )
    etiqueta_com_borda.paste(etiqueta, (border_size, border_size))

    # Salvar em memória e retornar como File
    final_buffer = BytesIO()
    etiqueta_com_borda.save(final_buffer, format='PNG')
    final_buffer.seek(0)

    return File(final_buffer, name=f"{data}.png")
