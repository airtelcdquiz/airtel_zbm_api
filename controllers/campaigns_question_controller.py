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
                    CampaignsQuestion.campaign_question.like(search_term),
                    CampaignsQuestion.campaign_value1.like(search_term),
                    CampaignsQuestion.campaign_value2.like(search_term),
                    CampaignsQuestion.campaign_value3.like(search_term),
                    CampaignsQuestion.campaign_value4.like(search_term)
                )
            )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
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
                    CampaignsQuestion.campaign_question.like(search_term),
                    CampaignsQuestion.campaign_value1.like(search_term),
                    CampaignsQuestion.campaign_value2.like(search_term),
                    CampaignsQuestion.campaign_value3.like(search_term),
                    CampaignsQuestion.campaign_value4.like(search_term)
                )
            )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'questions': [q.to_dict() for q in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })


    @staticmethod
    def create_question():
        data = request.get_json()
        if not data or not data.get('campaign_question') or not data.get('campaign_answer'):
            return jsonify({'error': 'Données invalides'}), 400
        new_question = CampaignsQuestion(
            campaign_question=data['campaign_question'],
            campaign_value1=data.get('campaign_value1'),
            campaign_value2=data.get('campaign_value2'),
            campaign_value3=data.get('campaign_value3'),
            campaign_value4=data.get('campaign_value4'),
            campaign_answer=data['campaign_answer'],
            is_active=data.get('is_active', False),
            archived=data.get('archived', False)
        )
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
        data = request.get_json()
        for field in ['campaign_question', 'campaign_value1', 'campaign_value2', 'campaign_value3', 'campaign_value4', 'campaign_answer', 'is_active', 'archived']:
            if field in data:
                setattr(question, field, data[field])
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
                    CampaignsQuestion.campaign_question.like(search_term),
                    CampaignsQuestion.campaign_value1.like(search_term),
                    CampaignsQuestion.campaign_value2.like(search_term),
                    CampaignsQuestion.campaign_value3.like(search_term),
                    CampaignsQuestion.campaign_value4.like(search_term)
                )
            )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
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
                    CampaignsQuestion.campaign_question.like(search_term),
                    CampaignsQuestion.campaign_value1.like(search_term),
                    CampaignsQuestion.campaign_value2.like(search_term),
                    CampaignsQuestion.campaign_value3.like(search_term),
                    CampaignsQuestion.campaign_value4.like(search_term)
                )
            )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'questions': [q.to_dict() for q in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }) 