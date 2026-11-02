# PLAN.md — MyProjects

**Documento canonico di pianificazione e tracking.** Versione 1.0 — 2026-10-29.
Percorso canonico: `/home/max/projects/MyProjects/PLAN.md`.

Questo file è l'unica fonte di verità per pianificazione, stato e avanzamento
del progetto. Sostituisce `roadmap.md` e le pianificazioni precedenti (anche
quelle in `~/.opencode/plan`), che restano solo come storico. Ogni aggiornamento
di piano va fatto qui: non creare duplicati altrove.

Repository: `/home/max/projects/MyProjects`
Stack: Django 5.2.3, Python 3.12 (`.venv`), SQLite.

---

## 1. Come usare questo documento

**Legenda stato fase**

| Simbolo | Significato |
|---|---|
| `[ ]` | Non iniziata |
| `[~]` | In corso |
| `[x]` | Completata |
| `[!]` | Bloccata |
| `[-]` | Rinviata / condizionale / fuori scope |

**Legenda task:** `- [ ]` da fare, `- [x]` completato.

**Protocollo di aggiornamento**

1. Segnare il task completato con `[x]`.
2. Aggiornare la dashboard di sezione 3 (stato e conteggi).
3. Aggiungere una riga nel changelog (sezione 10).
4. Non segnare una fase come `[x]` finché tutti i suoi criteri di accettazione
   non sono verificati con i comandi della sezione 9.

---

## 2. Contesto verificato (aggiornato 2026-10-30)

| Fatto | Evidenza |
|---|---|
| Progetto Django con app `blog` (`/`) e `accounts` (`/accounts/`) | `MyProjects/urls.py` |
| 6 post nel DB, 3 utenti, 1 solo profilo | query su `db.sqlite3` |
| Nessuna pagina di dettaglio post; `/` è una landing di link | `blog/urls.py`, `index.html` |
| Ricerca con link `href="#"` e senza filtro sui post privati | `blog/views.py`, `search.html` |
| `Post.views` mai incrementato | `blog/views.py` |
| 0 test; `check --deploy` con 7 warning | `manage.py test`, `check --deploy` |
| `/accounts/profile/edit/` anonimo → 500 confermato | smoke test HTTP |
| `db.sqlite3`, `.env` e `*.bak` non tracciati; `SECRET_KEY` da env | `git ls-files`, `settings.py` |
| Repo git su `main`, commit WP1 incluso | `git log` |
| Implementazione: WP1–WP2 completati; WP3–WP7 da fare | verifica 2026-10-30 |

**Comandi base** (con venv attiva):

```bash
source .venv/bin/activate
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py test blog.tests.ClassName.test_name
python manage.py runserver
```

---

## 3. Dashboard di avanzamento

| Fase | Stato | Avanzamento | Dipende da |
|---|---|---|---|
| **1. Fondamenta + blog leggibile** | `[~]` | 2/7 WP · 11/33 task | — |
| **2. Account e dashboard** | `[ ]` | 0/4 obiettivi | Fase 1 |
| **3. Workflow editoriale** | `[ ]` | 0/4 obiettivi | Fase 2 |
| **4. Robustezza e delivery** (condizionale) | `[-]` | 0/4 obiettivi | Fase 3 + cambio target |
| **5. Hardening** (opzionale) | `[-]` | 0/4 obiettivi | Fase 4 |

**Stato attuale:** WP1–WP2 completati; si prosegue con WP3 dopo verifica.

---

## 4. Decisioni bloccate

| Tema | Decisione |
|---|---|
| Target | Demo locale. Niente Postgres, Docker o deploy in Fase 1. |
| Autore post | FK a `User`, non campo testuale. |
| Post esistenti | Tutti assegnati all'utente `username="user"`. |
| Pubblicazione | `status` (`draft`/`published`) + `published_at`. |
| Dati esistenti | `is_public=True` → `published` (incluso il post "Draft", che oggi è pubblico). |
| Email | Backend console in dev; SMTP configurabile via env in futuro. |
| DB in git | Untrack + nuovo commit; `SECRET_KEY` ruotata. Vecchia copia resta nella storia (repo non condiviso). |
| Dati demo | Management command `seed_demo` idempotente + fixture sanificata. |
| UI | Inglese, come oggi. Home: hero breve + ultimi post. |
| Contatti | Persistenza DB + email console + honeypot. |
| Test | Flussi critici con assert reali, non solo smoke. |
| Gestione post | Solo Django admin. Nessuna UI di authoring. |
| Scope Fase 1 | Include reset password e persistenza contatti (già previsti qui, non in Fase 2/3). |

