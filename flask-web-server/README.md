# Visualisierung der Tinkerforge-Sensordaten

Zur Visualisierung der Sensordaten wird ein Flask-Server instantiiert.
Der Server wird über die Datei webserver.py gestartet.

## Webserver-Datenpfadkonfiguration

Die Pfadstruktur wird über die Variable 'root_path_to_jsons' zur Suche nach den JSONs mit den Sensordaten in der
webserver.py gesetzt.
Der Pfad hat die Form: '/example/dataset'. Unter dem Verzeichnis dataset befinden sich Verzeichnise für jeweils einen
Tag, mit JSONs sowie Bilddateien der Infrarotkamera für diesen Tag.
Somit wird aus dem Pfad die Form /example/dataset/2020-06-20/*json von der Flask-Applikation erstellt und benutzt.

Sobal der Webserver gestartet wurde, können über die URL http://localhost:5000/ die Sensordaten visualisiert werden.
Auf der Website wird eine rudimentäre Navigation bereitgestellt, mit der die einzelnen Tage durchlaufen oder alle
vorhandenn Tage gleichzeitig zur Visualisierunt selektiert werden können.

Die Daten wurden über ein Shell-Script (siehe collect_sensor_data/collect_tinkerforge_data.sh) in einem Turnus von 10
Sekunden gesammelt.
Dabei schwankt die Datenerfassung durch die Sensoren zwischen 1-1.5 Sekunden. Aufgrund dieser Ungenauigkeit werden in
der Webapplikation alle Daten zu einer Funktion zusammengeführt, so dass anschließend eine interpolierte Funktion
berechnet werden kann. Diese Funktion sorgt für die genauen Visualisierung der 10-Sekundenintervalle.