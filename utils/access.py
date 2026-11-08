"""Contrôle d'accès commun.

Règles :
- Admin global = utilisateur `is_superuser`. Il voit toutes les écoles et peut
  filtrer sur une école via le paramètre `school_code`.
- Tout autre utilisateur (ex. rôle `admin` d'école) ne voit que les écoles qui
  lui sont rattachées (table `attached_schools`). Un filtre `school_code` ne
  peut que restreindre cette portée, jamais l'élargir.
- Les opérations qui donnent des droits (superuser, rôles, permissions,
  rattachements d'écoles) et la gestion des écoles sont réservées à l'admin
  global.
"""
from functools import wraps

from flask import jsonify, request
from sqlalchemy import String, cast

from models.attached_school import AttachedSchool


def is_global_admin(user):
    return bool(getattr(user, 'is_superuser', False))


def allowed_school_codes(user):
    """None = toutes les écoles ; sinon liste (éventuellement vide) de codes."""
    if is_global_admin(user):
        return None
    rows = AttachedSchool.query.filter_by(phone_number=user.phone_number).all()
    return [str(a.code) for a in rows]


def scope_by_school(query, column, user, school_code=None):
    """Restreint `query` aux écoles visibles par `user`, puis applique le
    filtre facultatif `school_code` (par défaut lu dans la requête HTTP)."""
    if school_code is None:
        school_code = request.args.get('school_code') or None
    allowed = allowed_school_codes(user)
    col = cast(column, String)
    if allowed is not None:
        # in_([]) renvoie une requête vide : aucun rattachement = aucune donnée.
        query = query.filter(col.in_(allowed))
    if school_code:
        query = query.filter(col == str(school_code))
    return query


def can_access_school(user, code):
    allowed = allowed_school_codes(user)
    return allowed is None or str(code) in allowed


def superuser_required(f):
    """À placer SOUS @AuthController.token_required."""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not is_global_admin(current_user):
            return jsonify({'error': 'Réservé à l\'administrateur global'}), 403
        return f(current_user, *args, **kwargs)
    return decorated
