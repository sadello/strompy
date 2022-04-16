# strompy- Siemens TD-3511 Stromzähler mit Raspberry Pi auslesen und per MQTT publizieren.
Dieses Programm ist für AES verschlüsselte, oberösterreichische Zähler ausgelegt. Ich verarbeite die per MQTT übermittelten Werte anschließend mit iobroker, der am selben Raspi ebenfalls als eigenständiger Container läuft.


## Installation
- example.env im Programmverzeichnis duplizieren, auf die eigenen Bedürfnisse anpassen und auf .env umbenennen.
### Direktaufruf
- Python 3 installieren
- Bibliotheken aus requirements.txt installieren (`pip install pyserial`)
- `python3 strompy.py &`
### Dockercontainer
- Source downloaden
- in commandline in das dockerfile-Verzeichnis wechseln
- `docker build -t strompy .`
- `docker run -d --restart unless-stopped --device /dev/ttyAMA0:/dev/ttyAMA0 --name strompy strompy`
- .env Datei entweder schon vorher anpassen oder per Dockervolume einbinden oder Einzelwerte als Environmentvariablen übergeben (übersteuern jene der .env)

## Vorbereitungen
Den AES Schlüssel bekommt man unter https://eservice.netzooe.at/app/login 
Im Dashboard kann man unter seinem Strom-Vertragskonto unter "MBUS Key" den Schlüssel ganz einfach und sofort in Erfahrung bringen.

Als Lesekopf verwende ich einen [zugekauften "Eigenbau"](https://www.photovoltaikforum.com/thread/141332-neue-lesekopf-baus%C3%A4tze-ohne-smd-l%C3%B6ten/), kommerzielle Produkte wie z.B. von Weidmann dürften auch funktionieren, könnten aber ggf. andere TTY-Angaben als jene der Beispiel-env-Datei benötigen.

## Dankeschön
Vielen Dank an [Volkszähler.de](https://wiki.volkszaehler.org/hardware/channels/meters/power/edl-ehz/siemens_td3511_in_oberoesterreich) und Schnello_AT (mit Helfern) im [Photovoltaikforum](https://www.photovoltaikforum.com/thread/107784-siemens-td-3511-auslesen/?t=107784&start=30), deren Knowhow ich nur noch in ein Programm bringen musste.
... und Hichi für den IR-Lesekopf!
