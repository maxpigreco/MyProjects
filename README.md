# MyProjects — Django demo blog

Sito dimostrativo realizzato con Django 5.2.3: autenticazione utenti, profili,
blog con ricerca, form di contatto e recupero password. I contenuti del blog si
gestiscono da Django admin.

Il progetto è pensato per l'uso locale e per attività didattiche: non è
configurato per la produzione. Pianificazione, decisioni e stato di
avanzamento sono in [`PLAN.md`](PLAN.md).

## Stato attuale

- Fase 1 in corso: WP1–WP3 completati, WP4–WP7 da fare.
- Test automatici: 19 test verdi (`blog` e `accounts`).
- Database locale SQLite con dati demo; non viene versionato.

## Requisiti di sistema

- **Python 3.12+** con `venv` e `pip`.
- **SQLite**, incluso nella libreria standard di Python: nessun server DB.
- **Git** per clonare il repository.
- Nessun servizio esterno richiesto: niente PostgreSQL, Redis, Node.js o
  Docker in questa fase.
- Ambiente di riferimento: Linux. Su macOS i comandi sono gli stessi; su
  Windows vanno adattati i percorsi del virtualenv (vedi sotto).

Su Debian/Ubuntu il pacchetto del virtualenv può essere installato con:

```bash
sudo apt install python3.12 python3.12-venv
```

## Setup

1. Clona il repository e entra nella cartella:

   ```bash
   git clone <url-del-repository> MyProjects
   cd MyProjects
   ```

2. Crea e attiva il virtualenv con Python 3.12 (sostituisci il percorso se il
   tuo interprete è diverso):

   ```bash
   /usr/bin/python3.12 -m venv .venv
   source .venv/bin/activate
   ```

   Su Windows:

   ```powershell
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   ```

3. Installa le dipendenze:

   ```bash
   pip install -r requirements.txt
   ```

4. Crea il file `.env` a partire dall'esempio:

   ```bash
   cp .env.example .env
   ```

5. Genera una chiave segreta e inseriscila in `.env` come
   `DJANGO_SECRET_KEY`:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   Su Linux/macOS limita i permessi del file:

   ```bash
   chmod 600 .env
   ```

6. Applica le migrazioni (crea anche `db.sqlite3`):

   ```bash
   python manage.py migrate
   ```

7. Crea un utente amministratore, se serve accedere all'admin:

   ```bash
   python manage.py createsuperuser
   ```

8. Avvia il server di sviluppo:

   ```bash
   python manage.py runserver
   ```

   Poi apri <http://127.0.0.1:8000/>. L'admin è su
   <http://127.0.0.1:8000/admin/>.

## Configurazione dell'ambiente

Le variabili sono lette da `.env`, caricato automaticamente da
`MyProjects/settings.py`. Le variabili già presenti nell'ambiente di sistema
hanno la precedenza sul file.

| Variabile | Obbligatoria | Descrizione |
|---|---|---|
| `DJANGO_SECRET_KEY` | Sì | Chiave segreta Django. Se manca, l'avvio fallisce con `ImproperlyConfigured`. |

Note sull'ambiente di sviluppo:

- `DEBUG = True`, `ALLOWED_HOSTS` vuoto e SQLite locale: configurazione valida
  solo in locale.
- Le email sono stampate nella console del server tramite il backend console di
  Django; non viene inviato traffico SMTP reale.
- `db.sqlite3` e i backup `*.bak` sono ignorati da git e non vanno eliminati o
  resettati senza backup.
- `.env` è ignorato da git: non committare mai la chiave reale.
- I file `desktop.ini` e `*:Zone.Identifier` sono metadati di Windows e vanno
  ignorati.

## Comandi utili

Esegui i comandi con il virtualenv attivo:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py test blog.tests.PostModelTests.test_slug_is_generated_from_title
python manage.py runserver
python manage.py createsuperuser
```

## Struttura del progetto

```
MyProjects/
├── manage.py
├── MyProjects/          # impostazioni, URL e configurazione WSGI/ASGI
├── blog/                # post, viste pubbliche, form contatti e ricerca
├── accounts/            # signup, login, profili e reset password
├── templates/           # layout condiviso e template di registrazione
├── requirements.txt     # dipendenze con versioni bloccate
├── .env.example         # esempio di configurazione locale
└── PLAN.md              # piano canonico e stato di avanzamento
```

## Test

```bash
python manage.py test
```

I test coprono il modello `Post` e il relativo admin, la creazione dei profili,
il signup, la modifica del profilo e il flusso completo di reset password.
