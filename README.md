# Graboid Auctions - GrabA

**GrabA** è una piattaforma web orientata alle aste online, simile a eBay, progettata per venditori e acquirenti.

#### Tipologie di utenti

1. **Guest**

    Può navigare liberamente sulla piattaforma senza registrazione, con alcune limitazioni. Può utilizzare la barra di ricerca per trovare aste e visualizzarle, ma non può accedere ai servizi riservati agli utenti registrati.

2. **Utente registrato**

    Per partecipare o creare aste, l’utente deve registrarsi e creare un profilo. In base al tipo (privato o negoziante), la registrazione richiede dati diversi. Dopo la registrazione, l’utente deve attivare la modalità acquirente o venditore per partecipare alle aste o crearne di nuove.

3. **Acquirente**

    Dopo aver attivato la modalità acquirente dal proprio profilo, l’utente può partecipare alle aste. L’attivazione può richiedere informazioni aggiuntive, come indirizzo di spedizione e metodo di pagamento.

4. **Venditore**

    Dopo aver attivato la modalità venditore, l’utente può creare e gestire aste. Anche in questo caso, l’attivazione potrebbe richiedere informazioni aggiuntive come l’indirizzo di spedizione.

#### Lista Preferiti

Gli acquirenti possono aggiungere un’asta alla propria lista dei preferiti, visualizzabile nella pagina del profilo. Le aste preferite possono essere rimosse manualmente in qualsiasi momento.

#### Tipologie di offerta

1. **Offerta (Bid)**

    L’acquirente può fare un’offerta su un’asta, sempre superiore all’offerta attuale o al prezzo minimo stabilito dal venditore. La pagina dell’asta mostra tutte le offerte e permette di inserirne di nuove.

2. **Acquisto diretto (Buy Now)**

    Il venditore può opzionalmente impostare un prezzo massimo durante la creazione dell’asta. L’acquirente può acquistare subito l’oggetto chiudendo immediatamente l’asta. L’acquisto diretto è disponibile solo se non sono state fatte offerte.

#### Recensioni

Un acquirente può lasciare una recensione a un venditore solo se ha vinto un’asta di quel venditore. È consentita una sola recensione per asta vinta. La recensione può contenere testo e un voto da 1 a 5.

---

### Struttura cartelle

<!--
```bash
graba/
│
├─── subfolder/
│    │
│    ├─── subfolder/   # subfolder comment
│    └─── subfile.ext  # subfile comment
│
├─── folder/
└─── file.ext
```
-->

```bash
graba/
│
├─── apps/             # Applicazioni Django
├─── common/           # File statici condivisi
├─── config/           # Applicazione principale e impostazioni
│    ├─── settings/    # Settings Django e configurazioni esterne
│    └─── ...
├─── data/             # Database locali, file mock e immagini
├─── scripts/          # Comandi custom e script Django
└─── manage.py
```

---

# Installazione (Dicembre 2025)

### Dipendenze

Per una corretta installazione è necessario avere installati sul sistema:

- **Python 3.11+**
- **Redis** (per Celery e caching)

> ⚠️ Su Windows potrebbero essere necessari accorgimenti particolari per Redis o per il supporto di Pipenv. Si consiglia di usare WSL2 per un ambiente più simile a Linux.

Soddisfatte le dipendenze sarà possibile predisporre il servizio seguendo la procedura di setup.

### Setup

1. Clona il repository:

    ```bash
    git clone https://github.com/Tremors3/web-tech.git
    cd web-tech
    ```

2. Crea e attiva un ambiente virtuale con Pipenv:

    ```bash
    pip install --user pipenv       # se non già installato
    pipenv shell
    pipenv install --dev
    ```

3. Esegui le migrazioni e popola il database:

    ```bash
    cd graba/
    python manage.py migrate
    python manage.py runscript initdb
    ```

    > `initdb` inserisce dati di test utili per provare subito il progetto.

4. Crea un superuser (opzionale):

    ```bash
    python manage.py createsuperuser
    ```

### Avvio

1. Avvia Redis (se non già in esecuzione):

    ```bash
    redis-server
    ```

2. Avvia Celery

    ```bash
    celery -A config worker -B -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ```

3. Avvia il server di sviluppo Django:

    ```bash
    python manage.py runserver
    ```

    > L’app sarà disponibile su http://127.0.0.1:8000/.

---

## Contributors

<h4 align="left">
    <ul>
        <li>Matteo Menozzi <a href="https://github.com/Tremors3" style="vertical-align: middle;"><img src="https://badgen.net/badge/github/Tremors3/?icon=github"></a></li>
    </ul>
</h4>
