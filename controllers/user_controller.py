from flask import jsonify, request
from models.user import User, db
from sqlalchemy import or_
from models.attached_school import AttachedSchool

class UserController:
    @staticmethod
    def get_all_users():
        # Récupérer les paramètres de pagination et recherche
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')

        # Récupérer l'utilisateur connecté
        # current_user = request.current_user

        # Construire la requête de base
        query = User.query

        # Si l'utilisateur n'est pas superadmin et n'a pas le rôle admin, filtrer par les écoles attachées
        # if not current_user.is_superuser and 'admin' not in [role.name for role in current_user.roles]:
        #     # Récupérer les IDs des écoles attachées
        #     attached_codes = [attached_school.code for attached_school in current_user.attached_schools_association]
        #     # Filtrer les utilisateurs par les écoles attachées
        #     query = query.filter(User.code.in_(attached_codes))

        # Ajouter la recherche si un terme est fourni
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.like(search_term),
                    User.phone_number.like(search_term),
                    User.school_level.like(search_term),
                    User.school_class.like(search_term)
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
        
        if not data or not data.get('phone_number') or not data.get('name') or not data.get('school_level') or not data.get('school_class'):
            return jsonify({'error': 'Données invalides'}), 400
        
        new_user = User(
            phone_number=data['phone_number'],
            name=data['name'],
            school_level=data['school_level'],
            school_class=data['school_class']
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify(new_user.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    @staticmethod
    def get_user(phone_number):
        # Récupérer les paramètres de recherche
        search = request.args.get('search', '')

        # Construire la requête de base
        query = User.query

        # Ajouter la recherche si un terme est fourni
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.like(search_term),
                    User.phone_number.like(search_term),
                    User.school_level.like(search_term),
                    User.school_class.like(search_term)
                )
            )

        user = query.filter_by(id=phone_number).first_or_404()
        return jsonify(user.to_dict())
    
    @staticmethod
    def get_user_permissions(phone_number):
        user = User.query.filter_by(id=phone_number).first_or_404()
        return jsonify(user.get_all_permissions())
    
    @staticmethod
    def get_user_roles(phone_number):
        user = User.query.filter_by(id=phone_number).first_or_404()
        return jsonify(user.get_all_roles())

    @staticmethod
    def add_permission(phone_number, permission_id):
        user = User.query.filter_by(id=phone_number).first_or_404()
        from models.permission import Permission
        permission = Permission.query.get(permission_id)
        if not permission:
            return jsonify({'error': 'Permission not found'}), 404
        if permission in user.direct_permissions:
            return jsonify({'message': 'Permission already assigned to user'}), 200
        user.direct_permissions.append(permission)
        db.session.commit()
        return jsonify({'message': 'Permission added to user'}), 200

    @staticmethod
    def remove_permission(phone_number, permission_id):
        user = User.query.filter_by(id=phone_number).first_or_404()
        from models.permission import Permission
        permission = Permission.query.get(permission_id)
        if not permission:
            return jsonify({'error': 'Permission not found'}), 404
        if permission not in user.direct_permissions:
            return jsonify({'message': 'Permission not assigned to user'}), 200
        user.direct_permissions.remove(permission)
        db.session.commit()
        return jsonify({'message': 'Permission removed from user'}), 200

    @staticmethod
    def add_role(phone_number, role_id):
        user = User.query.filter_by(id=phone_number).first_or_404()
        from models.role import Role
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        if role in user.roles:
            return jsonify({'message': 'Role already assigned to user'}), 200
        user.roles.append(role)
        db.session.commit()
        return jsonify({'message': 'Role added to user'}), 200

    @staticmethod
    def remove_role(phone_number, role_id):
        user = User.query.filter_by(id=phone_number).first_or_404()
        from models.role import Role
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        if role not in user.roles:
            return jsonify({'message': 'Role not assigned to user'}), 200
        user.roles.remove(role)
        db.session.commit()
        return jsonify({'message': 'Role removed from user'}), 200

    @staticmethod
    def set_superuser(phone_number):
        user = User.query.filter_by(id=phone_number).first_or_404()
        user.is_superuser = True
        db.session.commit()
        return jsonify({'message': 'User set as superuser'}), 200

    @staticmethod
    def unset_superuser(phone_number):
        user = User.query.filter_by(id=phone_number).first_or_404()
        user.is_superuser = False
        db.session.commit()
        return jsonify({'message': 'User unset as superuser'}), 200

    @staticmethod
    def activate_user(phone_number):
        user = User.query.filter_by(id=phone_number).first_or_404()
        if user.is_active:
            return jsonify({'message': 'L\'utilisateur est déjà actif'}), 200
        
        user.is_active = True
        db.session.commit()
        return jsonify({'message': 'Utilisateur activé avec succès', 'user': user.to_dict()}), 200

    @staticmethod
    def deactivate_user(phone_number):
        user = User.query.filter_by(id=phone_number).first_or_404()
        if not user.is_active:
            return jsonify({'message': 'L\'utilisateur est déjà inactif'}), 200
        
        user.is_active = False
        db.session.commit()
        return jsonify({'message': 'Utilisateur désactivé avec succès', 'user': user.to_dict()}), 200