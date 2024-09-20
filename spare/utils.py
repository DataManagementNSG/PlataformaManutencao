import barcode
from barcode.writer import ImageWriter
from django.core.files import File
from io import BytesIO

def generate_barcode(data):
    CODE128 = barcode.get_barcode_class('code128')
    
    # Configurar tamanho da etiqueta e outras opções
    options = {
        'module_width': 0.2,  # Largura de cada "barra" do código de barras
        'module_height': 3.0,  # Altura de cada "barra"
        'font_size': 8,  # Tamanho da fonte para o texto abaixo do código
        'text_distance': 4.0,  # Distância entre o texto e o código de barras
        'quiet_zone': 0.5,  # Margem ao redor do código de barras
    }
    
    code128 = CODE128(data, writer=ImageWriter())
    
    # Criar buffer para armazenar a imagem do código de barras
    buffer = BytesIO()
    code128.write(buffer, options=options)
    
    # Retornar arquivo de imagem com o código de barras
    return File(buffer, name=f'{data}.png')
