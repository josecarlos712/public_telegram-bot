import os
import shutil

import utils

# Rutas de las carpetas
downloads_path = utils.paths_dictionary[utils.AvailablePaths.DEF_DOWNLOADS.value]
organized_path = utils.paths_dictionary[utils.AvailablePaths.DOWNLOADS.value]

# Leer el diccionario de extensiones
file_types = utils.read_dictionary_file("config/file-extensions.txt")
# Separarlo en sus componentes para almacenarlo como array
for key, value in file_types.items():
    subcadenas = value.split(',')
    file_types[key] = subcadenas

file_exceptions = file_types.pop("exceptions")
"""
# Extensiones por tipo de archivo
file_types = utils.read_dictionary_file("config/file-extensions.txt")
file_types = {
    "videos": [".mp4", ".mkv", ".avi"],
    "imagenes": [".jpg", ".jpeg", ".png", ".gif"],
    "torrents": [".torrent"],
    "comprimidos": [".rar", ".zip", ".7z", ".bin"],
    # Agrega más tipos de archivos según lo necesites
}
"""


def organize_downloads(_origin_folder=downloads_path, _destiny_folder=downloads_path):
    """
    Organiza los archivos en la carpeta de descargas en subcarpetas según su tipo de archivo.

    :param _origin_folder: Ruta de la carpeta de descargas.
    :param _destiny_folder: Ruta donde se organizarán los archivos.
    """

    # Crea la carpeta organizada si no existe
    if not os.path.exists(_destiny_folder):
        os.makedirs(_destiny_folder)

    operations_summary = []  # Lista para almacenar las operaciones realizadas

    # Itera a través de los archivos en la carpeta de descargas
    for filename in os.listdir(_origin_folder):
        if filename != "Descargas":
            src_path = os.path.join(_origin_folder, filename)

            # Itera a través de los tipos de archivo definidos
            for folder_name, extensions in file_types.items():
                for ext in extensions:
                    # Verifica si la extensión del archivo coincide con alguna de las extensiones definidas
                    if filename.lower().endswith(ext):
                        dest_folder = os.path.join(_destiny_folder, folder_name)
                        # Crea la carpeta de destino si no existe
                        if not os.path.exists(dest_folder):
                            os.makedirs(dest_folder)
                        dest_path = os.path.join(dest_folder, filename)

                        try:
                            shutil.move(src_path, dest_path)
                            operations_summary.append(f"Archivo {filename} movido a {dest_path}")
                        except Exception as e:
                            operations_summary.append(f"Error al mover el archivo {filename}: {e}")
                        break

    # Eliminar carpetas vacías en _organized_path y agregar a las operaciones realizadas
    for folder_name in file_types.keys():
        folder_path = os.path.join(_destiny_folder, folder_name)
        if os.path.exists(folder_path) and not os.listdir(folder_path):
            try:
                os.rmdir(folder_path)
                operations_summary.append(f"Carpeta {folder_path} vacía, eliminada")
            except Exception as e:
                operations_summary.append(f"No se pudo eliminar la carpeta {folder_path}: {e}")

    # Imprimir el resumen de operaciones
    print(f"Resumen de operaciones de la carpeta {_origin_folder}:")
    if len(operations_summary) > 0:
        for operation in operations_summary:
            print(operation)
    else:
        print("No se ha realizado ninguna accion.")


organize_downloads()
organize_downloads(_origin_folder=organized_path, _destiny_folder=organized_path)
