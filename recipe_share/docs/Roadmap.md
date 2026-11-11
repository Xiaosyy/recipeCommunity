a# Recipe Sharing Community System — Development Roadmap

## Execution rule
Complete and test one phase before beginning the next major phase. Each phase below has objectives, tasks, expected outputs, dependencies, and a completion checklist. Browser/API checks may be automated or manual, but phase completion requires recorded evidence.

## Phase 1: Project initialization and environment setup
### Objectives
Establish the Flask application, configuration model, dependency manifest, development workflow, and repository structure.

### Tasks
- Create the application factory in `recipeshare/__init__.py`.
- Add environment configuration and `.env.example` without secrets.
- Define application extension and database connection initialization.
- Create the modular directory structure from `SystemPlan.md`.
- Add dependencies for Flask, MySQL, password hashing, file handling, and testing.
- Add base public/authenticated layouts, shared CSS/JavaScript entry points, application error pages, and initial RecipeShare component partials.
- Establish SPA view contracts and progressive-enhancement entry points without hardcoding dynamic business records.
- Configure development logging and ignore generated, secret, upload, and virtual-environment files.
- Add README setup, test, and run instructions.

### Expected outputs
Runnable Flask application, development configuration, documented installation steps, base page layout, dependency manifest, and an initial smoke test.

### Dependencies
Approved project documentation and a local MySQL installation or approved test database.

### Completion checklist
- [x] Application starts without error.
- [x] Environment variables and missing required secrets are handled safely.
- [x] Unit/integration test runner executes.
- [x] Base template renders and shared assets load.
- [ ] Database connection configuration is tested.
- [x] No secrets or virtual environment files are tracked.

## Phase 2: Database design and configuration
### Objectives
Create the normalized MySQL schema and database access utilities.

### Tasks
- Create `database/schema.sql` with tables, keys, constraints, indexes, and seed roles/categories.
- Add migrations or an approved versioned migration mechanism.
- Implement pooled/request-scoped connections and parameterized repository helpers.
- Implement roles, users, profiles, recipes, menus, ingredients, categories, and supporting join tables.
- Add community, media, moderation, notification, location, and AI-generation tables.
- Implement transactions and rollback behavior for related writes.
- Seed only non-sensitive development/demo data.

### Expected outputs
Executable schema, migration history or equivalent scripts, seed scripts, database models/repositories, and connection tests.

### Dependencies
Phase 1 application configuration and approved database design in `SystemPlan.md`.

### Completion checklist
- [ ] Schema applies successfully to a clean MySQL database — pending an available MySQL service with administrator/start permissions.
- [x] Foreign keys and uniqueness constraints are defined in the canonical schema.
- [x] Draft and published states are constrained or validated.
- [x] Repository methods use parameterized statements.
- [x] Transaction behavior is centralized in database connection context managers.
- [x] Re-running setup and seed commands is safe and documented.

## Phase 3: Authentication and user roles
### Objectives
Provide secure registration, login/logout, profile/session handling, roles, and ownership checks.

### Tasks
- Implement registration, login, logout, password change, account status, and optional verification/recovery flows.
- Add role decorators and authorization helpers for user/admin access.
- Implement secure password hashing and session cookie configuration.
- Add registration/login/profile validation and CSRF protection.
- Implement profile creation and basic account updates.
- Add authorization tests including ownership and role boundaries.

### Expected outputs
Secure authentication pages, role assignments, profile management, authorization utilities, and authentication tests.

### Dependencies
Phases 1–2.

### Completion checklist
- [x] Passwords are never stored in plaintext.
- [x] Valid and invalid credentials behave correctly.
- [x] Session establishment and logout work.
- [x] Unauthenticated access is blocked appropriately.
- [x] Ownership checking is centralized for owner-only routes.
- [x] Role boundaries are protected by server-side decorators and tested where implemented.

## Phase 4: Shared UI, layout, and SPA foundation
### Objectives
Implement the public shell, authenticated application shell, reusable component library, server-rendered partial architecture, and progressive vanilla-JavaScript SPA behavior shown in the approved UI references.

### Tasks
- Create public and authenticated application layouts with the RecipeShare brand, cream, green, white, and orange visual system.
- Build reusable navigation, sidebar, mobile drawer, search, profile menu, notification, metric, card, table, form, chart, rank-list, alert, loading, empty, modal, and pagination partials.
- Create feature partials for public discovery, recipe/menu cards and details, dashboard, profile, forms, favorites, AI review, and administration views.
- Implement `spa-router.js`, `api-client.js`, shared History API handling, page-title updates, focus/scroll restoration, loading transitions, and pop-state support.
- Add server-backed role-aware navigation and `/api/v1/ui/navigation` plus fragment rendering contracts.
- Ensure direct page navigation, refresh, browser Back/Forward, and no-JavaScript form submission work without the SPA enhancement.
- Source all displayed business content from database-backed services/APIs. Do not keep recipe, category, statistic, chart, ranking, user, or navigation fixture arrays in templates or JavaScript.
- Add responsive desktop/mobile layouts and accessibility checks for shells, forms, navigation, cards, tables, dialogs, and status announcements.

