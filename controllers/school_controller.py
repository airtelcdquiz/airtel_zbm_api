from flask import jsonify, request
from models.school import School, db
from sqlalchemy import or_

class SchoolController:
    @staticmethod
    def get_all_schools():
        # Récupérer les paramètres de pagination et recherche
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')

        # Construire la requête de base
        query = School.query

        # Ajouter la recherche si un terme est fourni
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    School.schoolname.like(search_term),
                    School.idcode.like(search_term)
                )
            )

        # Paginer les résultats
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'schools': [school.to_dict() for school in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })

    @staticmethod
    def create_school():
        data = request.get_json()
        
        if not data or not data.get('idcode') or not data.get('schoolname'):
            return jsonify({'error': 'Données invalides'}), 400
        
        new_school = School(
            idcode=data['idcode'],
            schoolname=data['schoolname']
        )
        
        try:
            db.session.add(new_school)
            db.session.commit()
            return jsonify(new_school.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_school(school_id):
        school = School.query.get_or_404(school_id)
        return jsonify(school.to_dict())

    @staticmethod
    def update_school(school_id):
        school = School.query.get_or_404(school_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données invalides'}), 400
            
        try:
            if 'idcode' in data:
                school.idcode = data['idcode']
            if 'schoolname' in data:
                school.schoolname = data['schoolname']
                
            db.session.commit()
            return jsonify(school.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def delete_school(school_id):
        school = School.query.get_or_404(school_id)
        try:
            db.session.delete(school)
            db.session.commit()
            return jsonify({'message': 'École supprimée avec succès'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400 