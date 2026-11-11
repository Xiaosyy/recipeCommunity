# Recipe Sharing Community System — API Contract

## Conventions
- Base path: `/api/v1`.
- Formats: JSON requests and responses unless `multipart/form-data` is specified.
- IDs are positive integers.
- Dates are ISO 8601 UTC strings; timestamps are not recalculated by clients.
- Browser pages may share services and route URLs, while these REST endpoints remain the integration contract.
- Error responses use: `{"error": {"code": "ERROR_CODE", "message": "Human-readable message", "fields": {}}}`.
- CSRF protection is required for state-changing browser requests. API clients must also obtain the server's approved CSRF token if session-authenticated.
- Authentication is `session` or `none`. Roles are `user` and `admin`.
- Pagination uses `page`, `per_page`, `total`, and `items` unless otherwise noted.
- `draft` and `published` are reserved content statuses. Additional states must be added consistently to this document and database constraints.

## SPA and UI fragments

The SPA uses normal browser routes for initial render and the following server-backed UI contracts. Full page routes render the matching layout and partials; fragment responses must contain presentation-only HTML that does not duplicate layout shells.

### Navigation configuration
- `GET /api/v1/ui/navigation`
- Purpose: Return role-aware navigation, profile summary, notification count, location summary, and logout/search actions for the application shell.
- Authentication: Optional; signed session when available.
- Response `200`: `{navigation: [{id, label, path, icon, badge_key}], user, notifications, location}`.
- Rules: Navigation order, labels, icons, visibility, and badges come from server configuration plus authorization. JavaScript must not encode role-specific menus. Public and guest navigation use a separate default collection.

### SPA page fragment
- Browser routes such as `/dashboard`, `/recipes`, `/recipes/{recipe_id}`, `/favorites`, `/admin/dashboard`, `/admin/reports`, and form/detail routes remain directly addressable.
- `GET /api/v1/ui/pages/{view}`
- Purpose: Return one SPA main-content view built from the same feature services and Jinja partials used by direct rendering.
- Authentication: None or session according to the view.
- Query: optional `page`, filters, and view-specific parameters already defined by the matching resource endpoint.
- Response `200`: `{title, description, breadcrumb: [], html, page_state}`.
- Response `partial_content`: HTML contains only the main view and must be safe to insert in the existing application layout.
- Errors: `401`, `403`, `404` with the normal UI error partial representation.

### UI content conventions
- JSON content endpoints and SPA fragment endpoints share validators, services, authorization, pagination, sorting, and empty/error state contracts.
- UI fragment HTML is generated only by approved Jinja component/feature partials and must be escaped by Jinja.
- Client JavaScript may render transient loading state and request status, but it must not source persistent recipe/menu/user/chart/navigation data as hardcoded fixture arrays.
- Components that display action state (likes, favorites, ratings, notifications, moderation) use API response data to update the existing component instance.

## Authentication

### Register
- `POST /register` (and `POST /api/v1/auth/register`)
- Purpose: Create an end-user account, issue a 6-digit email verification OTP, and redirect to `/verify-email`.
- Authentication: None.
- Body: `{username, email, password, password_confirmation}`.
- Response `302` (browser) / `201` (API): `{user: {id, username, email, role, status}}`.
- Errors: `400`, `409` username/email already exists, `422` validation failure.

### Verify email OTP
- `GET /verify-email` / `POST /verify-email`
- Purpose: Verify a newly registered or unverified user's email address with a 6-digit one-time passcode (OTP) and establish an authenticated session.
- Authentication: Pending verification session (`pending_verification_user_id`).
- Body: `{otp_code}` or `{otp_1, otp_2, otp_3, otp_4, otp_5, otp_6}`.
- Response `302`: Redirects to `/dashboard` (or `/admin/dashboard`) with established session.
- Errors: `422` invalid, expired, or maximum-attempt-exceeded OTP code.

### Resend email OTP
- `POST /verify-email/resend`
- Purpose: Invalidate previous active OTPs and issue a fresh 6-digit verification code to the pending user's email.
- Authentication: Pending verification session (`pending_verification_user_id`).
- Body: `{csrf_token}`.
- Response `302`: Redirects back to `/verify-email`.

### Login
- `POST /api/v1/auth/login`
- Purpose: Authenticate and establish a session.
- Authentication: None.
- Body: `{email_or_username, password}`.
- Response `200`: `{user: {id, username, role}}`.
- Errors: `401` invalid credentials, `403` deactivated/suspended, `429` throttled.

