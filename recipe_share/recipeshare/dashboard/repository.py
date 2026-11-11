from recipeshare.shared.database import get_connection


class DashboardRepository:
    def metrics(self, user_id: int | None = None) -> dict:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        author_filter = " AND r.author_id = %s" if user_id is not None else ""
        params = (user_id,) if user_id is not None else ()
        try:
            cursor.execute("SELECT COUNT(*) AS recipe_count FROM recipes r WHERE r.status = 'published'" + author_filter, params)
            recipe_count = cursor.fetchone()["recipe_count"] or 0

            cursor.execute("SELECT COALESCE(SUM(view_count), 0) AS total_views FROM recipes r WHERE r.status = 'published'" + author_filter, params)
            total_views = int(cursor.fetchone()["total_views"] or 0)

            cursor.execute("SELECT COUNT(*) AS total_likes FROM likes lk JOIN recipes r ON r.id = lk.recipe_id WHERE r.status = 'published'" + author_filter, params)
            total_likes = cursor.fetchone()["total_likes"] or 0

            cursor.execute("SELECT COUNT(DISTINCT author_id) AS active_chefs FROM recipes r WHERE r.status = 'published'" + author_filter, params)
            active_chefs = cursor.fetchone()["active_chefs"] or 0

            # Real context trends
            cursor.execute("SELECT COUNT(*) AS weekly_recipes FROM recipes r WHERE r.status = 'published' AND (r.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) OR r.published_at >= DATE_SUB(NOW(), INTERVAL 7 DAY))" + author_filter, params)
            weekly_recipes = cursor.fetchone()["weekly_recipes"] or 0

            cursor.execute("SELECT COUNT(*) AS weekly_likes FROM likes lk JOIN recipes r ON r.id = lk.recipe_id WHERE r.status = 'published' AND lk.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)" + author_filter, params)
            weekly_likes = cursor.fetchone()["weekly_likes"] or 0

            return {
                "recipe_count": recipe_count,
                "total_views": total_views,
                "total_likes": total_likes,
                "active_chefs": active_chefs,
                "weekly_recipes": weekly_recipes,
                "weekly_likes": weekly_likes,
            }
        finally:
            cursor.close()

    def recipes(self, order_by: str = "view_count", limit: int = 100, user_id: int | None = None) -> list[dict]:
        allowed_orders = {
            "view_count": "r.view_count",
            "like_count": "like_count",
            "rating": "average_rating",
            "latest": "r.created_at"
        }
        sort_column = allowed_orders.get(order_by, allowed_orders["view_count"])
        order_clause = "average_rating DESC, review_count DESC, r.view_count DESC" if order_by == "rating" else f"{sort_column} DESC"
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT r.id, r.title, r.slug, r.view_count, r.published_at, r.created_at, "
                "c.name AS category_name, u.username AS author_name, l.name AS location_name, "
                "COALESCE((SELECT COUNT(*) FROM likes lk WHERE lk.recipe_id = r.id), 0) AS like_count, "
                "COALESCE((SELECT AVG(rt.score) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS average_rating, "
                "COALESCE((SELECT COUNT(*) FROM ratings rt WHERE rt.recipe_id = r.id), 0) AS review_count, "
                "COALESCE((SELECT ri.storage_path FROM recipe_images ri WHERE ri.recipe_id = r.id ORDER BY ri.is_primary DESC, ri.id LIMIT 1), '') AS image_path "
                "FROM recipes r LEFT JOIN categories c ON c.id = r.category_id "
                "LEFT JOIN users u ON u.id = r.author_id LEFT JOIN locations l ON l.id = r.location_id "
                "WHERE r.status = 'published' "
                + ("AND r.author_id = %s " if user_id is not None else "")
                + f"ORDER BY {order_clause}, r.id DESC LIMIT %s",
                ((user_id, limit) if user_id is not None else (limit,)),
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def chart_recipes(self, order_by: str = "view_count", user_id: int | None = None, period: str = "all", limit: int = 6) -> list[dict]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        order_clause = "r.view_count DESC, like_count DESC" if order_by == "view_count" else "like_count DESC, r.view_count DESC"
        
        period_clause = ""
        if period == "week":
            period_clause = " AND (r.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) OR r.published_at >= DATE_SUB(NOW(), INTERVAL 7 DAY))"
        elif period == "month":
            period_clause = " AND (r.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) OR r.published_at >= DATE_SUB(NOW(), INTERVAL 30 DAY))"

        try:
            query = (
                "SELECT r.id, r.title, r.slug, r.view_count, "
                "COALESCE((SELECT COUNT(*) FROM likes lk WHERE lk.recipe_id = r.id), 0) AS like_count "
                "FROM recipes r WHERE r.status = 'published' "
                + ("AND r.author_id = %s " if user_id is not None else "")
                + period_clause
                + f" ORDER BY {order_clause} LIMIT %s"
            )
            params = ((user_id, limit) if user_id is not None else (limit,))
            cursor.execute(query, params)
            results = cursor.fetchall()

            # If period filter returned empty and period was specific, fallback to all-time so charts are populated
            if not results and period in {"week", "month"}:
                fallback_query = (
                    "SELECT r.id, r.title, r.slug, r.view_count, "
                    "COALESCE((SELECT COUNT(*) FROM likes lk WHERE lk.recipe_id = r.id), 0) AS like_count "
                    "FROM recipes r WHERE r.status = 'published' "
                    + ("AND r.author_id = %s " if user_id is not None else "")
                    + f" ORDER BY {order_clause} LIMIT %s"
                )
                cursor.execute(fallback_query, params)
                results = cursor.fetchall()

            for item in results:
                raw_score = item["view_count"] if order_by == "view_count" else item["like_count"]
                item["score"] = raw_score
                if raw_score >= 1000:
                    item["display_score"] = f"{raw_score / 1000:.1f}K"
                else:
                    item["display_score"] = str(raw_score)

            return results
        finally:
            cursor.close()

    def location_names(self) -> list[str]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT name FROM locations ORDER BY name ASC")
            return [row["name"] for row in cursor.fetchall() if row.get("name")]
        finally:
            cursor.close()

    def category_names(self) -> list[str]:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT name FROM categories WHERE is_active = TRUE ORDER BY name ASC")
            return [row["name"] for row in cursor.fetchall() if row.get("name")]
        finally:
            cursor.close()


