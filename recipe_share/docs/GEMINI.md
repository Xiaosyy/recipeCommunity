# GEMINI.md — Recipe Sharing Community System Development Rules

## Project overview
This project is a server-rendered and progressively enhanced Flask web application for sharing, discovering, rating, saving, and managing recipes and menus. It is a community platform with end users and administrators. The initial planning scope explicitly excludes application implementation, but once approved these rules govern every subsequent change.

## Approved technology stack and restrictions
- Backend: Python and Flask.
- Database: MySQL.
- MySQL driver: `mysql-connector-python` or another explicitly compatible Flask/MySQL library.
- Frontend: HTML5, CSS3, and vanilla JavaScript.
- Templates: Jinja2 supplied by Flask.
- Authentication: Flask session-based authentication with secure password hashing.
- Keep secrets, credentials, API keys, database passwords, and environment-specific configuration out of source control.
- Do not replace Flask, MySQL, HTML/CSS, JavaScript, or the MySQL driver without discussing the change first.
- Do not introduce a frontend framework, ORM, alternate database, task queue, or external AI provider unless it is documented, justified, and approved.
- Location detection must use the browser Geolocation API only with permission and must provide a manual fallback.
- AI output is advisory. Never represent unverified ingredients or AI-generated claims as verified local inventory or facts.

## Coding standards
- Python code must be readable, consistently formatted, and type hints should be used for non-trivial public functions.
- Use snake_case for Python variables, functions, modules, database columns, and API payload fields; PascalCase for classes; UPPER_SNAKE_CASE for constants.
- Use kebab-case for CSS files and classes only where framework convention does not require another form. Use lower_snake_case or lower-case route names consistently with existing project conventions.
- Use HTML template names that match pages, routes, and modules (for example, `recipe_form.html`).
- Prefer explicit imports, small functions, and dependency-injected application configuration over global application state.
- Use parameterized SQL for every database operation. Never concatenate user-controlled values into SQL.
- Keep secrets in environment variables and provide safe defaults only for non-sensitive development settings.
- Every user-facing form must have server-side validation; client-side validation improves experience but never replaces server-side checks.
- Add concise comments only for non-obvious security, authorization, data-integrity, geolocation, or AI behavior.

## Folder organization and partial-based UI
The repository must use a standard, predictable, layered structure. Feature modules own their routes, services, repositories, templates, styles, and scripts without placing the full application in a single file.

```text
recipe_share/
├── app.py
├── requirements.txt
├── pyproject.toml
├── .env.example
├── README.md
├── config/
│   ├── __init__.py
│   └── settings.py
├── database/
│   ├── schema.sql
│   ├── migrations/
│   └── seeds/
├── docs/
│   ├── GEMINI.md
│   ├── Roadmap.md
│   ├── API.md
│   └── SystemPlan.md
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── recipeshare/
    ├── __init__.py
    ├── extensions.py
    ├── shared/
    │   ├── __init__.py
    │   ├── database.py
    │   ├── decorators.py
    │   ├── validators.py
    │   └── exceptions.py
    ├── auth/
    │   ├── __init__.py
    │   ├── routes.py
    │   ├── service.py
    │   ├── repository.py
    │   └── partials/
    ├── home/
    │   ├── __init__.py
    │   ├── routes.py
    │   ├── service.py
    │   └── partials/
    ├── users/
    │   ├── __init__.py
    │   ├── routes.py
    │   ├── service.py
    │   ├── repository.py
    │   └── partials/
    ├── recipes/
    ├── menus/
    ├── community/
    ├── location/
    ├── ai/
    ├── admin/
    ├── templates/
    │   ├── layouts/
    │   │   └── app.html
    │   ├── partials/
    │   │   ├── navbar.html
    │   │   ├── footer.html
    │   │   ├── flash_messages.html
    │   │   ├── loading.html
    │   │   ├── empty_state.html
    │   │   └── confirmation_modal.html
    │   └── components/
    │       ├── buttons.html
    │       ├── form_fields.html
    │       ├── cards.html
    │       ├── alerts.html
    │       └── pagination.html
    └── static/
        ├── css/
        │   ├── base.css
        │   ├── layout.css
        │   ├── components.css
        │   └── responsive.css
        ├── js/
        │   ├── app.js
        │   ├── spa-router.js
        │   ├── api-client.js
        │   └── components/
        └── uploads/
            ├── avatars/
            └── recipes/
```