### Logout
- `POST /api/v1/auth/logout`
- Purpose: End the current session.
- Authentication: Session.
- Body: `{}`.
- Response `204`.
- Errors: `401`.

### Change password
- `POST /api/v1/auth/change-password`
- Purpose: Replace the authenticated user's password.
- Authentication: Session; user.
- Body: `{current_password, new_password, new_password_confirmation}`.
- Response `200`: `{message}`.
- Errors: `401`, `422`, `429`.

## User profiles

### Get own profile
- `GET /api/v1/users/me`
- Purpose: Return the authenticated user's profile.
- Authentication: Session; user.
- Parameters: None.
- Response `200`: `{id, username, email, profile: {display_name, bio, avatar_url, location}}`.
- Errors: `401`, `404`.

### Update own profile
- `PUT /api/v1/users/me`
- Purpose: Update profile fields.
- Authentication: Session; user.
- Body: `{display_name, bio, location_id, preferred_units}`.
- Response `200`: `{profile}`.
- Errors: `401`, `422`, `409` username conflict where applicable.

### Upload avatar
- `POST /api/v1/users/me/avatar`
- Purpose: Replace profile avatar.
- Authentication: Session; user.
- Body: `multipart/form-data` containing `avatar`.
- Response `200`: `{avatar_url}`.
- Errors: `400`, `401`, `413`, `415`, `422`.

### Public profile
- `GET /api/v1/users/{user_id}`
- Purpose: Display approved public profile information and content counts.
- Authentication: None or session.
- Parameters: `user_id` path parameter.
- Response `200`: `{id, username, display_name, bio, avatar_url, recipe_count, menu_count}`.
- Errors: `404` inactive profile or not found.

## Recipes

### List published recipes
- `GET /api/v1/recipes`
- Purpose: Browse published recipes.
- Authentication: Optional.
- Query: `page`, `per_page`, `q`, `category_id`, `ingredient`, `location_id`, `author_id`, `sort` (`newest`, `popular`, `rating`).
- Response `200`: `{items, page, per_page, total}`.
- Errors: `400` invalid sort/filter, `422` invalid range.

### Get recipe
- `GET /api/v1/recipes/{recipe_id}`
- Purpose: Read recipe details.
- Authentication: Optional. A draft requires session and ownership.
- Response `200`: `{recipe with ingredients, instructions, author, images, category, aggregate_rating, user_liked, user_saved}`.
- Errors: `404`, `403` inaccessible draft.

### Create recipe
- `POST /api/v1/recipes`
- Purpose: Create a draft or published recipe.
- Authentication: Session; user.
- Body: `{title, description, category_id, servings, prep_minutes, cook_minutes, status, ingredients: [{ingredient_id_or_name, quantity, unit}], instructions, image_ids}`.
- Response `201`: `{recipe}`.
- Errors: `400`, `401`, `422`, `409` inconsistent status transition.

### Update recipe
- `PUT /api/v1/recipes/{recipe_id}`
- Purpose: Replace editable recipe fields.
- Authentication: Session; owner.
- Body: Same as create; `status` may be `draft` or `published` for an allowed transition.
- Response `200`: `{recipe}`.
- Errors: `401`, `403`, `404`, `409`, `422`.

### Delete recipe
- `DELETE /api/v1/recipes/{recipe_id}`
- Purpose: Remove a recipe owned by the user.
- Authentication: Session; owner.
- Body: None.
- Response `204`.
- Errors: `401`, `403`, `404`, `409` if dependency policy requires archival instead.

### Publish/unpublish recipe
- `POST /api/v1/recipes/{recipe_id}/status`
- Purpose: Change allowed draft/publication state.
- Authentication: Session; owner.
- Body: `{status: "draft" | "published"}`.
- Response `200`: `{recipe}`.
- Errors: `401`, `403`, `404`, `409`, `422`.

### Upload recipe images
- `POST /api/v1/recipes/{recipe_id}/images`
- Purpose: Upload one or more images for an owned recipe.
- Authentication: Session; owner.
- Body: `multipart/form-data` containing `images[]`; optional `primary_image`.
- Response `201`: `{images}`.
- Errors: `400`, `401`, `403`, `413`, `415`, `422`.

### Delete recipe image
- `DELETE /api/v1/recipes/{recipe_id}/images/{image_id}`
- Purpose: Delete an owned recipe image.
- Authentication: Session; owner.
- Response `204`.
- Errors: `401`, `403`, `404`.

### List own recipes
- `GET /api/v1/users/me/recipes`
- Purpose: View own drafts and published recipes.
- Authentication: Session; user.
- Query: `page`, `per_page`, `status`.
- Response `200`: `{items, ...pagination}`.
- Errors: `401`, `422`.

