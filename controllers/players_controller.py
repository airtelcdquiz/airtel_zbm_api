"""Joueurs (participants au quiz) et administrateurs du dashboard.

- Administrateur = superuser OU titulaire d'au moins un rôle.
- Joueur = tout autre utilisateur. Un utilisateur qui devient admin sort
  automatiquement de la liste des joueurs (et du classement / de l'export).
"""
import io
from datetime import datetime, timedelta, timezone

from flask import jsonify, request, send_file
from sqlalchemy import String, case, cast, exists, func, or_

from models.database import db
from models.question_responses import QuestionResponse
from models.school import School
from models.user import User
from models.user_role import user_roles
from models.attached_school import AttachedSchool
from utils.access import scope_by_school
from utils.labels import LEVELS, OPTIONS, class_label, level_label, option_label

POINTS_PER_CORRECT = 10


def admin_condition():
    """Condition SQL : l'utilisateur est administrateur du dashboard."""
    has_role = exists().where(user_roles.c.phone_number == User.phone_number)
    return or_(User.is_superuser.is_(True), has_role)


def _score_subquery():
    return db.session.query(
        QuestionResponse.phone_number.label('phone'),
        func.count(QuestionResponse.id).label('received'),
        func.count(QuestionResponse.choice).label('answered'),
        func.sum(case((QuestionResponse.is_correct.is_(True), 1), else_=0)).label('correct'),
    ).group_by(QuestionResponse.phone_number).subquery()


def _players_query(current_user):
    sc = _score_subquery()
    correct = func.coalesce(sc.c.correct, 0)
    q = db.session.query(
        User,
        School.name.label('school_name'),
        func.coalesce(sc.c.received, 0).label('received'),
        func.coalesce(sc.c.answered, 0).label('answered'),
        correct.label('correct'),
        (correct * POINTS_PER_CORRECT).label('points'),
    ).outerjoin(School, cast(User.school_code, String) == School.code
    ).outerjoin(sc, sc.c.phone == User.phone_number
    ).filter(~admin_condition())

    q = scope_by_school(q, User.school_code, current_user)

    a = request.args
    if a.get('school_level'):
        q = q.filter(cast(User.school_level, String) == a['school_level'])
    if a.get('school_class'):
        q = q.filter(cast(User.school_class, String) == a['school_class'])
    if a.get('school_option'):
        q = q.filter(cast(User.school_option, String) == a['school_option'])
    if a.get('search'):
        term = f"%{a['search']}%"
        q = q.filter(or_(User.name.ilike(term), User.phone_number.ilike(term)))

    sort = a.get('sort', 'recent')
    if sort == 'score':
        q = q.order_by(correct.desc(), User.created_at.asc())
    elif sort == 'name':
        q = q.order_by(func.lower(User.name).asc())
    else:
        q = q.order_by(User.created_at.desc().nullslast())
    return q


def _row_to_dict(row):
    u = row.User
    return {
        'phone_number': u.phone_number,
        'name': u.name,
        'school_code': u.school_code,
        'school_name': row.school_name,
        'school_level': u.school_level,
        'school_class': u.school_class,
        'school_option': u.school_option,
        'level_label': level_label(u.school_level),
        'class_label': class_label(u.school_class),
        'option_label': option_label(u.school_level, u.school_option),
        'is_subscribed': u.is_subscribed,
        'is_active': u.is_active,
        'created_at': u.created_at.isoformat() if u.created_at else None,
        'questions_received': int(row.received or 0),
        'answers': int(row.answered or 0),
        'correct_answers': int(row.correct or 0),
        'points': int(row.points or 0),
    }


class PlayersController:
    @staticmethod
    def list_players(current_user):
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 200)
        pagination = _players_query(current_user).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'players': [_row_to_dict(r) for r in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
        })

    @staticmethod
    def labels(current_user):
        return jsonify({
            'levels': [{'value': k, 'label': v} for k, v in LEVELS.items()],
            'options': [{'value': k, 'label': v} for k, v in OPTIONS.items()],
        })

    @staticmethod
    def export_players(current_user):
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        from openpyxl.utils import get_column_letter

        rows = [_row_to_dict(r) for r in _players_query(current_user).all()]

        wb = Workbook()
        ws = wb.active
        ws.title = "Joueurs"
        headers = [
            ("Téléphone", 'phone_number'), ("Nom", 'name'),
            ("Code école", 'school_code'), ("École", 'school_name'),
            ("Section", 'level_label'), ("Classe", 'class_label'), ("Option", 'option_label'),
            ("Score (points)", 'points'), ("Bonnes réponses", 'correct_answers'),
            ("Réponses données", 'answers'), ("Questions reçues", 'questions_received'),
            ("Abonné", 'is_subscribed'), ("Actif", 'is_active'),
            ("Date d'inscription", 'created_at'),
        ]
        ws.append([h for h, _ in headers])
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="E40000")

        for r in rows:
            line = []
            for _, key in headers:
                v = r.get(key)
                if key == 'created_at' and v:
                    # Excel ne gère pas les fuseaux : heure de Kinshasa (UTC+1).
                    dt = datetime.fromisoformat(v)
                    if dt.tzinfo:
                        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
                    v = dt + timedelta(hours=1)
                elif key in ('is_subscribed', 'is_active'):
                    v = "Oui" if v else "Non"
                elif key == 'phone_number' and v:
                    v = str(v)
                line.append(v)
            ws.append(line)

        date_col = len(headers)
        for row in ws.iter_rows(min_row=2, min_col=date_col, max_col=date_col):
            for c in row:
                c.number_format = 'DD/MM/YYYY HH:MM'
        widths = [16, 30, 12, 26, 18, 12, 16, 14, 15, 16, 16, 9, 8, 18]
        for i, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = w
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        name = f"joueurs-airtel-quiz-{datetime.now().strftime('%Y%m%d-%H%M')}.xlsx"
        return send_file(
            buf, as_attachment=True, download_name=name,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    @staticmethod
    def list_admins(current_user):
        q = db.session.query(User, School.name.label('school_name')).outerjoin(
            School, cast(User.school_code, String) == School.code
        ).filter(admin_condition())
        search = request.args.get('search')
        if search:
            term = f"%{search}%"
            q = q.filter(or_(User.name.ilike(term), User.phone_number.ilike(term)))
        q = q.order_by(User.is_superuser.desc(), func.lower(User.name))

        out = []
        for row in q.all():
            u = row.User
            attached = [a.code for a in AttachedSchool.query.filter_by(phone_number=u.phone_number).all()]
            out.append({
                'phone_number': u.phone_number,
                'name': u.name,
                'school_code': u.school_code,
                'school_name': row.school_name,
                'is_superuser': bool(u.is_superuser),
                'type': "Admin global" if u.is_superuser else "Admin d'école",
                'roles': u.get_all_roles(),
                'attached_schools': attached,
                'is_active': u.is_active,
                'created_at': u.created_at.isoformat() if u.created_at else None,
            })
        return jsonify({'admins': out, 'total': len(out)})
