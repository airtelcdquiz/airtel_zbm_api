from flask import Blueprint, request, jsonify, send_file
from controllers.document_controller import (
    create_document,
    get_document,
    get_all_documents,
    get_user_documents,
    delete_document
)
from controllers.auth_controller import AuthController
import os

document_bp = Blueprint('documents', __name__)

@document_bp.route('/api/documents', methods=['POST'])
@AuthController.token_required
def upload_document(current_user):
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier n\'a été envoyé'}), 400
    
    file = request.files['file']
    name = request.form.get('name', file.filename)
    description = request.form.get('description', '')

    document, error = create_document(file, name, description, current_user.id)
    if error:
        return jsonify({'error': error}), 400

    return jsonify(document.to_dict()), 201

@document_bp.route('/api/documents', methods=['GET'])
@AuthController.token_required
def list_documents(current_user):
    # Récupération des paramètres de pagination, tri et recherche
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    search = request.args.get('search', '').strip()

    # Validation des paramètres
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:  # Limite maximale de 100 éléments par page
        per_page = 10

    result = get_all_documents(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search if search else None
    )

    return jsonify({
        'items': [doc.to_dict() for doc in result['items']],
        'total': result['total'],
        'pages': result['pages'],
        'current_page': result['current_page'],
        'per_page': result['per_page'],
        'has_next': result['has_next'],
        'has_prev': result['has_prev']
    })

@document_bp.route('/api/documents/user', methods=['GET'])
@AuthController.token_required
def list_user_documents(current_user):
    # Récupération des paramètres de pagination, tri et recherche
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    search = request.args.get('search', '').strip()

    # Validation des paramètres
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:  # Limite maximale de 100 éléments par page
        per_page = 10

    result = get_user_documents(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search if search else None
    )

    return jsonify({
        'items': [doc.to_dict() for doc in result['items']],
        'pagination': {
            'total': result['total'],
            'pages': result['pages'],
            'current_page': result['current_page'],
            'per_page': result['per_page'],
            'has_next': result['has_next'],
            'has_prev': result['has_prev']
        }
    })

@document_bp.route('/api/documents/<int:document_id>', methods=['GET'])
@AuthController.token_required
def get_document_file(current_user, document_id):
    document = get_document(document_id)
    if not document:
        return jsonify({'error': 'Document non trouvé'}), 404

    if not os.path.exists(document.file_path):
        return jsonify({'error': 'Fichier non trouvé'}), 404

    return send_file(
        document.file_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=document.name
    )

@document_bp.route('/api/documents/<int:document_id>', methods=['DELETE'])
@AuthController.token_required
def remove_document(current_user, document_id):
    success, error = delete_document(document_id)
    if not success:
        return jsonify({'error': error}), 400
    return jsonify({'message': 'Document supprimé avec succès'}) 