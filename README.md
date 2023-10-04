# telegram-bot-manager
Telegram Bot Manager v23.825.01

This is a compilation of utilities to manage your own PC using a telegram bot to send commands.

---
## Working on
Nothing

## TO-DO
Nothing

## Done
- Integration of "Scheduled automatic organization" functionality in the bot.

---
## Functionalities
- **Roll a dice.** This returns a value between 1 and 6. (command <a href="#dice-functionality">/dice</a>)
- **Start a program from a list.** (command <a href="#start-functionality">/start</a>)
- **Help.** Displays the list of available commands along with a brief explanation. (command <a href="#help-functionality">/help</a>)
- **Turn off the PC.** (command <a href="#shutdown-functionality">/shutdown</a>)
- **Download a file given its URL.** (command <a href="#download-functionality">/download</a>)
- **Take a screenshot.** Sends a screenshot of the PC screen through the bot. (command <a href="#screenshot-functionality">/send_screenshot</a>)
- **Scheduled automatic organization.** Organizes the user downloads folder by file types. (function <a href="#organization-functionality">organize_downloads()</a>)

### <a name="dice-functionality"></a>/dice
The bot "rolls" a dice and return a random number between 1 and 6.

### <a name="start-functionality"></a>/start
The command /start starts a program on the PC.
To get a list of the available programs to start with the command message "/start help".
To modify this list you have to add or remove paths to the program executable to the configuration file "config/programs-locations.txt". It can be a .exe or a .bat.
The format is:

    [key word]=[path to the program]

Example:

    notepad=C:/Windows/system32/notepad.exe

### <a name="help-functionality"></a>/help
This command message you a brief explanation of every command available to use.

### <a name="shutdown-functionality"></a>/shutdown
This command shutdown the PC. Actualy is not inmediate, it retards the shutdown 1 second to let the bot message you a confirmation message.

### <a name="download-functionality"></a>/download
This command downloads a file given its URL.

By default, is saved on the user downloads folder. But you can change it writting the path where you want to save it as a parameter to the command.
It can be an absolute path, or it can be a keyword that represents a commonly used path.

    /download [path where to download]

Example: 

    /download downloads
    /downloads C:\Users\josec\Downloads

To download the resource you need to give all the links separated by a new line.
    
    /download [keyword or path]
    [link1]
    [link2]
    [link3]

Example:

    /download downloads
    https://www.server.com/image1.png
    https://www.server.com/image2.png
    https://www.server.com/image3.png


To see what keywords are available message "/download list" and the bot will message you back with a list of the available paths saved as a keyword.
Asswell, you can modify this list adding or removing paths on the "config/config-paths.txt" file.

### <a name="screenshot-functionality"></a>/send-screenshot
This command messages you back sending a screenshot of every monitor on the PC to see what is in screen at that moment.

### <a name="organization-functionality"></a>organize_downloads()
This function organizes the user downloads folder moving each file into a folder by file type (images, videos, documents, etc.).
If you want to modify where it goes each file by its extension you can modify the file "config/file-extensions.txt". Following the same format you can add new folders or extensions to an existing folder.
The first line is for exceptions. If you don't want an especific file to be moved you can add it to the exceptions line, each filename separated by a comma.

Example:

    exceptions=Descargas.rar,DontMove.png,ThisStaysHere.txt
    videos=.mp4,.mkv,.avi,.mov,.flv,.wmv
    images=.jpg,.jpeg,.png,.gif,.bmp,.tiff