### Expected outputs
Reusable layouts/components, direct-rendered and SPA fragment routes, role-aware navigation, responsive public/authenticated shells, and browser-navigation/JS-fallback tests.

### Dependencies
Phases 1–3 for the application shell; dynamic page content expands through later feature phases.

### Completion checklist
- [ ] Public and authenticated layouts match the approved visual direction and are responsive.
- [ ] No page-sized template or inline feature script duplicates reusable UI.
- [ ] SPA navigation preserves shared layout and works with direct Flask routes.
- [ ] Back/Forward, refresh, loading, error, empty, and unauthorized states pass browser checks.
- [ ] Business data and role-aware navigation are server-derived, not hardcoded in JavaScript.
- [ ] Shared components pass keyboard, focus, label, contrast, and mobile checks.

## Phase 5: User dashboard
### Objectives
Create role-specific dashboards and account-management navigation.

### Tasks
- Implement the authenticated user dashboard.
- Add counts for own recipes, menus, drafts, favorites, notifications, and moderation status where applicable.
- Add recent content and profile sections.
- Implement administrator dashboard skeleton and statistics layout.
- Add empty, loading, and permission-denied states.
- Ensure navigation differentiates end-user and administrator capabilities.

### Expected outputs
Responsive end-user dashboard, administrator shell, profile view/edit forms, and dashboard tests.

### Dependencies
Phases 3–4.

### Completion checklist
- [x] Dashboard only exposes current-user or permitted aggregate data.
- [x] Role-specific navigation is correct.
- [x] Mobile layout is usable.
- [x] Empty states are clear.
- [x] Sidebar modules navigate entirely through SPA content swaps without loading overlays or page animations.
- [x] Dashboard queries are parameterized and tested.
- [x] Authenticated application layout includes a fixed topbar, sidebar, responsive content area, metrics, charts, rankings, and recipe inventory.

## Phase 6: Recipe and menu management
### Objectives
Implement complete authoring, draft, publish, edit, delete, image, ingredient, and menu workflows.

### Tasks
- Build recipe create/edit forms and draft/published transitions.
- Create ingredients, quantities, units, instructions, times, categories, images, and validation.
- Build recipe detail and owner-management views.
- Build menu create/edit forms and select constituent recipes.
- Add menu drafts, publication, own-content listing, and delete workflows.
- Implement image validation, generated names, size limits, and safe storage.
- Write service/repository and HTTP authorization tests.

### Expected outputs
Functional recipe and menu CRUD flows, content status transitions, image uploads, owner dashboards, and workflow tests.

### Dependencies
Phases 2–5.

### Completion checklist
- [ ] Owners can create, edit, publish, draft, and delete their own content.
- [ ] Other users cannot modify owner-only content.
- [ ] Invalid ingredients, quantities, images, and transitions are rejected.
- [ ] Transactions preserve recipe/menu integrity.
- [ ] Draft and published pages follow access rules.
- [ ] Desktop and mobile authoring forms work.

## Phase 7: Recipe discovery and search
### Objectives
Enable community members to browse and find recipes and menus efficiently.

### Tasks
- Implement published-only recipe/menu listing and detail pages.
- Add keyword search over approved content.
- Add category, ingredient, author, location, and sorting filters.
- Implement pagination and stable ordering.
- Add author profile and public content views.
- Add database indexes based on tested search behavior.

### Expected outputs
Discovery pages, reusable cards, search/filter controls, author profiles, pagination, and query tests.

### Dependencies
Phase 6; public content must exist before tests can be meaningful.

### Completion checklist
- [ ] Drafts remain invisible in public discovery.
- [ ] Filters combine without SQL injection or incorrect joins.
- [ ] Pagination does not omit or duplicate records under normal sorting.
- [ ] Empty and invalid filter states are handled.
- [ ] Search page is accessible and responsive.

## Phase 8: Community interactions
### Objectives
Add likes, ratings, comments, favorites, reports, and notifications.

### Tasks
- Implement one-like and one-rating-per-user constraints.
- Add comments with moderation and author controls.
- Add favorites and saved-content views.
- Add reports with reason and optional detail, and prevent duplicate unresolved reports by the same user when policy requires it.
- Add notifications and read-state management.
- Add aggregates and prevent inconsistent counts via transactions or constraints.

