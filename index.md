---
layout: index
---

### eMonitor

eMonitor ist eine Applikation zur automatisierten Alarmfax-Auswertung. Organisationen im BOS-Bereich werden in
Deutschland gewöhnlich per FAX alarmiert oder erhalten zur Einsatzbestätigung ein Alarmfax.
eMonitor kann dieses Alarmfax auswerten und die enthaltenen Informationen verarbeiten. Daraus werden *Einsätze*
generiert, die anschließend auf einem Monitor übersichtlich dargestellt werden können.

**NEU:** [**Universeller Fax-Parser**][6]


**Derzeit sind folgende Funktionen verfügbar:**

* Adressvalidierung über OpenStreetMap
* Kartendarstellung auf dem Monitor
* Individuelle Ausrückeordnungen je Alarmstichwort
* Drucken einer Alarmübersicht mit Kartendarstellung
* [**weitere Details**][5]

eMonitor und sämtliche genutzte Komponenten stehen **OpenSource** zur Verfügung und werden ständig weiter entwickelt.

Die Dokumentation zum Server finden Sie [**hier**][1]

### Client

Für die Darstellung auf dem Monitor ist der **Client erforderlich**, der unter
[Client](https://github.com/seiferta/eMonitor-Client) steht unter https://github.com/seiferta/eMonitor-Client zur
Verfügung steht.

Informationen zum Client finden Sie [**hier**][2]

### Installation

Die komplette Anwendung ist mit Python 2.x geschrieben und unterstützt Windows und Linux Betriebssysteme.

* [**Linux**][3]

* [**Windows**][4]

### VirtualBox Image

Für VirtualBox steht ein Image im VDI-Format zum Download bereit. Das Image setzt auf Ubuntu auf und liefert eine komplett eingerichtete Umgebung für eMonitor. Details finden Sie [**hier**][7] 

[1]: server
[2]: client
[3]: install/linux
[4]: install/windows
[5]: details
[6]: faxchecker
[7]: install/image
