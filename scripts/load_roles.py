from models.database import db
from models.role import Role
from models.permission import Permission
from app import create_app

def load_default_roles_and_permissions():
    app = create_app()
    with app.app_context():
        # Création des permissions
        permissions = {
            # Permissions pour la gestion des utilisateurs
            'user_manage': Permission('user_manage', 'Gérer les utilisateurs'),
            'user_view': Permission('user_view', 'Voir les utilisateurs'),
            'user_create': Permission('user_create', 'Créer des utilisateurs'),
            'user_edit': Permission('user_edit', 'Modifier des utilisateurs'),
            'user_delete': Permission('user_delete', 'Supprimer des utilisateurs'),
            
            # Permissions pour la gestion des quiz
            'quiz_manage': Permission('quiz_manage', 'Gérer les quiz'),
            'quiz_view': Permission('quiz_view', 'Voir les quiz'),
            'quiz_create': Permission('quiz_create', 'Créer des quiz'),
            'quiz_edit': Permission('quiz_edit', 'Modifier des quiz'),
            'quiz_delete': Permission('quiz_delete', 'Supprimer des quiz'),
            
            # Permissions pour la gestion des écoles
            'school_manage': Permission('school_manage', 'Gérer les écoles'),
            'school_view': Permission('school_view', 'Voir les écoles'),
            'school_create': Permission('school_create', 'Créer des écoles'),
            'school_edit': Permission('school_edit', 'Modifier des écoles'),
            'school_delete': Permission('school_delete', 'Supprimer des écoles'),
            
            # Permissions pour les rapports
            'report_view': Permission('report_view', 'Voir les rapports'),
            'report_export': Permission('report_export', 'Exporter les rapports'),
        }

        # Sauvegarde des permissions
        for permission in permissions.values():
            db.session.add(permission)
        db.session.commit()

        # Création des rôles avec leurs permissions
        roles = {
            'admin': Role('admin', 'Administrateur système avec tous les droits'),
            'teacher': Role('teacher', 'Enseignant avec accès aux quiz et rapports'),
            'student': Role('student', 'Étudiant avec accès limité aux quiz'),
        }

        # Attribution des permissions aux rôles
        roles['admin'].permissions = list(permissions.values())  # Admin a toutes les permissions
        
        roles['teacher'].permissions = [
            permissions['user_view'],
            permissions['quiz_manage'],
            permissions['quiz_view'],
            permissions['quiz_create'],
            permissions['quiz_edit'],
            permissions['report_view'],
            permissions['report_export'],
        ]
        
        roles['student'].permissions = [
            permissions['quiz_view'],
            permissions['report_view'],
        ]

        # Sauvegarde des rôles
        for role in roles.values():
            db.session.add(role)
        db.session.commit()

        print("Rôles et permissions chargés avec succès!")

if __name__ == '__main__':
    load_default_roles_and_permissions() 