- Keep `config.py`, database utilities, application blueprints, services, repositories, templates, CSS, and JavaScript organized by responsibility.
- Every feature module must expose its UI as small Jinja partials stored under that feature's `partials/` folder; pages compose partials rather than embedding a module's full markup in a large template.
- Every reusable UI element—navigation, form fields, buttons, alerts, cards, pagination, loading states, empty states, modal confirmations, and recipe/menu cards—must be maintained as a reusable component partial and used consistently.
- A partial must have one clear presentation purpose, accept explicit inputs, and avoid direct database or service calls.
- Shared layout and global partials belong in `templates/layouts/` or `templates/partials/`; feature-specific partials belong in the feature module.
- Separate CSS and JavaScript by global concern and feature module. Do not use inline style blocks or inline page scripts.
- An SPA view or module must have a matching partial for navigation-level rendering and may also have smaller fragments loaded through API responses.
- Route names, partial names, template directories, module names, and API resource names must use the same English feature terminology.
- Do not place the complete application, a feature workflow, or all reusable components in a single Python or template file.
- Keep the package name `recipeshare` unless a deliberate, documented refactor is approved.
- Virtual environments, secrets, generated uploads, caches, and database files must stay outside tracked source directories.
- Store contributor documentation under `docs/`; planning documents are mirrored there rather than mixed into runtime packages.

## Database rules
- Model the logical schema using roles, users, profiles, recipes, menus, ingredients, categories, images, comments, ratings, likes, favorites, reports, notifications, generated-menu records, and supporting join tables.
- Every table must have a well-defined primary key. Use surrogate integer primary keys unless a domain key is demonstrably preferable.
- Enforce ownership and state transitions in application services and database constraints whenever practical.
- Use foreign keys, unique constraints, check constraints, indexes, and cascade rules to preserve integrity.
- Represent soft-deactivated users and reported content explicitly; do not use deletion as the only moderation mechanism.
- Use distinct content states such as `draft` and `published`. Withdrawn or hidden states may be added only for clear workflows.
- MySQL transactions are required for operations that create or update multiple related records.
- Store timestamps with UTC semantics where practical and display converted local values in templates.
- Passwords are stored only as strong adaptive hashes; never store reversible passwords.
- Run schema changes through versioned SQL migration scripts. Do not edit production data ad hoc.
- Search should add indexes after reviewing query plans; avoid premature denormalization.

## Authentication and authorization
- Use Flask session cookies with a secure secret, `HttpOnly`, `Secure` in production, and an appropriate `SameSite` policy.
- Hash passwords with a maintained adaptive password hashing implementation and a per-password salt.
- Verify ownership (`created_by == current_user_id`) before recipe/menu editing, deletion, publishing, or viewing private drafts.
- Use role/permission checks for administrator routes. Authentication alone is not authorization.
- Regenerate session identifiers after login and privilege changes.
- Protect state-changing browser endpoints against CSRF. Return appropriate 401/403 responses for API-style requests.
- Apply login throttling or equivalent abuse controls to authentication endpoints and never expose whether an account exists during password recovery or verification flows, unless those flows are explicitly implemented and approved.
- Account suspension/deactivation must prevent normal authenticated actions while preserving records needed for moderation and auditability.

## Security and privacy
- Escape template output by default; avoid `safe`, raw SQL, and raw HTML unless sanitized and justified.
- Validate content types, extensions, file dimensions, decoded content when practical, and size limits for uploads. Store uploaded user files outside executable application paths and use generated filenames.
- Consent is required for browser location access. Display a meaningful permission explanation, store only the precision necessary for recommendations, and allow the user to clear location data.
- Provide manual location selection and handle denied, timed-out, unavailable, and inaccurate geolocation responses gracefully.
- Add security headers, rate limiting for abusive endpoints, logging without sensitive payloads, and explicit privacy/cookie messaging.
- Sanitize filenames and never trust client-provided paths or MIME types.
- Add or update automated security checks and dependency scans when dependencies change.