### Expected outputs
Community interaction UI/API endpoints, report workflow, notification center, and interaction tests.

### Dependencies
Phases 3, 6, and 7.

### Completion checklist
- [ ] One user cannot create duplicate likes or multiple ratings for the same target.
- [ ] Comment/report validation works on server and client.
- [ ] Reported content is available to moderators without exposing private data broadly.
- [ ] Aggregates and favorite states are correct.
- [ ] Spam and abuse controls are covered by tests.

## Phase 9: Location detection
### Objectives
Provide permission-based geolocation with manual fallback and privacy controls.

### Tasks
- Implement geolocation UI using Browser Geolocation API.
- Create server endpoints to save or resolve a coarse, user-authorized location.
- Add manual location selection and denied/unavailable failure handling.
- Cache/process coordinates only according to privacy settings and avoid precise storage unless required.
- Add location to discovery filters and AI recommendation context.

### Expected outputs
Consent-aware browser workflow, manual location fallback, saved preference behavior, and location service tests using mocked responses.

### Dependencies
Phases 4–7; HTTPS in non-local deployment for browser geolocation support.

### Completion checklist
- [ ] Permission denial has a usable fallback.
- [ ] Coordinates or manual locations cannot be spoofed into administrator access.
- [ ] Location precision is limited appropriately.
- [ ] User can clear or change location preference.
- [ ] AI/discovery consume location only with user consent.

## Phase 10: AI-generated menus
### Objectives
Integrate a configurable AI provider that produces reviewable menu suggestions.

### Tasks
- Add an AI adapter with provider configuration, timeout, retries, and fallback behavior.
- Build a structured prompt that uses coarse location, category preferences, and known recipes/ingredients.
- Validate provider JSON against an application schema.
- Store generation metadata while not automatically exposing it as verified inventory.
- Render ingredient lists, instructions, confidence/assumption notes, regenerate, draft, and publish actions.
- Add content review/edit workflow before publication.

### Expected outputs
AI generation endpoint, provider adapter, validation and persistence, review UI, and mocked provider tests.

### Dependencies
Phases 6–9; approved provider credentials and data policies.

### Completion checklist
- [ ] Provider calls have timeout and failure handling.
- [ ] AI output cannot bypass menu validation.
- [ ] Generated menus are drafts or reviewable records by default.
- [ ] User must explicitly publish reviewed menus.
- [ ] No claim of live store availability is made.
- [ ] Provider keys remain server-side.

## Role module plan
### End-user modules
- **Dashboard:** own recipe/menu counts, drafts, favorites, notifications, recent activity, and recommended community content.
- **Recipes:** browse, search, create/edit, draft/publish, images, ingredients, instructions, detail, and ownership management.
- **Menus:** create/edit menus, select recipes, draft/publish, and own-menu management.
- **Community:** comments, ratings, likes, favorites, reports, author profiles, and notifications.
- **Discovery:** categories, locations, ingredients, popular/new recipes, menus, filters, and pagination.
- **My Kitchen:** My Recipes, drafts, published content, favorites, and saved menus.
- **AI Menus:** generate, review, regenerate, save drafts, and explicitly publish allowed menus.
- **Account:** profile, avatar, password, location consent, units, privacy preferences, sessions, and account status.
- **Messages/Feedback:** in-platform messages or feedback where enabled, notification read state, and support requests.

### System-administrator modules
- **Admin Dashboard:** platform totals, growth, active users, published content, unresolved reports, recent moderation activity, and system health.
- **User Administration:** search/filter users, profile view, role assignment, active/suspended/deactivated status, password-security status, and account history.
- **Content Moderation:** recipe/menu queues, status changes, hidden/removed content, restoration, author notices, and moderation reasons.
- **Reports and Complaints:** unresolved/historical reports, target preview, duplicate detection, resolution actions, notes, and content/account consequences.
- **Community Moderation:** comment visibility/removal, spam review, ratings/likes integrity review, and user abuse patterns.
- **Taxonomy Management:** categories, ingredients, locations, units, featured taxonomy records, activation, merge/retirement, and usage counts.
- **AI Oversight:** generation activity, failure rates, content flags, prompts/provider configuration status, and policy-review records without exposing secrets.
- **Notification Administration:** platform announcements, targeted notices, delivery/read metrics, and template management.
- **Audit and Activity:** immutable actor/action/target records, filters by date and user, reason codes, before/after summaries, and export.
- **System Settings:** public-site configuration, status labels, privacy/cookie text, maintenance mode, upload limits, retention policy, and non-secret health configuration.
- **Backup and Operations:** database backup status, migration status, restore guidance, storage usage, and environment-health monitoring. Backup execution may require deployment privileges and should not perform destructive operations from the browser.

