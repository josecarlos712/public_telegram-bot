import datetime
import os
import re
import shutil
import subprocess
from enum import Enum
from urllib.parse import urlsplit
import mss
import requests
from PIL import Image


class AvailablePaths(Enum):
    DOWNLOADS = "downloads"
    DEF_DOWNLOADS = "default_downloads"
    TEST = "test"


def read_file(file_path):
    try:
        lines = []
        with open(file_path, 'r') as file:
            for line in file:
                # Eliminar los caracteres de nueva línea (\n) al final de cada línea
                line = line.strip()
                lines.append(line)
        return lines
    except Exception as e:
        print("Error al leer el archivo:", e)
        return None


def read_dictionary_file(filename):
    data = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()  # Eliminar espacios en blanco al inicio y final de la línea
            if line:
                key, value = line.split('=')
                data[key] = value
    return data


paths_dictionary = read_dictionary_file("config/config-paths.txt")
paths_to_remove = []

for key, path in paths_dictionary.items():
    if not os.path.exists(path):
        paths_to_remove.append(key)
        print(f"'{path}' no es una ruta válida")

# Eliminar las rutas incorrectas del diccionario
for key in paths_to_remove:
    paths_dictionary.pop(key)

# Leer el diccionario de extensiones
file_types = read_dictionary_file("config/file-extensions.txt")
# Separarlo en sus componentes para almacenarlo como array
for key, value in file_types.items():
    subcadenas = value.split(',')
    file_types[key] = subcadenas

file_exceptions = file_types.pop("exceptions")


def get_current_datetime_string():
    current_datetime = datetime.datetime.now()
    datetime_string = current_datetime.strftime("%Y%m%d%H%M%S")
    return datetime_string


def convert_dict_to_string(dictionary):
    lines = []
    for key, value in dictionary.items():
        line = f"{key} -> '{value}'"
        lines.append(line)
    return '\n'.join(lines)


