import logging
import multiprocessing
import os
import random as rn
import time

import schedule
from PIL import Image
from pystray import Icon, MenuItem
from telegram import Update, InputMediaPhoto
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import utils

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Constantes
ORGANIZATION_POLLING_RATE = 10

# Ejemplo de uso
token = "TELEGRAM_API_TOKEN"
chat_id = "TELEGRAM_BOT_ID"
texto = "¡Hola desde el bot de Telegram!"
allowed_ids = [5382603273]

application = ApplicationBuilder().token(token).build()
# Carga de lista de programas a iniciar con "start"
locDic = utils.read_dictionary_file('config/programs-locations.txt')
command_list_file_path = "config/commands.txt"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id in allowed_ids:
        args = context.args
        if len(args) > 0:
            if args[0] == "list":
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"{utils.convert_dict_to_string(locDic)}")
            elif len(locDic) > 0:
                if args[0] in locDic:
                    ruta = locDic[args[0]]
                    if utils.execute_program(ruta):
                        await context.bot.send_message(chat_id=update.effective_chat.id,
                                                       text=f"El proceso \"{args[0]}\" ha iniciado correctamente.")
                    else:
                        await context.bot.send_message(chat_id=update.effective_chat.id,
                                                       text=f"El proceso \"{args[0]}\" ha fallado al iniciarse.")
                else:
                    print("La clave no existe en el diccionario.")
                    return False
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text="No hay rutas en el archivo programs-locations.txt")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Este comando necesita al menos un parametro indicando el programa a iniciar.\r\nPara saber que programas estan disponibles para iniciar escribe \"/start list\"")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Tu usuario no tiene permisos para ejecutar este comando.")


async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = rn.randint(1, 6)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ha salido un {r}")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_list = utils.read_file(command_list_file_path)
    command_list_string = '\n' + '\n'.join(command_list)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Lista de comandos disponibles: {command_list_string}")


async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    os.system("shutdown /s /t 1")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"El PC se está apagando.")


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    # Obtener el mensaje completo enviado por el usuario
    message_text = update.message.text

    # Dividir el mensaje en líneas para obtener cada URL por separado
    urls = message_text.split("\n")

    # Leer el primer elemento que contiene el comando /download para determinar a que carpeta se moverá el archivo
    # una vez se descargue
    # Eliminar la subcadena "/download "
    download_path = urls[0].replace("/download ", "").strip()
    # Luego se extrae para recorrer mas facilmente el array
    urls.pop(0)
    # Comprobar si la ruta existe
    if download_path == "list":
        available_paths = [f"{apath.value} - {utils.paths_dictionary.get(apath.value)}" for apath in
                           list(utils.AvailablePaths)]
        available_paths_message = "\n".join(available_paths)
        await context.bot.send_message(chat_id=chat_id,
                                       text=f"Rutas disponibles para descargar:\n{available_paths_message}")
    elif download_path == "":
        if len(urls) > 0:
            download_path_message = "por defecto."
            file_or_files = "archivo" if len(urls) == 1 else "archivos"
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"Descargando {len(urls)} {file_or_files} en la ruta por defecto.")

            # Activar la bandera de uso del diccionario de rutas para que la funcion download_file corriga la ruta
            path_dict_use = True

            # Recorrer todas las URLs y descargarlas
            for u in urls:
                if utils.check_url_format(u):
                    await context.bot.send_message(chat_id=chat_id, text=f"Descargando {u}")
                    # Descarga del archivo
                    ok_download, filename = utils.download_file(u, download_path, dictionary_use=path_dict_use)
                    if ok_download:
                        await context.bot.send_message(chat_id=chat_id,
                                                       text=f"Archivo descargado: {filename}")
                    else:
                        await context.bot.send_message(chat_id=chat_id,
                                                       text=f"Error al descargar el archivo.")
                else:
                    await context.bot.send_message(chat_id=chat_id, text=f"URLs invalidas: {urls}")
        else:
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"Debe proporcionar una o varias URL separadas por un salto de linea dejando la linea del comando para especificar la ruta de destino: /download ruta_de_destino\nhttps://url/\nhttps://url/\nhttps://url/")
    else:
        # Se comprueba si la ruta data esta en el diccionario de rutas
        available_paths = [apath.value for apath in list(utils.AvailablePaths)]
        if download_path in available_paths:
            # Activar la bandera de uso del diccionario de rutas para que la funcion download_file la sustituya la ruta
            path_dict_use = True
        else:
            print(f"{download_path} is not on {available_paths}")
            if not os.path.exists(download_path):
                # Si no, se lanza un mensaje de error
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f"La ruta '{download_path}' no existe. Se omitira la descargas de los archivos.")
                return 0

        if len(urls) > 0:
            if path_dict_use:
                download_path_message = f"\"{download_path}\""
            else:
                download_path_message = "por defecto."
            file_or_files = "archivo" if len(urls) == 1 else "archivos"
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"Descargando {len(urls)} {file_or_files} en la ruta {download_path_message}")

            # Recorrer todas las URLs y descargarlas
            for u in urls:
                if utils.check_url_format(u):
                    await context.bot.send_message(chat_id=chat_id, text=f"Descargando {u}")
                    # Descarga del archivo
                    ok_download, filename = utils.download_file(u, download_path, dictionary_use=path_dict_use)
                    if ok_download:
                        await context.bot.send_message(chat_id=chat_id,
                                                       text=f"Archivo descargado: {filename}")
                    else:
                        await context.bot.send_message(chat_id=chat_id,
                                                       text=f"Error al descargar el archivo.")
                else:
                    await context.bot.send_message(chat_id=chat_id, text=f"URLs invalidas: {urls}")
        else:
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"Debe proporcionar una o varias URL separadas por un salto de linea dejando la linea del comando para especificar la ruta de destino: /download ruta_de_destino\nhttps://url/\nhttps://url/\nhttps://url/")