### Recommended authorization policy
- `user`: all end-user capabilities limited to owned content and permitted public/community records.
- `admin`: all user capabilities plus platform administration, moderation, taxonomy, audit, and configuration.
- Keep sensitive account-role changes and audit access server-side. A future `moderator` permission set may be introduced only after explicit requirements; it must not weaken the current admin boundary.

### Shared administration SPA shell
- Reuse the authenticated application layout, fixed topbar, responsive sidebar, reusable data tables, date range filters, status badges, metric cards, dropdown actions, confirmation modals, pagination, empty states, alerts, and audit detail dialogs.
- Administration routes should remain directly addressable and render the same partials through SPA fragments: `/admin/dashboard`, `/admin/users`, `/admin/reports`, `/admin/content`, `/admin/categories`, `/admin/activity`, `/admin/notifications`, `/admin/settings`, and `/admin/system`.

## Phase 11: Administrator dashboard
### Objectives
Provide administration and moderation tools for users, recipes, menus, categories, reports, and activity.

### Tasks
- Implement administrator statistics, activity list, popular-content view, and health-oriented metrics.
- Add user listing, status changes, suspension, and profile view.
- Add recipe/menu moderation, removal, category management, and report resolution.
- Add feedback review and notification/audit logging.
- Ensure actions are authorized and audited.

### Expected outputs
Administrator pages, moderation workflows, category management, audit records, and permission tests.

### Dependencies
Phases 3–8; moderation data must exist.

### Completion checklist
- [ ] Administrator routes require an admin role and protect CSRF operations.
- [ ] Suspension and content removal are reflected consistently.
- [ ] Report actions cannot be repeated or applied without authorization.
- [ ] Audit records capture actor and target without sensitive data.
- [ ] Statistics cannot expose private information.

## Phase 12: Security and validation
### Objectives
Perform a security-focused review and standardize validation and resilience.

### Tasks
- Audit authentication, authorization, SQL, uploads, CSRF, headers, sessions, and external services.
- Run dependency and static security analysis.
- Verify frontend/backend validation parity.
- Add abuse/rate controls to sensitive endpoints.
- Review privacy, location, AI, and logging behavior.
- Document recovery and operational rollback steps.

### Expected outputs
Security checklist, fixes, security tests, dependency report, logging/privacy review, and deployment hardening configuration.

### Dependencies
All feature phases initially implemented.

### Completion checklist
- [ ] Critical and high-risk findings are resolved and retested.
- [ ] CSRF and ownership checks cover state changes.
- [ ] File uploads cannot execute or escape storage policy.
- [ ] No credentials appear in logs or source control.
- [ ] Security headers and cookie policies are verified.

## Phase 13: Testing and debugging
### Objectives
Complete automated and manual verification across the application.

### Tasks
- Add unit tests for services and utilities.
- Add integration tests for Flask routes, repositories, CSRF, and transactions.
- Add end-to-end tests for core user journeys when a stable browser harness is available.
- Test empty/error states, mobile layouts, keyboard use, and accessibility.
- Run migrations on clean and representative upgraded databases.
- Fix defects and regressions found by full suite execution.

### Expected outputs
Test suite, coverage report for critical modules, defect log, browser test evidence, and clean build/test output.

### Dependencies
Feature implementation and security fixes.

### Completion checklist
- [ ] Core user journeys pass.
- [ ] Administrator journeys pass.
- [ ] Critical security and ownership tests pass.
- [ ] Regression suite passes.
- [ ] Known limitations are documented and prioritized.

## Phase 14: Final integration and deployment
### Objectives
Integrate all verified modules and prepare a secure production deployment.

### Tasks
- Verify production configuration, HTTPS requirements, database backup, and reverse-proxy settings.
- Configure secure environment variables and provider credentials.
- Build static uploads and deployment directories with correct permissions.
- Run database migrations and smoke tests.
- Create rollback and backup procedures.
- Complete final documentation and acceptance walkthrough.

### Expected outputs
Deployment guide, production configuration template, migration runbook, backups/rollback plan, smoke-test evidence, and acceptance summary.

### Dependencies
Completed testing phase and approved hosting/database credentials.

### Completion checklist
- [ ] Production smoke tests pass.
- [ ] HTTPS is active and geolocation is available where required.
- [ ] Secrets are injected outside source control.
- [ ] Database backup and rollback procedures are tested.
- [ ] Logs and health checks are operational.
- [ ] User and administrator acceptance walkthrough is complete.
- [x] A local test user is seeded: `testuser@example.com` / `testuser` with password `TestUser123!`.
- [x] Main content drag, text selection drag, image drag, and viewport overscroll are disabled while content scrolling remains available.
