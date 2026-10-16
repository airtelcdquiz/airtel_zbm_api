"""Crée le rôle « responsable_ecole » et la permission « show_classement ».

Idempotent : peut être relancé sans dupliquer. À exécuter une fois après
déploiement, dans le conteneur de l'API :

    python -m scripts.create_school_manager_role

Le rôle donne accès au menu Classements (permission show_classement). La
portée est ensuite déterminée par les écoles rattachées à l'utilisateur
(table attached_schools) : il ne voit que le classement de ces écoles.
"""
from models.database import db
from models.role import Role
from models.permission import Permission
from app import create_app


def run():
    app = create_app()
    with app.app_context():
        perm = Permission.query.filter_by(name='show_classement').first()
        if not perm:
            perm = Permission('show_classement', 'Consulter les classements')
            db.session.add(perm)
            db.session.commit()
            print("Permission 'show_classement' créée.")
        else:
            print("Permission 'show_classement' déjà présente.")

        role = Role.query.filter_by(name='responsable_ecole').first()
        if not role:
            role = Role('responsable_ecole',
                        "Responsable d'école : accès au classement de ses écoles rattachées")
            db.session.add(role)
            db.session.commit()
            print("Rôle 'responsable_ecole' créé.")
        else:
            print("Rôle 'responsable_ecole' déjà présent.")

        if perm not in role.permissions:
            role.permissions.append(perm)
            db.session.commit()
            print("Permission 'show_classement' attachée au rôle.")
        else:
            print("Le rôle a déjà la permission 'show_classement'.")

        print("OK : rôle responsable_ecole prêt.")


if __name__ == '__main__':
    run()