**Decisione risolta:** `.env` viene caricato automaticamente da `settings.py`
con un loader stdlib; nessuna dipendenza aggiuntiva. `.env` resta gitignored e
`.env.example` documenta la variabile richiesta.

---

## 5. Definition of Done — Fase 1

La Fase 1 è chiusa solo se tutte le condizioni sono vere:

- [ ] `python manage.py check` senza errori.
- [ ] `python manage.py makemigrations --check --dry-run` → “No changes detected”.
- [ ] `python manage.py test` verde, con assert sui flussi critici.
- [ ] Nessun 500 su modifica profilo: né anonimo né utenti senza profilo.
- [ ] Bozze invisibili da home, ricerca e URL diretto.
- [ ] Contatto salvato nel DB + email in console + honeypot funzionante.
- [ ] Reset password completo funzionante.
- [ ] Titoli duplicati non causano 500.
- [x] `git ls-files` non include `db.sqlite3` né `.env`.
- [ ] Un clone pulito si avvia e si popola con `seed_demo`.
- [ ] Creato `README.md` e aggiornato `AGENTS.md` con setup e comandi.

---

## 6. Fase 1 — Fondamenta + blog leggibile

**Obiettivo:** eliminare i rischi immediati e rendere il blog realmente
leggibile, ricercabile e popolabile, senza regressioni.

**Stima:** 2–3 giorni. **Stato:** `[~]`

### WP1 — Igiene git e segreti

**Obiettivo:** nessun dato utente o segreto nei commit futuri.
**Dipendenze:** nessuna. **Stato:** `[x]`

- [x] Fare un backup locale di `db.sqlite3` (es. `db.sqlite3.bak`) prima di ogni migrazione.
- [x] `git rm --cached db.sqlite3`; aggiungere `db.sqlite3` e `*.bak` a `.gitignore`; commit.
- [x] Leggere `SECRET_KEY` da `DJANGO_SECRET_KEY`; creare `.env.example` senza valori reali.
- [x] Generare una nuova chiave e invalidare le sessioni esistenti.
- [x] Verificare che `git ls-files` non contenga DB, `.env` o backup; commit finale.

**Accettazione:** `git ls-files` pulito; il progetto parte con la chiave da env;
nessuna sessione vecchia resta valida.

### WP2 — Modello contenuti

**Obiettivo:** modello di pubblicazione esplicito e autori integri.
**Dipendenze:** WP1 (backup). WP5 dipende da WP2. **Stato:** `[x]`