def execute_program(ruta):
    try:
        # Verificar si el archivo existe
        if os.path.isfile(ruta):
            # Obtener el directorio del archivo
            directorio = os.path.dirname(ruta)
            # Cambiar al directorio del archivo si existe
            if directorio:
                os.chdir(directorio)
            # Ejecutar el archivo según su extensión
            if ruta.endswith(".bat"):
                proceso = subprocess.Popen(["cmd", "/c", ruta], creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif ruta.endswith(".exe"):
                proceso = subprocess.Popen([ruta], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                print("El archivo no es ejecutable.")
                return None
        else:
            print("El archivo no existe.")
            return None
    except Exception as e:
        print(f"Error al ejecutar el archivo: {e}")
        return None

    # Obtener y retornar el PID del proceso recién iniciado
    return proceso


def run_command(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        print(output)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.returncode}, {e.output}")


def run_batch_commands(commands):
    for command in commands:
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.returncode}, {e.output}")


def on_exists(fname):
    # type: (str) -> None
    """
    Callback example when we try to overwrite an existing screenshot.
    """

    if os.path.isfile(fname):
        newfile = fname + ".old"
        print("{} -> {}".format(fname, newfile))
        os.rename(fname, newfile)


def download_file(url, download_path, dictionary_use=False):
    # Send a GET request to the API to download the file
    response = requests.get(url, stream=True)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Extract the filename from the URL
        filename = os.path.basename(urlsplit(url).path)

        # Check if the response headers provide a filename
        if 'Content-Disposition' in response.headers:
            content_disposition = response.headers['Content-Disposition']
            filename = content_disposition.split('filename=')[1].strip('"')

        # Set the path where you want to save the file
        default_download_path = paths_dictionary[AvailablePaths.DOWNLOADS.value]
        save_path = f"{default_download_path}\\{filename}"

        # Download and save the file
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        try:
            if dictionary_use:
                # Obtener una lista de las rutas disponibles
                available_paths = list(paths_dictionary)
                if download_path in available_paths:
                    download_path = paths_dictionary.get(download_path)
                else:
                    print(f"La ruta {download_path} no existe o no es valida.")
                    download_path = default_download_path
                # Mover el archivo a la nueva ubicación
                shutil.move(save_path, f"{download_path}\\{filename}")
            return True, filename
        except Exception as e:
            print(f"Error al mover el archivo de '{default_download_path}' a '{download_path}'")
            print(e)
            return False, filename
    else:
        # print(f"Failed to download file. Status code: {response.status_code}")
        return False, ""


def check_url_format(url):
    # Expresión regular para verificar si el string cumple el formato de una URL
    patron_url = re.compile(
        r'^(https?|ftp)://'  # Protocolo http(s) o ftp
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # Dominio
        r'localhost|'  # También se admite localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # o dirección IP
        r'(?::\d+)?'  # Puerto opcional
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(patron_url.match(url))


# Separa un bloque de urls y las comprueba. Devuelve true si hay al menos una correcta.
def get_url_list(urls_chunk):
    urls = urls_chunk.splitlines()
    urls_validos = [url.strip() for url in urls if check_url_format(url.strip())]

    if len(urls_validos) > 0:
        return True, urls_validos
    else:
        return False, [None]


def take_dual_screen_screenshot():
    try:
        with mss.mss() as sct:
            # Get the number of monitors
            num_monitors = len(sct.monitors)

            # Lista para almacenar las imágenes de ambos monitores
            screenshots = []

            # Captura cada monitor
            for monitor_number in range(num_monitors):
                monitor = sct.monitors[monitor_number]

                # The screen part to capture
                monitor_capture = {
                    "top": monitor["top"],
                    "left": monitor["left"],
                    "width": monitor["width"],
                    "height": monitor["height"],
                    "mon": monitor_number,
                }

                # Grab the data
                sct_img = sct.grab(monitor_capture)

                # Save to the picture file
                output = f"tmp/screenshots/{get_current_datetime_string()}_{monitor_capture['mon']}.png"
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
                screenshots.append(output)

            # Devuelve la lista de nombres de archivo de las imágenes de ambos monitores
            return screenshots

    except Exception as e:
        print("Error al tomar capturas de pantalla:", e)
        return None


def show_multiple_images(image_paths):
    try:
        images = [Image.open(image_path) for image_path in image_paths]

        # Obtiene las dimensiones de las imágenes
        widths, heights = zip(*(img.size for img in images))

        # Calcula el ancho y alto totales del lienzo donde se mostrarán todas las imágenes
        total_width = sum(widths)
        max_height = max(heights)

        # Crea un nuevo lienzo con el tamaño calculado
        combined_image = Image.new('RGB', (total_width, max_height))

        # Pega cada imagen en el lienzo combinado
        x_offset = 0
        for img in images:
            combined_image.paste(img, (x_offset, 0))
            x_offset += img.width

        # Muestra la imagen combinada
        combined_image.show()
    except Exception as e:
        print("Error al mostrar las imágenes:", e)


def organize_downloads(_downloads_path=paths_dictionary[AvailablePaths.DEF_DOWNLOADS.value],
                       _organized_path=paths_dictionary[AvailablePaths.DEF_DOWNLOADS.value]):
    num_organized_files = 0
    # Verifica si la carpeta organizada existe, si no, créala
    if not os.path.exists(_organized_path):
        os.makedirs(_organized_path)

    # Itera a través de los archivos en la carpeta de descargas
    for filename in os.listdir(_downloads_path):
        # Ignora la subcarpeta "Descargas"
        if filename != "Descargas":
            src_path = os.path.join(_downloads_path, filename)

            # Itera a través de los tipos de archivo definidos
            for folder_name, extensions in file_types.items():
                for ext in extensions:
                    # Verifica si la extensión del archivo coincide con alguna de las extensiones definidas
                    if filename.lower().endswith(ext):
                        if not (filename in file_exceptions):
                            dest_folder = os.path.join(_organized_path, folder_name)
                            # Si la carpeta de destino no existe, créala
                            if not os.path.exists(dest_folder):
                                os.makedirs(dest_folder)
                            dest_path = os.path.join(dest_folder, filename)

                            try:
                                # Mueve el archivo a la carpeta de destino
                                shutil.move(src_path, dest_path)
                                print(f"Archivo {filename} movido a {dest_path}")
                                num_organized_files += 1
                            except Exception as e:
                                print(f"Ha ocurrido un error en la organizacion del archivo {filename}\n{e}")
                            break  # Sal del bucle de extensiones, ya que se movió el archivo
                        else:
                            print(f"El archivo {filename} se ha omitido.")
