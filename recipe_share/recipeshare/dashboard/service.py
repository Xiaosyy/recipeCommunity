import mysql.connector

from .repository import DashboardRepository


class DashboardService:
    def __init__(self, repository: DashboardRepository | None = None) -> None:
        self.repository = repository or DashboardRepository()

    def get_dashboard_data(self, user_id: int | None = None, period: str = "all") -> dict:
        try:
            chart_views = self.repository.chart_recipes("view_count", user_id, period)
            chart_likes = self.repository.chart_recipes("like_count", user_id, period)
            location_list = self.repository.location_names()
            category_list = self.repository.category_names()
            return {
                "metrics": self.repository.metrics(user_id),
                "chart_views": chart_views,
                "chart_likes": chart_likes,
                "chart_recipes": chart_views,  # backwards compatibility
                "top_views": self.repository.recipes("view_count", 5, user_id),
                "top_likes": self.repository.recipes("like_count", 5, user_id),
                "top_rated": self.repository.recipes("rating", 5, user_id),
                "inventory": self.repository.recipes("latest", 100, user_id),
                "all_locations": location_list,
                "locations": location_list,
                "all_categories": category_list,
                "categories": category_list,
            }
        except mysql.connector.Error:
            return {
                "metrics": {
                    "recipe_count": 0, "total_views": 0, "total_likes": 0,
                    "active_chefs": 0, "weekly_recipes": 0, "weekly_likes": 0,
                },
                "chart_views": [], "chart_likes": [], "chart_recipes": [],
                "top_views": [], "top_likes": [], "top_rated": [], "inventory": [],
                "all_locations": [], "locations": [],
                "all_categories": [], "categories": [],
            }


