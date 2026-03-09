from flask import jsonify, request
from models.attached_school import AttachedSchool
from models.database import db 

class AttachedSchoolsController:
    @staticmethod
    def get_all():
        try:
            attached_schools = AttachedSchool.query.all()
            return jsonify({
                'status': 'success',
                'data': [school.to_dict() for school in attached_schools]
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def get_by_id(id):
        try:
            attached_school = AttachedSchool.query.get(id)
            if not attached_school:
                return jsonify({
                    'status': 'error',
                    'message': 'Attached school not found'
                }), 404
            return jsonify({
                'status': 'success',
                'data': attached_school.to_dict()
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def create():
        try:
            data = request.get_json()
            new_attached_school = AttachedSchool(**data)
            db.session.add(new_attached_school)
            db.session.commit()
            return jsonify({
                'status': 'success',
                'data': new_attached_school.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def update(id):
        try:
            attached_school = AttachedSchool.query.get(id)
            if not attached_school:
                return jsonify({
                    'status': 'error',
                    'message': 'Attached school not found'
                }), 404

            data = request.get_json()
            for key, value in data.items():
                setattr(attached_school, key, value)

            db.session.commit()
            return jsonify({
                'status': 'success',
                'data': attached_school.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def delete(id):
        try:
            attached_school = AttachedSchool.query.get(id)
            if not attached_school:
                return jsonify({
                    'status': 'error',
                    'message': 'Attached school not found'
                }), 404

            db.session.delete(attached_school)
            db.session.commit()
            return jsonify({
                'status': 'success',
                'message': 'Attached school deleted successfully'
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def get_user_attached_schools(current_user):
        try:
            attached_schools = AttachedSchool.query.filter_by(phone_number=current_user.phone_number).all()
            return jsonify({
                'status': 'success',
                'data': [school.to_dict() for school in attached_schools]
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500 