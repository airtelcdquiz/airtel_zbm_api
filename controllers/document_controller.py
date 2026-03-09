import os
from werkzeug.utils import secure_filename
from models.document import Document
from models.database import db
from datetime import datetime
from sqlalchemy import desc, or_
from worker.document_worker import process_document

UPLOAD_FOLDER = 'uploads/documents'
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_document(file, name, description, phone_number):
    if not file or not allowed_file(file.filename):
        return None, "Format de fichier non autorisé. Seuls les fichiers PDF sont acceptés."

    try:
        # Créer le dossier d'upload s'il n'existe pas
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Sécuriser le nom du fichier
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        # Sauvegarder le fichier
        file.save(file_path)

        # Créer l'enregistrement dans la base de données
        document = Document(
            name=name,
            description=description,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            uploaded_by=phone_number,
            processing_status='pending'  # Nouveau statut
        )

        db.session.add(document)
        db.session.commit()

        # Ajouter le document à la file d'attente de traitement
        process_document.delay(document.id)

        return document, None
    except Exception as e:
        return None, str(e)

def get_document(document_id):
    return Document.query.get(document_id)

def get_all_documents(page=1, per_page=10, sort_by='created_at', sort_order='desc', search=None):
    """
    Récupère tous les documents avec pagination, tri et recherche
    
    Args:
        page (int): Numéro de la page (commence à 1)
        per_page (int): Nombre d'éléments par page
        sort_by (str): Colonne de tri ('created_at', 'name', 'file_size')
        sort_order (str): Ordre de tri ('asc' ou 'desc')
        search (str): Terme de recherche pour le nom et la description
    
    Returns:
        dict: Résultats paginés avec informations de pagination
    """
    # Validation des paramètres de tri
    valid_sort_columns = ['created_at', 'name', 'file_size']
    if sort_by not in valid_sort_columns:
        sort_by = 'created_at'
    
    # Construction de la requête de base
    query = Document.query
    
    # Application de la recherche si un terme est fourni
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Document.name.ilike(search_term),
                Document.description.ilike(search_term)
            )
        )
    
    # Application du tri
    sort_column = getattr(Document, sort_by)
    if sort_order.lower() == 'asc':
        query = query.order_by(sort_column)
    else:
        query = query.order_by(desc(sort_column))
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }

def get_user_documents(phone_number, page=1, per_page=10, sort_by='created_at', sort_order='desc', search=None):
    """
    Récupère les documents d'un utilisateur avec pagination, tri et recherche
    
    Args:
        phone_number (int): ID de l'utilisateur
        page (int): Numéro de la page (commence à 1)
        per_page (int): Nombre d'éléments par page
        sort_by (str): Colonne de tri ('created_at', 'name', 'file_size')
        sort_order (str): Ordre de tri ('asc' ou 'desc')
        search (str): Terme de recherche pour le nom et la description
    
    Returns:
        dict: Résultats paginés avec informations de pagination
    """
    # Validation des paramètres de tri
    valid_sort_columns = ['created_at', 'name', 'file_size']
    if sort_by not in valid_sort_columns:
        sort_by = 'created_at'
    
    # Construction de la requête de base avec filtre utilisateur
    query = Document.query.filter_by(uploaded_by=phone_number)
    
    # Application de la recherche si un terme est fourni
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Document.name.ilike(search_term),
                Document.description.ilike(search_term)
            )
        )
    
    # Application du tri
    sort_column = getattr(Document, sort_by)
    if sort_order.lower() == 'asc':
        query = query.order_by(sort_column)
    else:
        query = query.order_by(desc(sort_column))
    
    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }

def delete_document(document_id):
    document = Document.query.get(document_id)
    if document:
        try:
            # Supprimer le fichier physique
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # Supprimer l'enregistrement de la base de données
            db.session.delete(document)
            db.session.commit()
            return True, None
        except Exception as e:
            return False, str(e)
    return False, "Document non trouvé" 