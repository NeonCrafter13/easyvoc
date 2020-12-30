# easyvoc
Eine Vokabel Lern Website
![logo](https://raw.githubusercontent.com/NeonCrafter13/easyvoc_privat/master/Website/favicon.ico?token=AO4RLGP27IDAUAY7Z6IWDYC75SQSY)


## Setup
- In dem Website Ordner kopiere die Datei .envvar.template in .envvar.
- In der .envvar Datei gebe alle Daten an, bei Email Setup muss ein externer SMTP-Server benutzt werden. Ich empfehle MAIL_USE_TLS auf 1 zu setzen.
- MySQL User und Password müssen auch in der docker-compose.yml an gegeben werden.
- Auf dem MySql server muss das SQL Script aus SQL_SETUP ausgeführt werden.
- danach kann `bash ./dockersetup.sh` ausgeführt werden und die Website sollte online gehen.

## Infos 
- Wenn das Security level von einem Nutzer auf 1 oder 2 ist hat er zugriff auf die /admin routes.
- User Table
    - permcreate beschreibt das Recht Aufgaben zu erstellen
    - permreport beschreibt das Recht Reports zu erstellen.
    - email authorizated beschreibt ob der Nutzer Email verifiziert ist nur dann ist ein Passwort zurücksetzen möglich.


## License
Alle Dateien unter [MIT-LICENSE](https://github.com/NeonCrafter13/easyvoc/blob/main/LICENSE).

All Files under [MIT-LICENSE](https://github.com/NeonCrafter13/easyvoc/blob/main/LICENSE)
