# Get Polish Bonds

## Motywacja
W zwiazku z tym ze skaner rentowanosci obligacji na rynku catalyst moim zdaniem zostawia wiele do zyczenia, w szczegolnosci przy przenoszeniu danych do excela, postanowilem stworzyc wlasny skrypt.
Skrypt jest odpowiedzialny za pobranie danych z serwisu z ktorego korzysta ten skaner, agreguje je i zrzuca do excela.

## Wymagania
* Python 3

Biblioteki:
* pandas
* requests
* openpyxl (potrzebne dla pandasu w celu zrzucenia do excela)

w celu instalacji wymaganych bibliotek wywolaj nastepujace polecenie.

```
pip install -r /path/to/requirements.txt
```

## Uruchamianie 

W celu uruchomienia skryptu nalezy wywolac nastepujace polecenie

```
python /path/to/bonds.py
```

Domyslnie program bedzie wolac po wszystkie papiery dluzne notowane na regulowanym rynku GPW,
bez wzgledu na ich rodzaj czy typ odsetek, ktorych dojrzalosc miesci sie w przedziale <1, 5> 
a ich YTM bedzie w przedziale <1, 5>.

### Konfiguracja

Program wspiera nastepuje mozliwosci konfiguracyjne

| **Parametr**            | **Opis**                                     | **Wartosc**                                                        |
|---------------------|------------------------------------------|----------------------------------------------------------------|
| --yf                | Wartosc do wykupu - od                   | Liczba. (Domyslnie: 1)                                         |
| --yt                | Wartosc do wykupu - do                   | Liczba. (Domyslnie: 5)                                         |
| --mt                | Czas do wykupu - od                      | Liczba. (Domyslnie: 1)                                         |
| --mf                | Czas do wykupu - do                      | Liczba. (Domyslnie: 5)                                         |
| -r / --rate         | Rodzaj odsetek                           | Lista elementow odzielona spacja. Domyslnie wszystkie elementy |
|                     |                                          | ZC - zero kuponowe                                             |
|                     |                                          | XC -  staly kupon                                              |
|                     |                                          | FC - zmienny kupon                                             |
|                     |                                          | IN - indeksowana wartosc nominalna                             |
| -t / --type         | Rodzaj papieru                           | Lista elementow odzielona spacja. Domyslnie wszystkie elementy |
|                     |                                          | TB - skarbowe                                                  |
|                     |                                          | MB - komunalne                                                 |
|                     |                                          | CB - korporacyjne                                              |
|                     |                                          | SB - spoldzielcze                                              |
|                     |                                          | MG - listy zastawne                                            |
| -b / --bondspot     | Czy wyszukiwac na rynku BondSpot         | - (jest to flaga, wystarczy obecnosc)                          |
| -a / --alternatives | Czy wyszukiwac na rynkach alternatywnych | - (jest to flaga, wystarczy obecnosc)                          |

### Przyklady

1. W celu zawolania po stalokuponowe lub zerokuponowe obligacje skarbowe i korporacyjne,
notowanych na rynku catalyst i BondSpot, ktorych wartosc do wykupu miesci sie w
przedziale <1, 3,5> roku, nalezy wykonac nastepujace polecenie:

```
python /path/to/bonds.py --yf 1 --yt 3.5 -r ZC XC -t TB CB -b
```

2. W celu zawolania po zmiennokuponowe obligacje korporacyjne,
notowanych na rynku catalyst regulowanym i alternatywnym, ktorych wartosc do wykupu miesci sie w
przedziale <1, 3.5> roku a czas do wykupu miesci sie w przedziale <1, 2> nalezy wykonac
nastepujace polecenie
```
python /path/to/bonds.py --yf 1 --yt 3.5 -r FC -t CB -a --mf 1 --mt 2
```

## Wyniki

W katalogu w ktorym zostala wykonana komenda powstanie nastepujacy plik 
`bonds-${d}-${m}-${Y}.xlsx`, gdzie pod `${d}`, `${m}`, `${Y}` kolejno zostana podstawione
aktualny dzien, miesiac i rok. W powstalym pliku znajda sie nastepujace kolumny:

* Rynek - rynek na ktorym notowana jest obligacja 
GPW, GPW Alternatywny, BondSpot, BondSpot Alternatywny
* Nazwa - nazwa obligacji
* Emitent
* Typ - rodzaj papieru, czy komunalne skarbowe itd.
* Kupon - rodzaj kuponu, czy stalokuponowe, zerokuponowe itd.
* Kurs - aktualny kurs
* Oprocentowanie - aktualne oprocentowanie
* Roczna stopa zwrotu brutto
* Roczna stopa zwrotu netto 
* Zapadalnosc - czas do wykupu
* Zwrot z inwestycji brutto - szacowany zwrot z inwestycji, Roczna stopa zwrotu brutto * Zapadalnosc
* Zwrot z inwestycji netto - szacowany zwrot z inwestycji, Roczna stopa zwrotu netto * Zapadalnosc
