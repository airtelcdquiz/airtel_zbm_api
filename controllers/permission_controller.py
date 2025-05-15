from flask import jsonify, request
from models.permission import Permission, db

class PermissionController:
    @staticmethod
    def get_all():
        permissions = Permission.query.all()
        return jsonify([permission.to_dict() for permission in permissions])

    @staticmethod
    def get_by_id(permission_id):
        permission = Permission.query.get(permission_id)
        if not permission:
            return jsonify({'error': 'Permission not found'}), 404
        return jsonify(permission.to_dict())

    @staticmethod
    def create():
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400

        if Permission.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Permission with this name already exists'}), 400

        permission = Permission(
            name=data['name'],
            description=data.get('description')
        )

        db.session.add(permission)
        db.session.commit()

        return jsonify(permission.to_dict()), 201

    @staticmethod
    def create_many():
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': 'A list of permissions is required'}), 400

        created_permissions = []
        errors = []

        for permission_data in data:
            if not isinstance(permission_data, dict) or 'name' not in permission_data:
                errors.append({'error': f'Invalid permission data: {permission_data}'})
                continue

            if Permission.query.filter_by(name=permission_data['name']).first():
                errors.append({'error': f'Permission with name "{permission_data["name"]}" already exists'})
                continue

            try:
                permission = Permission(
                    name=permission_data['name'],
                    description=permission_data.get('description')
                )
                db.session.add(permission)
                created_permissions.append(permission)
            except Exception as e:
                errors.append({'error': f'Error creating permission {permission_data["name"]}: {str(e)}'})

        if created_permissions:
            db.session.commit()
            response = {
                'created': [p.to_dict() for p in created_permissions],
                'errors': errors if errors else None
            }
            return jsonify(response), 201
        else:
            return jsonify({'errors': errors}), 400

    @staticmethod
    def update(permission_id):
        permission = Permission.query.get(permission_id)
        if not permission:
            return jsonify({'error': 'Permission not found'}), 404

        data = request.get_json()
        
        if 'name' in data:
            existing_permission = Permission.query.filter_by(name=data['name']).first()
            if existing_permission and existing_permission.id != permission_id:
                return jsonify({'error': 'Permission with this name already exists'}), 400
            permission.name = data['name']

        if 'description' in data:
            permission.description = data['description']

        db.session.commit()
        return jsonify(permission.to_dict())

    @staticmethod
    def delete(permission_id):
        permission = Permission.query.get(permission_id)
        if not permission:
            return jsonify({'error': 'Permission not found'}), 404

        db.session.delete(permission)
        db.session.commit()
        return '', 204 