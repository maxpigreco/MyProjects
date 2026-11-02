# AGENTS.md

Django 5.2.3 demo site: user auth, profiles, contact form, and post search.
Settings package is `MyProjects/`; apps are `blog` (mounted at `/`) and
`accounts` (mounted at `/accounts/`).

Planning and progress: `PLAN.md` is the single source of truth for roadmap,
decisions, task status, and acceptance criteria. Update its checkboxes and
changelog when work is completed.

## Setup

- Use the local `.venv` (Python 3.12, gitignored); dependencies are pinned in
  `requirements.txt` (Django 5.2.3). Activate it with
  `source .venv/bin/activate`, or call `.venv/bin/python` directly.
- The default `python` (pyenv 3.15.1) does not have Django installed; always
  use the venv. Recreate it with:
  `/usr/bin/python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
- Secrets: `DJANGO_SECRET_KEY` is read from `.env`, which is auto-loaded by
  `settings.py` and gitignored. Copy `.env.example` to create it; never commit
  `.env`.
- No CI. `README.md` is a short stub to be rewritten in WP7. `db.sqlite3` is
  local and gitignored (it contains the demo data); a fresh clone must run
  migrations before use. Do not delete or reset the local DB.
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

`blog/tests.py` covers the `Post` model and admin (10 tests);
`accounts/tests.py` is still a placeholder.

## Conventions and gotchas

- `MyProjects/settings.py` is development-only: `DEBUG = True`, `SECRET_KEY`
  from `.env`, SQLite, empty `ALLOWED_HOSTS`.
- Root `templates/base.html` (Bootstrap 5 via CDN) is the shared layout. App
  templates live under `<app>/templates/<app>/`.
- URL names are global (no namespaces): refer to `index`, `login`, `signup`,
  `logout`, `dashboard`, `profile`, `edit_profile`, `contact`, `search`.
  `LOGIN_URL = "login"` and `LOGIN_REDIRECT_URL = "dashboard"`.
- `accounts.Profile` is created/updated by a `post_save` signal on `User`.
  Views touching `request.user.profile` must be login-protected;
  `accounts.views.edit_profile_view` currently lacks `@login_required` and
  errors for anonymous users. It also needs a profile: `user` and `Bob` have
  none until the WP3 data migration runs.
- `blog.models.Post.save()` generates the slug (unique, with `-2`/`-3`
  suffixes) and sets `published_at` on first publication. The admin keeps
  `slug` read-only, so changing a title keeps the URL and duplicate titles are
  allowed.
- `blog.views.search_view` queries all `Post` rows without filtering
  `status="published"`.
- `Post.get_absolute_url()` targets `post_detail`, added in WP5; until then the
  admin uses `view_on_site = False`.
- `accounts/templates/accounts/logout.html` is unused: logout uses a
  `LogoutView` subclass that redirects to the `login` URL.
