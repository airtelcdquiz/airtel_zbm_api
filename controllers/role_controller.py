from flask import jsonify, request 
from models.role import Role, db
from models.permission import Permission

class RoleController:
    @staticmethod
    def get_all():
        roles = Role.query.all()
        return jsonify([role.to_dict() for role in roles])

    @staticmethod
    def get_by_id(role_id):
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        return jsonify(role.to_dict())

    @staticmethod
    def create():
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400

        if Role.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Role with this name already exists'}), 400

        role = Role(
            name=data['name'],
            description=data.get('description')
        )

        # Ajouter les permissions si spécifiées
        if 'permissions' in data:
            permissions = Permission.query.filter(Permission.id.in_(data['permissions'])).all()
            role.permissions = permissions

        db.session.add(role)
        db.session.commit()

        return jsonify(role.to_dict()), 201

    @staticmethod
    def create_many():
        data = request.get_json()
        
        if not data or not isinstance(data, list):
            return jsonify({'error': 'A list of roles is required'}), 400

        created_roles = []
        errors = []

        for role_data in data:
            if not isinstance(role_data, dict) or 'name' not in role_data:
                errors.append({'error': f'Invalid role data: {role_data}'})
                continue

            if Role.query.filter_by(name=role_data['name']).first():
                errors.append({'error': f'Role with name "{role_data["name"]}" already exists'})
                continue

            try:
                role = Role(
                    name=role_data['name'],
                    description=role_data.get('description')
                )

                # Ajouter les permissions si spécifiées
                if 'permissions' in role_data:
                    permissions = Permission.query.filter(Permission.id.in_(role_data['permissions'])).all()
                    role.permissions = permissions

                db.session.add(role)
                created_roles.append(role)
            except Exception as e:
                errors.append({'error': f'Error creating role {role_data["name"]}: {str(e)}'})

        if created_roles:
            db.session.commit()
            response = {
                'created': [r.to_dict() for r in created_roles],
                'errors': errors if errors else None
            }
            return jsonify(response), 201
        else:
            return jsonify({'errors': errors}), 400

    @staticmethod
    def update(role_id):
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404

        data = request.get_json()
        
        if 'name' in data:
            existing_role = Role.query.filter_by(name=data['name']).first()
            if existing_role and existing_role.id != role_id:
                return jsonify({'error': 'Role with this name already exists'}), 400
            role.name = data['name']

        if 'description' in data:
            role.description = data['description']

        if 'permissions' in data:
            permissions = Permission.query.filter(Permission.id.in_(data['permissions'])).all()
            role.permissions = permissions

        db.session.commit()
        return jsonify(role.to_dict())

    @staticmethod
    def delete(role_id):
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404

        db.session.delete(role)
        db.session.commit()
        return '', 204

    @staticmethod
    def add_permission(role_id, permission_id):
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        permission = Permission.query.get(permission_id)
        if not permission:
            return jsonify({'error': 'Permission not found'}), 404
        if permission in role.permissions:
            return jsonify({'message': 'Permission already assigned to role'}), 200
        role.permissions.append(permission)
        db.session.commit()
        return jsonify({'message': 'Permission added to role'}), 200

    @staticmethod
    def remove_permission(role_id, permission_id):
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        permission = Permission.query.get(permission_id)
        if not permission:
            return jsonify({'error': 'Permission not found'}), 404
        if permission not in role.permissions:
            return jsonify({'message': 'Permission not assigned to role'}), 200
        role.permissions.remove(permission)
        db.session.commit()
        return jsonify({'message': 'Permission removed from role'}), 200 