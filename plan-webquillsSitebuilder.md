Plan: WebQuills Specification & Implementation

TL;DR — Produce a developer-ready specification and implementation plan that maps README features to concrete models, service-layer functions, views, templates, background tasks, and tests. This plan breaks work into implementable steps with file and symbol references so tasks can be converted to GitHub issues and handed to developers.

Steps
1. Define domain models: add `StaticSite`, `DraftBranch`, and `ContentFileMetadata` in `sitebuilder/models.py`.
2. Add service layer modules: `sitebuilder/services/git_provider`, `sitebuilder/services/site`, `sitebuilder/services/content`, `sitebuilder/services/drafts` with clear interfaces.
3. Implement provider clients: `sitebuilder/services/git_provider/github.py` (PyGitHub) and `sitebuilder/services/git_provider/gitea.py` (requests/pygitea) implementing shared `GitProviderClient` interface.
4. Build high-level flows: implement `SiteService.import_site_from_repo`, `SiteService.create_site_from_template`, `ContentService.*` and `DraftService.*` in respective modules.
5. Add views, templates, and forms: implement site import/create UIs, content tree UI, content-edit form with front-matter panel, drafts list UI, publish/discard actions; wire URLs in `sitebuilder/urls.py`.
6. Add background tasks: `sitebuilder/tasks.py` (Celery/django-rq) for rebase/polling/merge/cleanup and integrate with `DraftService`.
7. Add tests: unit tests for services and provider clients (mocking network), integration tests for views and workflows in `tests/` mirroring README flows.

Further Considerations
1. Provider choice: Github via PyGitHub is primary (per README); design `GitProviderClient` interface to allow Gitea/GitLab later.
2. Token storage: leverage allauth's `SocialToken` model for OAuth tokens; ensure secure storage and refresh handling.
3. Error handling: robust error handling in service layer for network/API errors, with user-friendly messages in views.
4. Accessibility: ensure all templates and UIs follow accessibility best practices (keyboard navigation, ARIA roles).

Specification (by feature) — models, services, views, templates, and detailed service actions

Feature 1 — Authentication (existing)
- Models: none required (uses allauth).
- Files to update: Add setting `SOCIALACCOUNT_STORE_TOKENS = True` to ensure tokens are stored on socialaccount connect.
- Views/Templates: use existing allauth templates in `sitebuilder/templates/account/` and `sitebuilder/templates/allauth/`. Uncomment social login buttons in `account/base.html`.