async def send_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Indicar que el bot está cargando contenido (opcional)
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)

    # Rutas de las tres imágenes que deseas enviar
    image_paths = utils.take_dual_screen_screenshot()
    image_paths.pop(0)

    # Crear una lista de objetos InputMediaPhoto con las imágenes
    media = [InputMediaPhoto(open(image_path, 'rb')) for image_path in image_paths]

    # Enviar las imágenes como un mensaje
    await context.bot.send_media_group(chat_id=chat_id, media=media)


async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) > 2:
        print(args[1])


async def default(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="El comando no existe.\r\nPara obtener la "
                                                                          "lista de programas disponibles para "
                                                                          "iniciar escribe \"/start list\"")


async def on_quit(icon, item):
    icon.stop()
    await application.stop()


def icon_thread():
    icon_image = Image.open("icon.ico")  # Reemplaza con la ruta de tu archivo .ico
    menu = (MenuItem('Salir', on_quit),)
    icon = Icon("nombre_app", icon_image, "Telegram bot", menu)

    icon.run()


def organize_downloads():
    utils.organize_downloads()
    utils.organize_downloads(_downloads_path=utils.paths_dictionary[utils.AvailablePaths.DOWNLOADS.value],
                             _organized_path=utils.paths_dictionary[utils.AvailablePaths.DOWNLOADS.value])


def organize_and_schedule():
    # Planificar la ejecución cada hora
    schedule.every(ORGANIZATION_POLLING_RATE).seconds.do(organize_downloads)

    while True:
        schedule.run_pending()
        time.sleep(ORGANIZATION_POLLING_RATE / 2)


def bot_thread():
    start_handler = CommandHandler('start', start)
    dice_handler = CommandHandler('dice', dice)
    command_handler = CommandHandler('command', command)
    download_handler = CommandHandler('download', download)
    shutdown_handler = CommandHandler('shutdown', shutdown)
    send_screenshot_handler = CommandHandler('send_screenshot', send_screenshot)
    help_handler = CommandHandler('help', help)
    application.add_handler(start_handler)
    application.add_handler(dice_handler)
    application.add_handler(command_handler)
    application.add_handler(shutdown_handler)
    application.add_handler(download_handler)
    application.add_handler(send_screenshot_handler)
    application.add_handler(help_handler)

    application.run_polling()


if __name__ == '__main__':
    # Crear el proceso del bot
    thread_bot = multiprocessing.Process(target=bot_thread)
    # Crear un hilo para la planificación y organización
    organize_process = multiprocessing.Process(target=organize_and_schedule)

    # Iniciar el proceso del bot
    thread_bot.start()
    organize_process.start()

    icon_thread()
