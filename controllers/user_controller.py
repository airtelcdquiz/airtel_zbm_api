from flask import jsonify, request
from models.user import User, db
from sqlalchemy import or_

class UserController:
    @staticmethod
    def get_all_users():
        # Récupérer les paramètres de pagination et recherche
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')

        # Construire la requête de base
        query = User.query

        # Ajouter la recherche si un terme est fourni
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.participant_full_name.like(search_term),
                    User.participant_phone.like(search_term),
                    User.participant_category.like(search_term),
                    User.participant_class.like(search_term)
                )
            )

        # Paginer les résultats
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })

    @staticmethod
    def create_user():
        data = request.get_json()
        
        if not data or not data.get('participant_phone') or not data.get('participant_full_name') or not data.get('participant_category') or not data.get('participant_class'):
            return jsonify({'error': 'Données invalides'}), 400
        
        new_user = User(
            participant_phone=data['participant_phone'],
            participant_full_name=data['participant_full_name'],
            participant_category=data['participant_category'],
            participant_class=data['participant_class']
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify(new_user.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_user(user_id):
        # Récupérer les paramètres de recherche
        search = request.args.get('search', '')

        # Construire la requête de base
        query = User.query

        # Ajouter la recherche si un terme est fourni
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.participant_full_name.like(search_term),
                    User.participant_phone.like(search_term),
                    User.participant_category.like(search_term),
                    User.participant_class.like(search_term)
                )
            )

        user = query.filter_by(id=user_id).first_or_404()
        return jsonify(user.to_dict())