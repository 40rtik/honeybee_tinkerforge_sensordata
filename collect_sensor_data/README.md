# Sensordatenrefassung

Die Datenrefassung durch die Tinkerforge-Sensoren wird über das Shell-Script 'collect_tinkerforge_data.sh' gestaret.
Intern wird das Pythonscript 'tinkerforge_collection.py' in einem Intervall von 10 Sekunden aufgerufen.

# Sensordatenablage

Die Datenerfassung über das Script 'tinkerforge_collection.py' legt die erfassten Sensordaten in das Verzeichnis '
data/'.
Die Thermalimages werden separat als eigene Datei parallel zum JSON gespeichert.
Die Images haben den Suffix 'thermal_image_' mit einem Zeitstempel. Die JSONs haben den Suffix 'sensor_data_' mit einem
Zeitstempel. Diese Dateinamen werden benutzt um mit den Script 'move_data_to_date_directory.py' die Dateine in separate
Verzeichnisse zu unterteilen. Der Aufbau dieser Verzeichnisse kann im Package flask-web-server/example/dataset
eingesehne werden.