## Frontend rules
- Preserve the approved RecipeShare UI direction: cream public surfaces, deep-green navigation and primary actions, warm food photography, white cards, restrained green/red/orange status accents, and a consistent branded shell.
- Implement one server-backed application layout with separate public and authenticated shells. SPA navigation swaps the main view and preserves shared headers, sidebars, search, profile, notifications, location, and role-aware navigation.
- Use progressively enhanced server-rendered Jinja views and vanilla JavaScript SPA routing. Direct Flask routes, history navigation, refresh, and non-JavaScript submission must remain functional.
- Navigation configuration, dashboard metrics, recipe/menu/category content, rankings, charts, location choices, notifications, profile values, moderation records, and status badges must be loaded from services/APIs. Seed data may exist for development, but placeholders must never be permanent template data.
- Keep stable UI configuration centralized (pagination limits, allowed sorts, breakpoints, upload limits) while business content remains dynamic. Do not duplicate feature route lists or role lists across templates and JavaScript.
- Use shared component partials and feature partials; do not create page-sized templates or inline full feature markup.
- Add a loading skeleton for SPA transitions and reuse shared empty, error, unauthorized, validation, confirmation, and timeout states.
- All SPA state-changing requests must use CSRF protection and the same authorization, validation, and API error contracts as direct page requests.
- Use the History API and support browser Back/Forward, title updates, focus restoration, and scroll restoration without full-layout remounts.
- Design for desktop and mobile breakpoints with semantic HTML, keyboard navigation, visible focus states, and sufficient contrast.
- Use shared layout, component, and responsive CSS files. Avoid page-specific CSS embedded in templates unless temporary and explicitly justified.
- Use progressive enhancement: core browsing and form submission work before enhanced JavaScript.
- Keep fetch/AJAX requests small, handle loading, empty, success, timeout, and error states, and avoid exposing secrets in browser code.
- Preserve accessible labels, descriptions, error summaries, status announcements, image alternative text, and confirmation dialogs.
- Use reusable recipe cards, menu cards, navigation, pagination, form field, alert, and profile components.
- Frontend validation mirrors backend constraints but does not replace backend validation.
- No excessive animation, unnecessary empty space, or overcrowded recipe detail screens.

## Backend rules
- Use Flask application factories and Blueprints.
- Keep HTTP concerns in routes, domain rules in services, persistence in repositories, and presentation in templates.
- Use request schemas/payload validation even for browser form posts.
- Return consistent JSON error objects for endpoints intended for clients and normal Flask error templates for browser pages.
- Handle 400, 401, 403, 404, 409, 422, 429, and 500 responses consistently and avoid leaking stack traces.
- Keep database connections in request context, close them reliably, and commit only after successful complete transactions.
- Treat external AI and geocoding services as unreliable adapters with timeouts, validation, and fallback behavior.
- A generated menu is never published automatically. It must enter review and be explicitly saved as draft or published.

## Rules for modifying existing files
- Read the surrounding implementation and tests before editing existing files.
- Make the smallest complete change that satisfies the requirement and preserve existing behavior.
- Do not rename public routes, database columns, or templates without migration and reference updates.
- Update directly related tests and documentation whenever behavior changes.
- Do not refactor unrelated code in the same change.
- Do not overwrite user changes or generated content without review.
- Add database migration and seed changes together when a schema dependency changes.

## Avoiding duplication and maintaining consistency
- Reuse layout, partial templates, CSS components, JavaScript utilities, repositories, and service functions.
- UI partial components are mandatory. Create a shared component only after two views repeat the same structure, and name it by its UI purpose rather than by the page that first uses it.
- Feature pages compose global partials, shared components, and feature partials; feature partials must never duplicate equivalent markup from another module.
- Centralize role checks, pagination, upload handling, flash/error presentation, and standardized API responses.
- Define API contracts in `API.md` before implementation and keep the implementation synchronized with them.
- Keep database column names, route payload names, template form names, and service arguments aligned.
- Add shared constants for statuses and roles instead of duplicating string literals.
- Every feature must have a user-visible workflow, authorization rule, validation, persistence, error handling, and automated coverage.
- When requirements are uncertain, document an assumption and do not invent scope silently.

## Development workflow
1. Complete and review this document, `Roadmap.md`, `API.md`, and `SystemPlan.md`.
2. Obtain approval before starting Phase 1 implementation.
3. Complete each roadmap phase and its automated checks before the next major phase begins.
4. Review the diff, update related documentation, run targeted tests, then run the relevant broader suite.
5. Keep database schema and API documentation synchronized with the implementation.
6. Record unplanned scope in the roadmap rather than expanding silently.

## Setup expectations
- Add a Python virtual environment and `requirements.txt` or an equivalent pinned dependency manifest.
- Provide `.env.example` containing documented variable names without real secrets.
- Include MySQL setup and schema commands.
- Document Windows and cross-platform activation or configuration commands when practical.
- Never treat the virtual environment directory as application source or commit it.