- [x] Aggiungere `status` con choices `draft`/`published` e default `draft`.
- [x] Introdurre `created_at` e `published_at`; migrare da `published` (i post pubblicati ricevono il timestamp).
- [x] Sostituire `author` con FK `User` (`on_delete=PROTECT`, `related_name="posts"`); data migration verso `username="user"` (creare l'utente se assente).
- [x] Aggiungere `Post.get_absolute_url()`, indice su `status`/`published_at`, ordering `-published_at`.
- [x] Centralizzare lo slug in `Post.save()` con suffisso anti-collisione; rimuovere l'override fragile da `PostAdmin`.
- [x] Applicare e testare le migrazioni su una **copia** del DB, mai solo sull'originale.

**Accettazione:** migrazione applicata senza perdita dati; titoli duplicati
producono slug univoci; nessun post senza autore.

### WP3 — Auth e profili

**Obiettivo:** eliminare i 500 e completare il recupero password.
**Dipendenze:** WP1. Indipendente da WP2.

- [ ] Rendere idempotente il segnale profilo con `get_or_create`; rimuovere `instance.profile.save()` incondizionato.
- [ ] Data migration che crea i profili mancanti (`user` e `Bob`).
- [ ] Aggiungere `@login_required` a `edit_profile_view` e messaggio di successo dopo il salvataggio.
- [ ] Implementare reset password completo: 4 URL + template `registration/` + email console.
- [ ] Test: anonimo → redirect; utente senza profilo → modifica OK; signup → profilo creato; reset invia email e cambia password (`mail.outbox`).

**Accettazione:** tutti gli utenti esistenti possono modificare il profilo;
flusso reset completo verde nei test.

### WP4 — Contatti

**Obiettivo:** nessun messaggio perso e antispam minimo.
**Dipendenze:** WP1. Indipendente da WP2/WP3.

- [ ] Creare `ContactMessage` (nome, email, messaggio, creato il, letto) + migrazione + admin.
- [ ] `contact_view`: salva, invia email a `DEFAULT_FROM_EMAIL`, redirect a `contact_thanks`.
- [ ] Aggiungere honeypot (`website` nascosto): se compilato, redirect a thanks senza salvare/inviare.
- [ ] Test: persistenza, email in outbox, honeypot ignorato, validazione `min_length`.

**Accettazione:** contatto valido → record + email; bot → nessun record;
form invalido → nessun effetto collaterale.

### WP5 — Blog pubblico

**Obiettivo:** un visitatore anonimo legge e cerca i soli post pubblicati.
**Dipendenze:** WP2. WP4 non blocca.

- [ ] Home con hero breve + lista post pubblicati, paginazione (6/pagina), stato vuoto.
- [ ] Dettaglio `/posts/<slug>/`: solo pubblicati, 404 per draft; incremento viste atomico con `F()`.
- [ ] Ricerca con `Q` su titolo/contenuto, solo pubblicati, link reali al dettaglio, paginazione.
- [ ] Partial riutilizzabile per le card e navbar aggiornata.
- [ ] Rimuovere `accounts/templates/accounts/logout.html` (vuoto e non usato); `thanks` ora è collegato.
- [ ] Test: index esclude draft; dettaglio 404; viste incrementate; ricerca filtrata e link corretti.

**Accettazione:** home, dettaglio e ricerca mostrano solo contenuti pubblicati;
i link funzionano; le viste crescono solo sul dettaglio.

### WP6 — Dati demo

**Obiettivo:** progetto riproducibile da clone.
**Dipendenze:** WP2.

- [ ] Management command `seed_demo` idempotente: utente autore `user` (password inutilizzabile), 5 post pubblicati, 1 draft.
- [ ] Fixture sanificata senza hash password né sessioni.
- [ ] Test: esecuzione su DB vuoto crea i dati attesi e non duplica al secondo run.

**Accettazione:** `seed_demo` su DB vuoto produce lo stato demo; secondo run
non crea duplicati.

### WP7 — Verifica finale

**Obiettivo:** chiudere la fase con prove eseguibili.
**Dipendenze:** WP1–WP6.

- [ ] Eseguire `check`, `makemigrations --check --dry-run` e `manage.py test`; tutto verde.
- [ ] Smoke manuale: home, dettaglio, ricerca, contatti, signup, reset password, modifica profilo, 404 draft.
- [ ] Verificare `git ls-files` e assenza di segreti; controllare `git status`.
- [ ] Creare `README.md` e aggiornare `AGENTS.md` con setup, comandi e stato del progetto.

**Accettazione:** tutti i criteri della sezione 5 soddisfatti e registrati nel
changelog.

---

## 7. Fasi successive

> Queste fasi non sono in scope finché la Fase 1 non è `[x]`. Le stime sono
> indicative e vanno riviste all'apertura della fase.

### Fase 2 — Account e dashboard — `[ ]`

**Obiettivo:** dare valore all'area autenticata.

- [ ] Dashboard con dati utente e “My posts” basata sulla FK autore.
- [ ] Rifiniture signup e profilo (feedback, validazioni, stato vuoto).
- [ ] Test dei flussi account e della dashboard.
- [ ] Aggiornare documentazione e changelog.

**Accettazione:** un utente vede i propri dati e i propri post senza admin.

### Fase 3 — Workflow editoriale — `[ ]`

**Obiettivo:** gestire pubblicazione e contatti senza interventi manuali sul DB.

- [ ] Admin actions publish/unpublish e anteprima bozze per lo staff.
- [ ] Gestione inbox contatti (letto/archiviato) e filtri admin.
- [ ] Eventuale ruolo editor con permessi minimi.
- [ ] Test su azioni admin e permessi.

**Accettazione:** lo staff pubblica/ritira post e gestisce i messaggi da admin
senza modificare il codice o il DB.

### Fase 4 — Robustezza e delivery — `[-]` (condizionale)

**Attivare solo se il target smette di essere demo locale.**

- [ ] Split settings `base/dev/prod`; `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL` da env.
- [ ] Security settings di produzione e `check --deploy` pulito.
- [ ] CI: `check`, `makemigrations --check`, `test`, `pip-audit`.
- [ ] README di deploy, statici (WhiteNoise/SRI), logging, 404/500 personalizzate.

**Accettazione:** deploy riproducibile senza segreti nel repo; CI verde.

### Fase 5 — Hardening — `[-]` (opzionale)

- [ ] Rate limiting login e contatti.
- [ ] CSP e header di sicurezza.
- [ ] Backup/retention e monitoraggio errori.
- [ ] Accessibilità e, se serve, ricerca full-text.

**Accettazione:** definita all'apertura della fase in base ai rischi residui.

---

## 8. Rischi e mitigazioni

| Rischio | Gravità | Stato | Mitigazione |
|---|---|---|---|
| Vecchio DB con hash/sessioni nella storia git | Media | Accettato | Repo non condiviso; `SECRET_KEY` ruotata; rewrite valutabile in futuro |
| Migrazione dati distruttiva | Media | Da gestire | Backup + test su copia prima di applicare |
| `DEBUG=True`, cookie non secure | Bassa in locale | Accettato | Documentato; chiuso solo in Fase 4 |
| Nessun rate limiting | Bassa in locale | Accettato | Fase 5 |
| Bootstrap CDN senza SRI | Bassa | Accettato | Vendorizzazione in Fase 4 |
| Segreti esportati a mano in `.env` | Bassa | Aperto | `.env.example` + `.gitignore`; valutare auto-load |

---

## 9. Verifica

**Automatica (obbligatoria a fine WP):**

```bash
source .venv/bin/activate
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

**Manuale (fine Fase 1):**

- [ ] `/` mostra hero + soli post pubblicati paginati.
- [ ] Un draft non è raggiungibile da home, ricerca o URL diretto.
- [ ] Il dettaglio incrementa `views` di 1.
- [ ] Ricerca con termine presente/assente e link funzionanti.
- [ ] Contatto valido → record in admin + email in console.
- [ ] Honeypot compilato → nessun record.
- [ ] Signup → login → modifica profilo → reset password.
- [ ] `/accounts/profile/edit/` da anonimo → redirect al login (302, non 500).
- [ ] `seed_demo` su DB vuoto e secondo run senza duplicati.

**Criterio di chiusura:** nessun task aperto in Fase 1, DoD soddisfatta,
changelog aggiornato.

---

## 10. Changelog

| Data | Versione | Modifica |
|---|---|---|
| 2026-10-29 | 1.0 | Creazione del documento canonico; incorporate le decisioni del Q&A e il perimetro Fase 1. |
| 2026-10-30 | 1.1 | WP1 completato: DB e backup untracked, `SECRET_KEY` da `.env`, sessioni invalidate. |
| 2026-10-30 | 1.2 | WP2 completato: `status`, `created_at`/`published_at`, autore FK, slug centralizzato, 8 test; migrazioni verificate su copia (incluso rollback). |

---

## 11. Fuori scope

Commenti, like, newsletter, API REST/SPA, custom user model, Postgres/Docker,
i18n, UI di authoring, notifiche realtime. Non aggiungere queste voci senza
aggiornare esplicitamente questo piano e le relative fasi.
