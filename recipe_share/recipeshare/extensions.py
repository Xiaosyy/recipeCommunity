from flask import render_template
from flask_wtf.csrf import CSRFProtect


csrf = CSRFProtect()


def register_error_handlers(app):
    from .shared.database import close_database_connection

    app.teardown_appcontext(lambda exception: close_database_connection())
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.exception("Unhandled application error")
        return render_template("errors/500.html"), 500