Feature 2 — Import site from Git provider
- Models:
  - `StaticSite` fields:
    - `id`: Django's auto field
    - `name`: Supplied by user or parsed from Hugo config
    - `owner` (FK to User)
    - `provider` (choice): Allauth provider (supplies keys and base urls)
    - `provider_repo_owner` (FK to SocialAccount): provides ID & details of provider user/organization owning the repo. [GitHub best practices](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/best-practices-for-creating-a-github-app#use-the-durable-unique-id-to-store-the-user) advises storing IDs rather than usernames (usernames can change and be reassigned).
    - `provider_repo_name` (str): for display purposes only
    - `provider_repo_id` (int/str): unique repo ID from provider API
    - `default_branch` (str, default "main")
    - `metadata` (JSON)
    - `date_created`
    - `date_modified`
  - User's repository credentials are stored by Allauth in `allauth.socialaccount.models.SocialToken`. The `token` field contains the access token. The `token_secret` field contains the refresh token. The `expires_at` field contains the expiration time. Expired tokens should be refreshed automatically.
- Service layer:
  - `sitebuilder/services/site.py` — `import_site_from_repo(repo_url, user, grant_write=False)`:
    - Parse `repo_url` to provider/owner/repo.
    - Resolve user's `SocialToken` for provider.
    - Use `git_provider = GitProviderFactory.for_provider(provider, credential)` to create client.
    - Call `git_provider.get_repo(owner, repo)` → validate repo access.
    - Read Hugo config:
      - Hugo config can be a single file in YAML, TOML, or JSON format, or a directory tree of such files. Hugo also supports environment-specific configuration.
      - For our purposes, we only need to extract basic site metadata (title, baseURL, languageCode, theme).
      - For first implementation, just look for `(hugo|config).(yaml|yml|toml|json)` in the root of the default branch.
      - Use `git_provider.get_file(repo, path, ref=default_branch)` to read config file.
      - Parse config file using appropriate parser (PyYAML, toml, json).
      - Future versions, MAYBE: Would it be easier to simply clone the repo locally and run `hugo config` to get the effective configuration? Would require git CLI and Hugo CLI installed on server. (Clone with `--depth 1 --filter=blob:none --no-checkout` to minimize data transfer. Then use `sparse-checkout` to get only config files.)
    - Create `StaticSite` record with parsed metadata and repo info.
    - If `grant_write=True`, create/update repository collaborator permission via `git_provider.add_collaborator(repo, user_account)`.
    - Return `StaticSite` instance and metadata.
  - Libraries: `PyGithub` (Github), `requests` or pygitea for Gitea.
- Views & Templates:
  - View: SiteListView (ListView) at `/sites/` — list user's imported sites.
  - View: SiteDetailView (DetailView) at `/sites/<id>/` — show site metadata and links to content tree.
  - View: SiteUpdateView (FormView) at `/sites/<id>/edit/` — form to update site metadata (name, default branch).
  - View: `ImportSiteView` (FormView) at `/sites/import/`. On POST, calls `SiteService.import_site_from_repo()`. On success, redirect to SiteUpdateView.
  - Form: `ImportSiteForm` — fields for repo URL and options.
  - On successful import, redirect to SiteUpdateView displaying prefilled metadata from config with edit form.
  - Template: `sitebuilder/templates/sites/import.html` — form for repo URL and options, display prefilled metadata from config with edit form.
  - Template: `sitebuilder/templates/sites/list.html` — list of user's imported sites with links to manage.
  - Template: `sitebuilder/templates/sites/detail.html` — site detail view with metadata and links to content tree.
  - Template: `sitebuilder/templates/sites/update.html` — form to update site metadata.
- Tests:
  - Unit tests: mock `GitProviderClient` to assert parsing and record creation.
  - Integration: use test repo fixtures.

Feature 3 — Create new site in provider
- Services:
  - `SiteService.create_site_from_template(site_spec, user)`:
    - Use `git_provider.create_repo(name, private, description, auto_init=False)`.
    - Create bootstrap commit: upload Hugo skeleton files via `git_provider.put_file()` iterating template files.
    - Set branch protections if needed.
    - Create `StaticSite` record.
  - Complexity: handle repo creation failures, template zips, and repository initial commit with correct directory structure.
  - Libraries: `PyGithub.Repository.create_from_template` (if using template repo) or iterative `create_file`.
- Views/Templates:
  - `CreateSiteView` (FormView) at `/sites/create/`.
  - Template: `sitebuilder/templates/sites/create.html`.
- Tests:
  - Mock provider client to assert repo creation and file uploads.

Feature 4 — List site content (content tree)
- Models:
  - `ContentFileMetadata` (site FK, path, last_commit_sha, is_page_bundle boolean).
- Services:
  - `ContentService.list_content_tree(site, ref='main')`:
    - Use `git_provider.get_tree(repo, ref)` -> recursive listing.
    - Convert to structured tree nodes, detect page bundles (directories with index.md/_index.md).
    - Fetch quick front matter snippet for each page via `git_provider.get_file()` for first N bytes.
  - Complexity: pagination for large repos, caching of tree in DB or Redis.
- Views/Templates:
  - `ContentTreeView` (ListView) at `/sites/<id>/content/`.
  - Template: `sitebuilder/templates/sites/content_tree.html` — keyboard accessible tree with selection actions.
- Tests:
  - Unit tests for `list_content_tree` with mocked repo trees.

Feature 5 — Edit content (Draft)
- Models:
  - `DraftBranch` fields: `id`, `site` (FK), `branch_name`, `created_by` (FK), `pr_number` (nullable), `status` (enum: draft, published, discarded), `created_at`, `updated_at`.
- Services:
  - `ContentService.load_content_file(site, path, ref)`:
    - `git_provider.get_file(repo, path, ref)` → parse front matter and body.
  - `ContentService.save_file_as_draft(site, path, front_matter, body, user)`:
    - Ensure draft branch exists: if not, `git_provider.create_branch(repo, base_ref=site.default_branch, new_branch_name=generate_name(user, path))`.
    - Reconstruct file content: front matter + body.
    - `git_provider.put_file(repo, path, content, message='Edit via WebQuills', branch=draft_branch)`.
    - Create or update `DraftBranch` record linking branch and optionally create/refresh PR via `DraftService.create_draft_pr()`.
  - `DraftService.create_draft_pr(site, branch_name, title, body)`:
    - Call `git_provider.create_pull_request(repo, head=branch, base=default_branch, title, body, draft=True)`.
    - Save `pr_number` on `DraftBranch`.
  - Complexity: handle merge conflicts, branch naming collisions, pushing binary/media files (use separate upload endpoints).
  - Libraries: PyGitHub `Repository.create_git_ref`, `Repository.create_file`, `Repository.get_contents`, `create_pull`, `edit`.
- Views/Templates:
  - `ContentEditView` (FormView) at `/sites/<id>/content/<path>/edit/`.
  - Template: `sitebuilder/templates/sites/edit.html` with two panels (metadata and content). Accessible keyboard-first UI, include preview.
- Tests:
  - Unit tests for `save_file_as_draft` mocking provider push and PR creation.
  - Integration tests for editing flow with simulated git provider.

Feature 6 — Continue working (Draft listing and management)
- Services:
  - `DraftService.list_drafts(site)` — query `DraftBranch` records and hydrate PR/check status from provider (`git_provider.get_pull_request(pr_number)`).
  - `DraftService.rebase_branch(draft, base_ref)`:
    - Option A: use provider's merge API to rebase; Option B: perform git rebase via a temporary clone (complex, may require server-side git).
    - Initially implement as: fast-forward / merge from base into branch using `git_provider.merge` with `merge_method='rebase'` if provider supports; otherwise alert user.
  - `DraftService.publish_draft(draft, user)`:
    - Rebase, ensure checks pass: poll `git_provider.get_check_runs(pr)` until success or timeout.
    - `git_provider.merge_pull_request(repo, pr_number)`.
    - Update `DraftBranch.status` to `published`.
  - `DraftService.discard_draft(draft, user)`:
    - Close PR if exists (`git_provider.update_pull_request(pr_number, state='closed')`).
    - Rename branch to `waste/<original>` using `git_provider.rename_branch(repo, old, new)` or create new branch + delete old (provider-dependent).
    - Set `status = discarded` and set `discarded_at`.
  - Complexity: provider API differences around rebase/rename; consider server-side git operations if needed.
- Views/Templates:
  - `DraftListView` at `/sites/<id>/drafts/` with Edit/Publish/Discard actions.
  - Partial templates for draft row in tree.
- Tests:
  - Unit tests for draft lifecycle service (mock PR check runs and merging).

Feature 7 — Publish content
- Services:
  - See `DraftService.publish_draft` above.
  - Background task `Tasks.wait_for_checks_and_merge(pr_number, timeout)`:
    - Poll `git_provider.get_check_runs(pr)` every N seconds up to timeout.
    - If success, call `git_provider.merge_pull_request`.
    - If fail, record failure and notify user (via DB notification or email).
  - Libraries: PyGitHub `PullRequest.get_combined_status` or `get_check_runs`.
- Views/Templates:
  - Publish action triggers POST to `DraftPublishView` that queues background task and shows progress UI (poll via HTMX).
- Tests:
  - Mock check-run polling and merge success/failure; assert state transitions.

Feature 8 — Discard Draft
- Services:
  - See `DraftService.discard_draft` above.
  - Background cleanup `Tasks.cleanup_discarded_branches(older_than_days)` to fully delete discarded branches after retention period.
- Views/Templates:
  - Confirm discard modal in UI (templated).
- Tests:
  - Test discard sets status and branch rename; cleanup task deletes branches after retention.

Cross-cutting components

A. Git Provider Interface (sitebuilder/services/git_provider/__init__.py)
- Interface methods:
  - `get_repo(owner, repo)`
  - `create_repo(name, private, template=None)`
  - `get_tree(repo, ref)`
  - `get_file(repo, path, ref)`
  - `put_file(repo, path, content, message, branch)`
  - `create_branch(repo, base_ref, new_branch_name)`
  - `rename_branch(repo, old_name, new_name)` (if supported)
  - `create_pull_request(repo, head, base, title, body, draft=True)`
  - `get_pull_request(repo, pr_number)`
  - `merge_pull_request(repo, pr_number, merge_method='merge')`
  - `get_check_runs(repo, ref or pr)`
  - `add_collaborator(repo, username, permission)`
- Implementation details for GitHub (github.py):
  - Use PyGitHub: `Github(token)`, `get_repo(f"{owner}/{repo}")`, `repo.get_contents(path, ref)`, `repo.create_file(path, message, content, branch)`, `repo.create_git_ref(ref='refs/heads/<name>', sha=base_commit.sha)`, `repo.create_pull(title, body, head, base, draft=True)`, `pr.merge()`, `pr.get_checks()` or `pr.get_combined_status()`.
  - Handle rate limits via catching `GithubException.RateLimitExceededException`.
  - Use retries and exponential backoff for transient errors.
- Implementation details for Gitea (gitea.py):
  - Use `requests` to call Gitea API endpoints for contents/branches/pulls.
  - Keep helpers to translate to same interface.

B. Background Tasks (sitebuilder/tasks.py)
- Functions:
  - `rebase_and_merge(draft_id)` — performs rebase (or merge) and merges PR when checks pass.
  - `poll_pr_checks(pr_number, timeout, success_callback, fail_callback)` — poll provider check runs.
  - `cleanup_discarded_branches()` — scheduled.

C. DB Migrations and Admin
- Add migrations for new models and basic admin pages in `sitebuilder/admin.py` for site/draft/credential management.

D. Frontend templates & accessibility
- Templates to add:
  - `sitebuilder/templates/sites/import.html`
  - `sitebuilder/templates/sites/create.html`
  - `sitebuilder/templates/sites/list.html`
  - `sitebuilder/templates/sites/content_tree.html`
  - `sitebuilder/templates/sites/edit.html`
  - `sitebuilder/templates/sites/drafts.html`
- Accessibility: keyboard navigation, ARIA roles, alt text, form labels.

E. Tests & CI
- Add unit tests for all service functions using pytest or Django TestCase with mocks (use VCR/requests-mock for provider tests).
- Add integration tests for main flows using Django TestCase and mock provider API.
- Update `tox.ini` and CI to run tests; add test fixtures for repo contents.

Example Issue Breakdown (convertible to GitHub issues)
- Models: Create `StaticSite` and migrations.
- Services: Add provider interface and GitHub implementation (PyGitHub).
- Services: Implement `SiteService.import_site_from_repo`.
- UI: Implement import site form & template.
- Services: Implement `SiteService.create_site_from_template`.
- UI: Implement create site form & template.
- Services: Implement `ContentService.list_content_tree`.
- UI: Implement content tree view & template.
- Services: Implement `ContentService.load/save` and `DraftService.create_pr`.
- UI: Implement content editor UI with metadata panel.
- Background: Implement `tasks.rebase_and_merge`.
- Tests: Add unit and integration tests per service and views above.
- Admin: Register models in Django admin.
- Security: Implement token encryption and storage policy.
- Docs: Update README with developer setup and API contracts.

If you want, I can now convert the above into a prioritized list of GitHub issues with titles, descriptions, acceptance criteria, and suggested labels and estimates. Which format would you prefer?
