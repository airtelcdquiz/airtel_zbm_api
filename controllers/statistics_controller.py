from flask import jsonify, request
from models.user import User
from models.question_responses import QuestionResponse
from models.school import School
from models.attached_school import AttachedSchool
from sqlalchemy import func, or_, case, cast, String
from datetime import datetime
from decimal import Decimal


def _is_admin(user):
    """Un admin/superuser voit toutes les écoles."""
    if getattr(user, 'is_superuser', False):
        return True
    return any(r.name == 'admin' for r in user.roles)


def _allowed_school_codes(user):
    """Codes des écoles rattachées à l'utilisateur (liste vide s'il n'en a aucune)."""
    return [a.code for a in AttachedSchool.query.filter_by(phone_number=user.phone_number).all()]


class StatisticsController:
    @staticmethod
    def get_user_points(current_user):
        # Paramètres
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        f_school = request.args.get('school_code')
        f_level = request.args.get('school_level')
        f_class = request.args.get('school_class')
        f_option = request.args.get('school_option')

        # Valider les dates
        try:
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Format de date invalide. Utilisez YYYY-MM-DD'}), 400

        empty = {'results': [], 'total': 0, 'pages': 0, 'current_page': page}

        # Portée : admin -> toutes les écoles ; sinon -> écoles rattachées.
        admin = _is_admin(current_user)
        allowed = None
        if not admin:
            allowed = _allowed_school_codes(current_user)
            if not allowed:
                # Aucun droit sur aucune école : rien à afficher.
                return jsonify(empty)

        # Construire la requête
        query = User.query.join(
            School, User.school_code == School.code
        ).outerjoin(
            QuestionResponse,
            (User.phone_number == QuestionResponse.phone_number) &
            (QuestionResponse.created_at.between(start_date, end_date) if start_date and end_date else True)
        )

        # Restriction par écoles autorisées (jamais élargie par un filtre).
        if allowed is not None:
            query = query.filter(cast(User.school_code, String).in_([str(c) for c in allowed]))

        # Filtres facultatifs (cast en texte : robuste que la colonne soit
        # INTEGER en base ou String dans le modèle).
        if f_school:
            query = query.filter(cast(User.school_code, String) == str(f_school))
        if f_level:
            query = query.filter(cast(User.school_level, String) == str(f_level))
        if f_class:
            query = query.filter(cast(User.school_class, String) == str(f_class))
        if f_option:
            query = query.filter(cast(User.school_option, String) == str(f_option))

        if search:
            query = query.filter(
                or_(
                    User.phone_number.ilike(f'%{search}%'),
                    User.name.ilike(f'%{search}%')
                )
            )

        points_case = func.coalesce(
            func.sum(case((QuestionResponse.is_correct == True, 10), else_=0)),
            0
        )
        query = query.with_entities(
            points_case.label('points'),
            User.phone_number,
            User.name,
            School.code,
            School.name.label('schoolname')
        ).group_by(
            User.phone_number, User.name, School.code, School.name
        ).order_by(points_case.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        results = []
        for item in pagination.items:
            points = int(item.points) if isinstance(item.points, Decimal) else item.points
            results.append({
                'points': points,
                'phone_number': item.phone_number,
                'name': item.name,
                'code': item.code,
                'schoolname': item.schoolname
            })

        return jsonify({
            'results': results,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })

    @staticmethod
    def get_filters(current_user):
        """Valeurs disponibles pour les filtres du classement, limitées à la
        portée de l'utilisateur (toutes les écoles pour un admin, sinon ses
        écoles rattachées)."""
        admin = _is_admin(current_user)

        if admin:
            schools = School.query.order_by(School.name).all()
            base = User.query
        else:
            allowed = _allowed_school_codes(current_user)
            if not allowed:
                return jsonify({'schools': [], 'levels': [], 'classes': [], 'options': []})
            schools = School.query.filter(
                cast(School.code, String).in_([str(c) for c in allowed])
            ).order_by(School.name).all()
            base = User.query.filter(cast(User.school_code, String).in_([str(c) for c in allowed]))

        def distinct_values(column):
            rows = base.with_entities(column).distinct().all()
            vals = [r[0] for r in rows if r[0] is not None and str(r[0]).strip() != '']
            return sorted(vals, key=lambda v: str(v))

        return jsonify({
            'schools': [{'code': s.code, 'name': s.name} for s in schools],
            'levels': distinct_values(User.school_level),
            'classes': distinct_values(User.school_class),
            'options': distinct_values(User.school_option),
        })