## Menus

### List published menus
- `GET /api/v1/menus`
- Purpose: Browse published menus.
- Authentication: Optional.
- Query: `page`, `per_page`, `q`, `category_id`, `location_id`, `sort`.
- Response `200`: `{items, ...pagination}`.
- Errors: `400`, `422`.

### Get menu
- `GET /api/v1/menus/{menu_id}`
- Purpose: Read a menu and its recipes.
- Authentication: Optional; drafts require ownership.
- Response `200`: `{menu}`.
- Errors: `403`, `404`.

### Create menu
- `POST /api/v1/menus`
- Purpose: Create a menu draft or publication.
- Authentication: Session; user.
- Body: `{title, description, status, category_id, recipe_ids: [id], menu_notes}`.
- Response `201`: `{menu}`.
- Errors: `400`, `401`, `422`, `409` unpublished recipe referenced unless policy allows drafts.

### Update menu
- `PUT /api/v1/menus/{menu_id}`
- Purpose: Replace editable menu fields.
- Authentication: Session; owner.
- Body: Same as create.
- Response `200`: `{menu}`.
- Errors: `401`, `403`, `404`, `409`, `422`.

### Delete menu
- `DELETE /api/v1/menus/{menu_id}`
- Purpose: Remove an owned menu.
- Authentication: Session; owner.
- Response `204`.
- Errors: `401`, `403`, `404`.

### Change menu status
- `POST /api/v1/menus/{menu_id}/status`
- Purpose: Publish or return a menu to draft.
- Authentication: Session; owner.
- Body: `{status: "draft" | "published"}`.
- Response `200`: `{menu}`.
- Errors: `401`, `403`, `409`, `422`.

### List own menus
- `GET /api/v1/users/me/menus`
- Purpose: View own drafts and published menus.
- Authentication: Session; user.
- Query: `page`, `per_page`, `status`.
- Response `200`: `{items, ...pagination}`.
- Errors: `401`, `422`.

## Categories and ingredients

### List categories
- `GET /api/v1/categories`
- Purpose: List active recipe/menu categories.
- Authentication: Optional.
- Response `200`: `{categories: [{id, name, slug}]}`.
- Errors: `500` service unavailable.

### Create category (admin)
- `POST /api/v1/admin/categories`
- Purpose: Create a category.
- Authentication: Session; admin.
- Body: `{name, slug, description}`.
- Response `201`: `{category}`.
- Errors: `401`, `403`, `409`, `422`.

### Update category (admin)
- `PUT /api/v1/admin/categories/{category_id}`
- Purpose: Rename or deactivate a category.
- Authentication: Session; admin.
- Body: `{name, slug, description, is_active}`.
- Response `200`: `{category}`.
- Errors: `401`, `403`, `404`, `409`, `422`.

### Delete category (admin)
- `DELETE /api/v1/admin/categories/{category_id}`
- Purpose: Deactivate or delete an unused category.
- Authentication: Session; admin.
- Response `204` or `409` if category has content.
- Errors: `401`, `403`, `404`, `409`.

### Search ingredients
- `GET /api/v1/ingredients`
- Purpose: Support ingredient autocomplete and normalized selection.
- Authentication: Optional for public search.
- Query: `q`, `limit`.
- Response `200`: `{ingredients: [{id, name}]}`.
- Errors: `400`, `422`.

### Create ingredient
- `POST /api/v1/ingredients`
- Purpose: Suggest/create an approved normalized ingredient while authoring.
- Authentication: Session; user.
- Body: `{name}`.
- Response `201`: `{ingredient}` or `200` existing canonical ingredient.
- Errors: `401`, `409`, `422`.

## Search and filters

### Unified search
- `GET /api/v1/search`
- Purpose: Search published recipes and menus.
- Authentication: Optional.
- Query: `q`, `type` (`recipe`, `menu`, `all`), `category_id`, `ingredient`, `location_id`, `page`, `per_page`.
- Response `200`: `{recipes, menus, total}`.
- Errors: `400`, `422`.

### Popular recipes
- `GET /api/v1/recipes/popular`
- Purpose: Return recipes ranked by views, likes, and ratings using documented weighted rules.
- Authentication: Optional.
- Query: `period` (`day`, `week`, `month`, `all`), `limit`, `category_id`.
- Response `200`: `{recipes}`.
- Errors: `400`, `422`.

## Comments, ratings, likes, and favorites

