# Icy Tower Clone

Gra platformowa inspirowana klasycznym Icy Tower, stworzona w PyGame. Wspinaj się jak najwyżej, unikając przeszkód i zbierając power-upy!

[Link do prezentacji projektu](https://www.canva.com/design/DAGoHOnrRVw/3a_lxSfqsr05ycl9wtO-cQ/edit?utm_content=DAGoHOnrRVw&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

## Opis
W grze sterujesz postacią, która musi wspinać się coraz wyżej po platformach. Każdy region wprowadza nowe wyzwania i zwiększa trudność rozgrywki. Zbieraj monety, aby aktywować specjalny Hyper Jump, i unikaj kolców oraz lawy!

## Wymagania
- Python 3.x
- PyGame

## Instalacja
```bash
pip install pygame
```

## Uruchomienie
```bash
python icy_tower.py
```

## Sterowanie
- Strzałki lewo/prawo: Poruszanie postacią
- Spacja: Skok
- Strzałka w górę: Aktywacja Hyper Jump
- P: Pauza
- R: Restart po przegranej
- ESC: Wyjście do menu

## Funkcjonalności
1. **Sterowanie i interakcja**
   - Intuicyjne sterowanie postacią
   - System kolizji z platformami i przeszkodami

2. **Logika gry**
   - System punktacji oparty na wysokości
   - Power-up Hyper Jump
   - Zbieranie monet
   - System progresji przez regiony
   - Proceduralne generowanie platform

3. **Interfejs i struktura**
   - Menu główne z wyborem trudności
   - System pauzy
   - HUD
   - Ekran końca gry

4. **Mechaniki specjalne**
   - Różne typy platform (normalne, ruchome, śliskie)
   - System przeszkód (kolce)
   - Mechanika rosnącej lawy
   - Regiony o różnej trudności

## Poziomy trudności
- **No Lava**: Tryb treningowy bez lawy
- **Casual**: Umiarkowana prędkość lawy
- **Hard**: Szybka lawa i większe wyzwanie

## Regiony
1. Podstawa (0-4000)
2. Środek (4000-10000)
3. Wyżyny (10000-18000)
4. Chmury (18000-28000)
5. Stratosfera (28000+)

Każdy region wprowadza nowe wyzwania:
- Większe odstępy między platformami
- Więcej ruchomych i śliskich platform
- Częstsze występowanie kolców
- Szybsze platformy ruchome
