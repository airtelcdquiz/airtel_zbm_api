from flask import jsonify, request
from models.campaigns_question import CampaignsQuestion, db
from sqlalchemy import or_

class CampaignsQuestionController:
    @staticmethod
    def get_all_questions():
        # Pagination et recherche
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')

        query = CampaignsQuestion.query.filter_by(archived=False)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    CampaignsQuestion.question.ilike(search_term),
                    CampaignsQuestion.option_1.ilike(search_term),
                    CampaignsQuestion.option_2.ilike(search_term),
                    CampaignsQuestion.option_3.ilike(search_term),
                    CampaignsQuestion.option_4.ilike(search_term)
                )
            )
        pagination = query.order_by(CampaignsQuestion.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'questions': [q.to_dict() for q in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })

    @staticmethod
    def get_archived_questions():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')

        query = CampaignsQuestion.query.filter_by(archived=True)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    CampaignsQuestion.question.ilike(search_term),
                    CampaignsQuestion.option_1.ilike(search_term),
                    CampaignsQuestion.option_2.ilike(search_term),
                    CampaignsQuestion.option_3.ilike(search_term),
                    CampaignsQuestion.option_4.ilike(search_term)
                )
            )
        pagination = query.order_by(CampaignsQuestion.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'questions': [q.to_dict() for q in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })


    @staticmethod
    def _validate(data, partial=False):
        """Renvoie (champs nettoyés, erreur). `response` = numéro 1-4 de la
        bonne option ; `campaign_answer` est accepté comme ancien nom."""
        if 'campaign_answer' in data and 'response' not in data:
            data['response'] = data['campaign_answer']
        clean = {}
        for f in ('question', 'option_1', 'option_2', 'option_3', 'option_4'):
            if f in data:
                v = (data[f] or '').strip()
                if not v:
                    return None, f"Le champ {f} est obligatoire"
                if len(v) > 255:
                    return None, f"Le champ {f} dépasse 255 caractères"
                clean[f] = v
            elif not partial:
                return None, f"Le champ {f} est obligatoire"
        if 'response' in data:
            if str(data['response']) not in ('1', '2', '3', '4'):
                return None, "La bonne réponse doit être 1, 2, 3 ou 4"
            clean['response'] = str(data['response'])
        elif not partial:
            return None, "La bonne réponse est obligatoire"
        for f in ('is_active', 'archived'):
            if f in data:
                clean[f] = bool(data[f])
        return clean, None

    @staticmethod
    def create_question():
        data = request.get_json(silent=True) or {}
        clean, err = CampaignsQuestionController._validate(data)
        if err:
            return jsonify({'error': err}), 400
        clean.setdefault('is_active', False)
        clean.setdefault('archived', False)
        new_question = CampaignsQuestion(**clean)
        try:
            db.session.add(new_question)
            db.session.commit()
            return jsonify(new_question.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_question(question_id):
        question = CampaignsQuestion.query.filter_by(id=question_id).first()
        if not question:
            return jsonify({'error': 'Question non trouvée'}), 404
        return jsonify(question.to_dict())

    @staticmethod
    def update_question(question_id):
        question = CampaignsQuestion.query.filter_by(id=question_id).first()
        if not question:
            return jsonify({'error': 'Question non trouvée'}), 404
        data = request.get_json(silent=True) or {}
        clean, err = CampaignsQuestionController._validate(data, partial=True)
        if err:
            return jsonify({'error': err}), 400
        for field, value in clean.items():
            setattr(question, field, value)
        try:
            db.session.commit()
            return jsonify(question.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def delete_question(question_id):
        question = CampaignsQuestion.query.filter_by(id=question_id).first()
        if not question:
            return jsonify({'error': 'Question non trouvée'}), 404
        try:
            db.session.delete(question)
            db.session.commit()
            return jsonify({'message': 'Question supprimée'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_active_questions():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')

        query = CampaignsQuestion.query.filter_by(is_active=True).filter_by(archived=False)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    CampaignsQuestion.question.ilike(search_term),
                    CampaignsQuestion.option_1.ilike(search_term),
                    CampaignsQuestion.option_2.ilike(search_term),
                    CampaignsQuestion.option_3.ilike(search_term),
                    CampaignsQuestion.option_4.ilike(search_term)
                )
            )
        pagination = query.order_by(CampaignsQuestion.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'questions': [q.to_dict() for q in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })

    @staticmethod
    def get_inactive_questions():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')

        query = CampaignsQuestion.query.filter_by(is_active=False).filter_by(archived=False)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    CampaignsQuestion.question.ilike(search_term),
                    CampaignsQuestion.option_1.ilike(search_term),
                    CampaignsQuestion.option_2.ilike(search_term),
                    CampaignsQuestion.option_3.ilike(search_term),
                    CampaignsQuestion.option_4.ilike(search_term)
                )
            )
        pagination = query.order_by(CampaignsQuestion.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'questions': [q.to_dict() for q in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }) 