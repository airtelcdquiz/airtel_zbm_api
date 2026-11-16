"""Indicateurs de la page d'accueil du dashboard.

Tout est limité aux écoles visibles par l'utilisateur (toutes pour l'admin
global, sinon ses écoles rattachées) et exclut les administrateurs. Les jours
sont comptés à l'heure de Kinshasa.
"""
from datetime import datetime, timedelta, timezone

from flask import jsonify, request
from sqlalchemy import Date, String, case, cast, func

from controllers.players_controller import POINTS_PER_CORRECT, admin_condition
from models.campaigns_question import CampaignsQuestion
from models.database import db
from models.question_responses import QuestionResponse
from models.school import School
from models.user import User
from utils.access import allowed_school_codes, scope_by_school
from utils.labels import LEVELS, class_label, level_label

TZ = 'Africa/Kinshasa'
KPI_WINDOW = 7


def _day(col):
    return cast(func.timezone(TZ, col), Date)


def _today():
    return (datetime.now(timezone.utc) + timedelta(hours=1)).date()


def _rate(num, den):
    return round(100.0 * num / den, 1) if den else None


def _players(current_user, *cols):
    q = db.session.query(*cols).filter(~admin_condition())
    return scope_by_school(q, User.school_code, current_user)


class DashboardController:
    @staticmethod
    def overview(current_user):
        days = min(max(request.args.get('days', 30, type=int), 7), 90)
        today = _today()
        window = max(days, 2 * KPI_WINDOW)
        start = today - timedelta(days=window - 1)

        players_sq = _players(current_user, User.phone_number).subquery()
        players_total = db.session.query(func.count()).select_from(players_sq).scalar() or 0

        # Inscriptions par jour.
        reg_day = _day(User.created_at)
        reg = dict(
            _players(current_user, reg_day, func.count(User.phone_number))
            .filter(reg_day >= start).group_by(reg_day).all()
        )

        # Questions envoyées / réponses / bonnes réponses par jour.
        qr_day = _day(QuestionResponse.created_date)
        correct_sum = func.sum(case((QuestionResponse.is_correct.is_(True), 1), else_=0))
        qr_rows = (
            db.session.query(qr_day, func.count(QuestionResponse.id), func.count(QuestionResponse.choice), correct_sum)
            .join(players_sq, players_sq.c.phone_number == QuestionResponse.phone_number)
            .filter(qr_day >= start).group_by(qr_day).all()
        )
        qr = {d: (int(s or 0), int(a or 0), int(c or 0)) for d, s, a, c in qr_rows}

        series = []
        for i in range(window):
            d = start + timedelta(days=i)
            s, a, c = qr.get(d, (0, 0, 0))
            series.append({'date': d.isoformat(), 'registrations': int(reg.get(d, 0)),
                           'sent': s, 'answered': a, 'correct': c})

        def totals(chunk):
            return {k: sum(x[k] for x in chunk) for k in ('registrations', 'sent', 'answered', 'correct')}

        cur, prev = totals(series[-KPI_WINDOW:]), totals(series[-2 * KPI_WINDOW:-KPI_WINDOW])

        since = today - timedelta(days=KPI_WINDOW - 1)
        active = (
            db.session.query(func.count(func.distinct(QuestionResponse.phone_number)))
            .join(players_sq, players_sq.c.phone_number == QuestionResponse.phone_number)
            .filter(QuestionResponse.choice.isnot(None), qr_day >= since).scalar() or 0
        )

        # Meilleurs joueurs (tous temps).
        correct_all = func.coalesce(correct_sum, 0)
        top_rows = (
            _players(current_user, User.phone_number, User.name, User.school_level, User.school_class,
                     School.name.label('school_name'), correct_all.label('correct'),
                     func.count(QuestionResponse.choice).label('answered'))
            .outerjoin(School, cast(User.school_code, String) == School.code)
            .outerjoin(QuestionResponse, QuestionResponse.phone_number == User.phone_number)
            .group_by(User.phone_number, User.name, User.school_level, User.school_class, School.name)
            .order_by(correct_all.desc(), User.created_at.asc())
            .limit(5).all()
        )
        top = [{
            'phone_number': r.phone_number, 'name': r.name, 'school_name': r.school_name,
            'level_label': level_label(r.school_level), 'class_label': class_label(r.school_class),
            'points': int(r.correct or 0) * POINTS_PER_CORRECT, 'correct_answers': int(r.correct or 0),
            'answers': int(r.answered or 0),
        } for r in top_rows]

        # Répartition par école.
        school_rows = (
            _players(current_user, User.school_code, School.name, func.count(func.distinct(User.phone_number)),
                     func.count(QuestionResponse.choice), correct_all)
            .outerjoin(School, cast(User.school_code, String) == School.code)
            .outerjoin(QuestionResponse, QuestionResponse.phone_number == User.phone_number)
            .group_by(User.school_code, School.name).all()
        )
        schools = sorted([{
            'code': code, 'name': name or code or 'Sans école', 'players': int(n or 0),
            'answers': int(a or 0), 'success_rate': _rate(int(c or 0), int(a or 0)),
        } for code, name, n, a, c in school_rows], key=lambda s: -s['players'])

        # Répartition par section.
        level_rows = _players(current_user, User.school_level, func.count(User.phone_number)).group_by(User.school_level).all()
        sections = {lbl: 0 for lbl in LEVELS.values()}
        for lvl, n in level_rows:
            lbl = level_label(lvl) or 'Non renseigné'
            sections[lbl] = sections.get(lbl, 0) + int(n or 0)

        return jsonify({
            'today': today.isoformat(),
            'scope': 'all' if allowed_school_codes(current_user) is None else 'schools',
            'kpis': {
                'players_total': players_total,
                'new_players': cur['registrations'], 'new_players_prev': prev['registrations'],
                'active_players': active,
                'participation_rate': _rate(cur['answered'], cur['sent']),
                'participation_rate_prev': _rate(prev['answered'], prev['sent']),
                'success_rate': _rate(cur['correct'], cur['answered']),
                'success_rate_prev': _rate(prev['correct'], prev['answered']),
                'answers': cur['answered'], 'answers_prev': prev['answered'],
                'active_questions': CampaignsQuestion.query.filter_by(is_active=True, archived=False).count(),
                'window_days': KPI_WINDOW,
            },
            'series': series[-days:],
            'top_players': top,
            'schools': schools,
            'sections': [{'label': k, 'count': v} for k, v in sections.items()],
        })
