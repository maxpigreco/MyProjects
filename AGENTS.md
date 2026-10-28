# AGENTS.md

Django 5.2.3 demo site: user auth, profiles, contact form, and post search.
Settings package is `MyProjects/`; apps are `blog` (mounted at `/`) and
`accounts` (mounted at `/accounts/`).

## Setup

- Use the local `.venv` (Python 3.12, gitignored); dependencies are pinned in
  `requirements.txt` (Django 5.2.3). Activate it with
  `source .venv/bin/activate`, or call `.venv/bin/python` directly.
- The default `python` (pyenv 3.15.1) does not have Django installed; always
  use the venv. Recreate it with:
  `/usr/bin/python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
- No README or CI. `db.sqlite3` ships with existing data (three users, one
  superuser) and all migrations applied. Do not delete or reset it.
- Ignore `desktop.ini` and `*:Zone.Identifier` files throughout the tree; they
  are Windows metadata, not source.

## Commands

```bash
python manage.py runserver
python manage.py check
python manage.py makemigrations --check --dry-run    # verify no pending migrations
python manage.py test blog.tests.ClassName.test_name  # single test
python manage.py createsuperuser
```

Test files are placeholders: `manage.py test` currently runs 0 tests.

## Conventions and gotchas

- `MyProjects/settings.py` is development-only: `DEBUG = True`, hardcoded
  `SECRET_KEY`, SQLite, empty `ALLOWED_HOSTS`.
- Root `templates/base.html` (Bootstrap 5 via CDN) is the shared layout. App
  templates live under `<app>/templates/<app>/`.
- URL names are global (no namespaces): refer to `index`, `login`, `signup`,
  `logout`, `dashboard`, `profile`, `edit_profile`, `contact`, `search`.
  `LOGIN_URL = "login"` and `LOGIN_REDIRECT_URL = "dashboard"`.
- `accounts.Profile` is created/updated by a `post_save` signal on `User`.
  Views touching `request.user.profile` must be login-protected;
  `accounts.views.edit_profile_view` currently lacks `@login_required` and
  errors for anonymous users.
- `blog.admin.PostAdmin.save_model` always overwrites `slug` with
  `slugify(title)`, so the `prepopulated_fields` value is discarded. `slug` is
  unique, so posts with identical titles raise an integrity error.
- `blog.views.search_view` queries all `Post` rows without filtering
  `is_public`.
- `accounts/templates/accounts/logout.html` is unused: logout uses a
  `LogoutView` subclass that redirects to the `login` URL.
