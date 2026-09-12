from functools import wraps

from flask import flash, redirect, session, url_for


def admin_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Please sign in as an administrator.", "error")
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)

    return wrapped
