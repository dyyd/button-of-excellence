# button-of-excellence
Garage48 EduTech Hackathon project Button of Excellence

Web interface and REST API for registering button presses from specific hardware button over HTTP(S) protocol and 
allowing useful aggregation of buttons and presses.
Initial use-case is for use in school classrooms for registering attendance or answers to questions.

System uses ID-s for each button which can be connected to a user in the system. Also allows for pseudo-anonymous 
use-cases where from a group of buttons only number of unique presses are registered and no identification information 
is provided.

## Requirements

Python 3.6
pip3

## Running the app


## Ideas

#### UI:
  * Central display with count of presses (and percentage of total compared to registered in group) in time window  
  (needs to have "reset" option since time window might need to change during class e.g multiple questions that have 
  different times to answer)
  * Central display changes colour if context requires it upon hitting treshold
  * Configuration page that allows:
    - Creating and configuring contexts
    - adding/removing/editing users and groups
    -
  * Review that shows timeline of button presses (anonymous or unanonymous)
  * Tester tool that allows to generate x number of virtual buttons and press them with each press being registered by 
  app



## TODO:
* Testide sait
* Bugide parandamine
  - Sessioonide tegemine avab aegajalt vana sessiooni
  - Kasutajate tegemine feilib
  - Gruppide tegemine feilib
  - "Lõpeta sessioon" nupp peaks olema ainult aktiivsel sessioonil ja muidu peaks seal kas nupp puuduma või olema null 
  "Tagasi"
  - % paigutus paigast ära
* Nupu vajutuse päringu tüüp muuta POST-ks
* Sessioonide leht ümber teha nimekirjaks, et rohkem mahuks lehele (pagineerimine)
* Gruppide ja kasutajate leht teha vähem ruumimahukaks (loomine väiksemaks ja nimekiri normaalsemaks tabeliks)
* Sessiooni kestvuse counter
* Lüüa sessiooni loomine ja ülevaade eraldi lehtedele ja "home" peaks olema Sessiooni alustamine
* Kuvada sessiooni infot tabelis onClick tulemina mitte eraldi lehel ("unhide" stiilis tabeli alaminfo)
* Refactor page reloading to only reload when fetching from API results in new values
* Statistika lehel näidata ajajoont õpilase aktiivsusest (Stiilis nimekirjas onClick avab ajajoone kus info peal. Või 
  siis üks suurem statisika tabel kus on võimalik aktiveerida õpilasi ja küsimuste liike ja küsimusi ja konditsioone jne)
* Tunnis kohaoleku kontrolli lisamine mille põhjal statistika saaks paremini hinnata kohal oldud osalust.  (Võib-olla 
  oleks parem lihtsalt, kui statistika võimaldaks üldisest osalusest mingeid osalusi lisada/eemaldada või konditsiooni 
  seada, et näita neid kui see on tõene vms. Annab suurema paindlikkuse)
* Sisse logimine kasutajana
* Küsimuste kontekstid (mitu küsimust sessiooni kohta)
* Kasutajate muutmise võimekus
* Kasutajate kustutamise võimekus
* Gruppide muutmise võimekus
* Gruppide kustutamise võimekus
* Sessioonide muutmise võimekus
* Sessioonide kustutamise võimekus
* Koodi refaktoreerimine
* https://flask-restful.readthedocs.io/en/0.3.5/


## Development env setup

pip3 install -r requirements.txt