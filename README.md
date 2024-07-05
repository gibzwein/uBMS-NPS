# uBMS_NPS
Wyłącznik fotowoltaiki przy cenach ujemnych.\
Urządzenie, które wyłącza fotowoltaikę lub inne źródło przy przekroczeniu ceny minimalnej sprzedaży.\
W menu konfiguracyjnym ustawiamy SSID i hasło do sieci WiFi oraz minimalną cenę sprzedaży energii (PLN/MWh).\
Gdy cena jest niższa, urządzenie podaje napięcie, które może być wyzwalaczem dla cewki stycznika NC (normalnie zamknięty) rozłączającego instalację.

Potrzebne elementy:
1. Sonoff basic R4 (ESP32)
2. Konwerter USB=>UART

Proces instalacji:
  1. Na płytkę Sonoff Basic R4 wgrywamy najnowszy Micropython dla ESP32 C3 zgodnie z instrukcją:\
     https://randomnerdtutorials.com/flashing-micropython-firmware-esptool-py-esp32-esp8266/
  2. Ściągamy zawartość niniejszego repozytorium.
  3. W pliku config.py podajemy swoje dane sieci WiFi, hasło i minimalną cenę sprzedaży energii za MWh.
  4. Ja używam Visual Studio Code i dodatku PyMakr, ale dostępne jest wiele innych rozwiązań.
  5. Wgrywamy potrzebne pliki na płytkę ESP32 Relay board

Jeżeli coś jest niejasne, lub coś Ci nie wychodzi. Napisz do mnie.

Nie oddawaj energii za darmo.\

Jeżeli podoba ci się to co robię i chcesz mnie wesprzeć w dalszych pracach nad projektem.\
<a href="https://suppi.pl/gibzwein" target="_blank"><img width="165" src="https://suppi.pl/api/widget/button.svg?fill=6457FD&textColor=ffffff"/></a>
