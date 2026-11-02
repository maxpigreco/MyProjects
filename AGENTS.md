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
- No CI. `README.md` documents the project, system requirements and setup.
  `db.sqlite3` is local and gitignored (it contains the demo data); a fresh
  clone must run migrations before use. Do not delete or reset the local DB.
- Ignore `desktop.ini` and `*:Zone.Identifier` files throughout the tree; they
  are Windows metadata, not source.

## Commands

```bash
python manage.py runserver
python manage.py check
python manage.py makemigrations --check --dry-run    # verify no pending migrations
python manage.py test blog.tests.ClassName.test_name  # single test
python manage.py seed_demo                           # refresh demo content
python manage.py createsuperuser
```

`blog/tests.py` covers the `Post` model and admin, the public home/detail/search
views, contact messages and the `seed_demo` command; `accounts/tests.py` covers
profiles, signup and password reset (44 tests total).

## Conventions and gotchas

- `MyProjects/settings.py` is development-only: `DEBUG = True`, `SECRET_KEY`
  from `.env`, SQLite, empty `ALLOWED_HOSTS`, console email backend.
  `CONTACT_EMAIL` comes from env with a `contact@example.com` default.
- Root `templates/base.html` (Bootstrap 5 via CDN) is the shared layout. App
  templates live under `<app>/templates/<app>/`.
- URL names are global (no namespaces): refer to `index`, `post_detail`,
  `login`, `signup`, `logout`, `dashboard`, `profile`, `edit_profile`,
  `contact`, `search`, and `password_reset`, `password_reset_done`,
  `password_reset_confirm`, `password_reset_complete`. Reset templates live in
  `templates/registration/`. `LOGIN_URL = "login"` and
  `LOGIN_REDIRECT_URL = "dashboard"`.
- `accounts.Profile` is ensured by a `post_save` signal on `User`
  (`get_or_create`, so existing bios are never overwritten).
  Views touching `request.user.profile` must be login-protected
  (`edit_profile_view` is).
- `blog.models.Post.save()` generates the slug (unique, with `-2`/`-3`
  suffixes) and sets `published_at` on first publication. The admin keeps
  `slug` read-only, so changing a title keeps the URL and duplicate titles are
  allowed.
- Public views (`index_view`, `post_detail_view`, `search_view`) filter
  `status="published"` and use `select_related("author")`; all paginate at
  `POSTS_PER_PAGE = 6`. Drafts 404 on the detail URL.
- `post_detail_view` increments `views` with `F("views") + 1` and refreshes the
  field before rendering. The author shows `author_name` with a fallback to
  `author.username`.
- `Post.get_absolute_url()` targets `post_detail`; the admin uses
  `view_on_site = True`.
- Post cards and pagination are shared partials:
  `blog/templates/blog/_post_card.html` and `_pagination.html`.
- `seed_demo` creates or refreshes the demo user `user` (unusable password,
  no staff flags), its profile and 6 posts keyed by slug. It is idempotent and
  overwrites edits to demo posts. `blog/fixtures/demo.json` is a sanitized
  snapshot for `loaddata demo` on an empty DB only.
- Contact submissions are stored in `blog.ContactMessage` and emailed to
  `CONTACT_EMAIL` (console backend in dev). The hidden `website` field is a
  honeypot: when filled, the view redirects to thanks without saving or
  sending. Email errors are logged and never lose the stored message.
- `ContactMessageAdmin` keeps the message content read-only; only `is_read` is
  editable.
- Logout uses a `LogoutView` subclass that redirects to the `login` URL; there
  is no logout template.