### List comments
- `GET /api/v1/recipes/{recipe_id}/comments`
- Purpose: List visible comments for a recipe.
- Authentication: Optional.
- Query: `page`, `per_page`.
- Response `200`: `{items, ...pagination}`.
- Errors: `404` recipe unavailable.

### Add comment
- `POST /api/v1/recipes/{recipe_id}/comments`
- Purpose: Leave feedback on a published recipe.
- Authentication: Session; user.
- Body: `{body, parent_comment_id}` optional for a reply.
- Response `201`: `{comment}`.
- Errors: `401`, `403`, `404`, `422`, `429`.

### Update comment
- `PUT /api/v1/comments/{comment_id}`
- Purpose: Edit an owned comment.
- Authentication: Session; owner.
- Body: `{body}`.
- Response `200`: `{comment}`.
- Errors: `401`, `403`, `404`, `422`.

### Delete comment
- `DELETE /api/v1/comments/{comment_id}`
- Purpose: Delete an owned comment; administrator may moderate it.
- Authentication: Session; owner/admin.
- Response `204`.
- Errors: `401`, `403`, `404`.

### Rate recipe
- `PUT /api/v1/recipes/{recipe_id}/rating`
- Purpose: Create or update the user's one rating.
- Authentication: Session; user.
- Body: `{score}` integer in the documented 1–5 range.
- Response `200`: `{rating, average_rating, rating_count}`.
- Errors: `401`, `403`, `404`, `422`.

### Remove rating
- `DELETE /api/v1/recipes/{recipe_id}/rating`
- Purpose: Remove the current user's rating.
- Authentication: Session; user.
- Response `204`.
- Errors: `401`, `404`.

### Toggle recipe like
- `PUT /api/v1/recipes/{recipe_id}/like`
- Purpose: Idempotently set a like.
- Authentication: Session; user.
- Body: `{liked: true|false}`.
- Response `200`: `{liked, like_count}`.
- Errors: `401`, `403`, `404`, `409`.

### Add/remove favorite
- `PUT /api/v1/recipes/{recipe_id}/favorite`
- Purpose: Set or remove a favorite.
- Authentication: Session; user.
- Body: `{favorited: true|false}`.
- Response `200`: `{favorited}`.
- Errors: `401`, `403`, `404`, `409`.

### List favorites
- `GET /api/v1/users/me/favorites`
- Purpose: List saved recipes.
- Authentication: Session; user.
- Query: `page`, `per_page`.
- Response `200`: `{items, ...pagination}`.
- Errors: `401`.

## Reports and notifications

### Create report
- `POST /api/v1/reports`
- Purpose: Report inappropriate recipe, menu, or comment content.
- Authentication: Session; user.
- Body: `{target_type, target_id, reason, details}`.
- Response `201`: `{report}`.
- Errors: `401`, `404`, `409` duplicate unresolved report, `422`.

### List own notifications
- `GET /api/v1/users/me/notifications`
- Purpose: Retrieve user notifications.
- Authentication: Session; user.
- Query: `unread_only`, `page`, `per_page`.
- Response `200`: `{items, unread_count, ...pagination}`.
- Errors: `401`.

### Mark notification read
- `POST /api/v1/users/me/notifications/{notification_id}/read`
- Purpose: Mark one notification read.
- Authentication: Session; user.
- Body: `{}`.
- Response `200`: `{notification}`.
- Errors: `401`, `404`.

## Location detection and manual location

### Save consented location preference
- `POST /api/v1/users/me/location`
- Purpose: Save coarse detected or manual location.
- Authentication: Session; user.
- Body: `{latitude, longitude, location_id, location_source: "geolocation" | "manual", consent: true}`. Coordinates may be omitted when a `location_id` identifies an allowed area.
- Response `200`: `{location}`.
- Errors: `400`, `401`, `422`.

### Clear location
- `DELETE /api/v1/users/me/location`
- Purpose: Remove saved location preference and related precise coordinates.
- Authentication: Session; user.
- Response `204`.
- Errors: `401`.

### Search locations
- `GET /api/v1/locations`
- Purpose: Support manual location selection.
- Authentication: Optional.
- Query: `q`, `limit`.
- Response `200`: `{locations: [{id, name, region, country_code}]}`.
- Errors: `400`, `422`.

## AI menu generation

### Generate a menu
- `POST /api/v1/ai/menus/generate`
- Purpose: Create an AI-suggested draft menu for review.
- Authentication: Session; user.
- Body: `{location_id, category_ids, dietary_preferences, excluded_ingredients, serving_count, meal_type}`. A location is used only after consent.
- Response `202`: `{generation_id, status: "pending"}`; upon synchronous completion, `201`: `{menu_id, menu: {draft}, assumptions, generated_at}`.
- Errors: `401`, `422`, `429`, `503` provider unavailable, `504` timeout.

