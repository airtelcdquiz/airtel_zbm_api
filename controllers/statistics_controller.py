from flask import jsonify, request
from models.user import User
from models.question_responses import QuestionResponse
from models.school import School
from sqlalchemy import func, or_
from datetime import datetime
from decimal import Decimal

class StatisticsController:
    @staticmethod
    def get_user_points():
        # Récupérer les paramètres
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')

        # Valider les dates
        try:
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Format de date invalide. Utilisez YYYY-MM-DD'}), 400

        # Construire la requête
        query = User.query.join(
            School, User.school_code == School.code
        ).outerjoin(
            QuestionResponse,
            (user.phone_number == QuestionResponse.phone_number) &
            (QuestionResponse.created_at.between(start_date, end_date) if start_date and end_date else True)
        )

        # Ajouter la recherche si spécifiée
        if search:
            query = query.filter(
                or_(
                    User.participant_phone.ilike(f'%{search}%'),
                    User.participant_full_name.ilike(f'%{search}%')
                )
            )

        query = query.with_entities(
            func.coalesce(func.sum(QuestionResponse.points), 0).label('points'),
            User.participant_phone,
            User.participant_full_name,
            School.code.label('school_code'),
            School.schoolname
        ).group_by(
            user.phone_number,
            User.participant_phone,
            User.participant_full_name,
            School.code,
            School.schoolname
        ).order_by(
            func.coalesce(func.sum(QuestionResponse.points), 0).desc()
        )

        # Paginer les résultats
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Formater les résultats
        results = []
        for item in pagination.items:
            # Convertir les valeurs décimales en entiers
            points = int(item.points) if isinstance(item.points, Decimal) else item.points
            
            results.append({
                'points': points,
                'participant_phone': item.participant_phone,
                'participant_full_name': item.participant_full_name,
                'school_code': item.school_code,
                'schoolname': item.schoolname
            })

        return jsonify({
            'results': results,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })