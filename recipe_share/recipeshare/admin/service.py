from .repository import AdminRepository


class AdminService:
    def __init__(self, repository: AdminRepository | None = None) -> None:
        self.repository = repository or AdminRepository()

    def users(self) -> list[dict]:
        return self.repository.users()

    def categories(self) -> list[dict]:
        return self.repository.categories()

    def reports(self) -> list[dict]:
        return self.repository.reports()

    def recipes(self) -> list[dict]:
        return self.repository.recipes()

    def activity(self) -> list[dict]:
        return self.repository.activity()

    def notifications(self, user_id: int) -> list[dict]:
        return self.repository.notifications(user_id)

    def settings(self) -> dict:
        return self.repository.settings()

    def save_settings(self, settings: dict[str, str], actor_id: int) -> None:
        if len(settings.get("community_name", "").strip()) == 0:
            raise ValueError("Community name is required")
        self.repository.save_settings({key: value.strip() for key, value in settings.items()}, actor_id)

    def system_overview(self) -> dict:
        return self.repository.system_overview()

    def set_user_status(self, user_id: int, status: str, actor_id: int) -> None:
        if status not in {"active", "suspended", "deactivated"}:
            raise ValueError("Invalid user status")
        self.repository.set_user_status(user_id, status, actor_id)

    def set_user_role(self, user_id: int, role: str, actor_id: int) -> None:
        if role not in {"user", "admin"}:
            raise ValueError("Invalid role")
        self.repository.set_user_role(user_id, role, actor_id)

    def delete_user_permanently(self, user_id: int, actor_id: int) -> dict:
        if int(user_id) == int(actor_id):
            raise ValueError("You cannot delete your own account.")
        all_users = self.users()
        target = next((u for u in all_users if int(u["id"]) == int(user_id)), None)
        if not target:
            raise ValueError("User not found.")
        if target.get("role_name") == "admin":
            admin_count = len([u for u in all_users if u.get("role_name") == "admin"])
            if admin_count <= 1:
                raise ValueError("Cannot delete the only administrator account.")
        return self.repository.delete_user_permanently(int(user_id), actor_id)

    def save_category(self, category_id: int | None, name: str, description: str, active: bool, actor_id: int) -> None:
        if not name.strip():
            raise ValueError("Category name is required")
        self.repository.save_category(category_id, name.strip(), description.strip(), active, actor_id)

    def delete_category(self, category_id: int, actor_id: int) -> None:
        self.repository.delete_category(category_id, actor_id)

    def resolve_report(self, report_id: int, status: str, actor_id: int) -> None:
        if status not in {"resolved", "dismissed"}:
            raise ValueError("Invalid report status")
        self.repository.resolve_report(report_id, status, actor_id)

    def set_recipe_status(self, recipe_id: int, status: str, actor_id: int) -> None:
        if status not in {"draft", "published", "hidden", "removed"}:
            raise ValueError("Invalid recipe status")
        self.repository.set_recipe_status(recipe_id, status, actor_id)