### Get generation
- `GET /api/v1/ai/menus/generations/{generation_id}`
- Purpose: Read generation status/output.
- Authentication: Session; owner.
- Response `200`: `{generation_id, status, menu, error}`.
- Errors: `401`, `403`, `404`.

### Regenerate menu
- `POST /api/v1/ai/menus/generations/{generation_id}/regenerate`
- Purpose: Generate a new reviewed suggestion with the same or adjusted request.
- Authentication: Session; owner.
- Body: `{overrides}` optional.
- Response `202/201` using the generate response contract.
- Errors: `401`, `403`, `404`, `429`, `503`, `504`.

### Save generated menu
- `POST /api/v1/ai/menus/generations/{generation_id}/save`
- Purpose: Save edited generated output as draft or directly request the allowed publish workflow.
- Authentication: Session; owner.
- Body: `{status: "draft" | "published", title, description, recipe_ids, ingredients, instructions}`.
- Response `201`: `{menu}`.
- Errors: `401`, `403`, `404`, `409`, `422`.

## Administration

All administration API requests require an authenticated administrator role. State-changing requests require a valid CSRF token and return consistent `401`, `403`, `409`, or `422` errors. Every successful administrative state change creates an audit record with actor, target, action, reason, and privacy-safe metadata.

Administration browser routes and SPA fragments use the same names:
- `/admin/dashboard` and `/api/v1/ui/pages/admin/dashboard`
- `/admin/users` and `/api/v1/ui/pages/admin/users`
- `/admin/reports` and `/api/v1/ui/pages/admin/reports`
- `/admin/content` and `/api/v1/ui/pages/admin/content`
- `/admin/categories` and `/api/v1/ui/pages/admin/categories`
- `/admin/activity` and `/api/v1/ui/pages/admin/activity`
- `/admin/notifications` and `/api/v1/ui/pages/admin/notifications`
- `/admin/settings` and `/api/v1/ui/pages/admin/settings`
- `/admin/system` and `/api/v1/ui/pages/admin/system`

### Dashboard statistics
- `GET /api/v1/admin/dashboard`
- Purpose: Return aggregate platform statistics.
- Authentication: Session; admin.
- Response `200`: `{users, recipes, menus, reports, popular_recipes, activity}`.
- Errors: `401`, `403`.

### List users
- `GET /api/v1/admin/users`
- Purpose: Search and list managed accounts.
- Authentication: Session; admin.
- Query: `q`, `status`, `role`, `page`, `per_page`.
- Response `200`: `{items, ...pagination}`.
- Errors: `401`, `403`.

### Update user status
- `PATCH /api/v1/admin/users/{user_id}`
- Purpose: Change account status/role within permitted admin policy.
- Authentication: Session; admin.
- Body: `{status: "active" | "suspended" | "deactivated", role}` optional.
- Response `200`: `{user}`.
- Errors: `401`, `403`, `404`, `409`, `422`.

### List moderation reports
- `GET /api/v1/admin/reports`
- Purpose: List unresolved and historical reports.
- Authentication: Session; admin.
- Query: `status`, `target_type`, `page`, `per_page`.
- Response `200`: `{items, ...pagination}`.
- Errors: `401`, `403`.

### Resolve report
- `POST /api/v1/admin/reports/{report_id}/resolve`
- Purpose: Record report action and optionally hide/remove the target.
- Authentication: Session; admin.
- Body: `{resolution, action: "none" | "warn" | "hide" | "remove" | "suspend", note}`.
- Response `200`: `{report}`.
- Errors: `401`, `403`, `404`, `409`, `422`.

### Moderate recipe/menu
- `PATCH /api/v1/admin/content/{target_type}/{target_id}`
- Purpose: Hide, restore, or remove reported published content.
- Authentication: Session; admin.
- Path: `target_type` is `recipe` or `menu`; `target_id` is integer.
- Body: `{status: "published" | "hidden" | "removed", reason}`.
- Response `200`: `{content}`.
- Errors: `401`, `403`, `404`, `409`, `422`.

### List activity
- `GET /api/v1/admin/activity`
- Purpose: View authorized audit and activity records.
- Authentication: Session; admin.
- Query: `actor_id`, `action`, `start`, `end`, `page`, `per_page`.
- Response `200`: `{items, ...pagination}`.
- Errors: `400`, `401`, `403`, `422`.
