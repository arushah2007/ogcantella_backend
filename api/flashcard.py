from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin
from api.jwt_authorize import token_required
from model.flashcard import Flashcard
from __init__ import db


flashcard_api = Blueprint('flashcard_api', __name__, url_prefix='/api')

# ✅ Correctly enable CORS with credentials support
CORS(
    flashcard_api,
    resources={r"/*": {"origins": ["http://127.0.0.1:4887", "https://xaviertho.github.io"]}},
    supports_credentials=True
)


api = Api(flashcard_api)

class FlashcardAPI:
    class _CRUD(Resource):
        @token_required()
        @cross_origin(origins=["http://127.0.0.1:4887", "https://xaviertho.github.io"], supports_credentials=True)
  # ✅ Allow credentials
        def post(self):
            """Create a new flashcard."""
            current_user = g.current_user
            data = request.get_json()

            if not data or 'title' not in data or 'content' not in data or 'deck_id' not in data:
                return {'message': 'Title, content, and deck_id are required'}, 400

            flashcard = Flashcard(data['title'], data['content'], current_user.id, data['deck_id'])
            flashcard = flashcard.create()

            if not flashcard:
                return {'message': 'Failed to create flashcard'}, 400

            return jsonify(flashcard.read())

        @token_required()
        @cross_origin(origins=["http://127.0.0.1:4887", "https://xaviertho.github.io"], supports_credentials=True)
        def get(self):
            """Get all flashcards for the current user."""
            current_user = g.current_user
            flashcards = Flashcard.query.filter_by(_user_id=current_user.id).all()
            return jsonify([flashcard.read() for flashcard in flashcards])

        @token_required()
        @cross_origin(origins=["http://127.0.0.1:4887", "https://xaviertho.github.io"], supports_credentials=True)
        def put(self, flashcard_id):
            """Update an existing flashcard."""
            print(f"🔍 Attempting to update Flashcard ID: {flashcard_id}")  # Debug log
            data = request.get_json()
            
            if not data:
                return {'message': 'Request body is missing'}, 400

            flashcard = Flashcard.query.get(flashcard_id)
            if not flashcard:
                print(f"❌ Flashcard ID {flashcard_id} not found in database!")  # Debug log
                return {'message': 'Flashcard not found'}, 404

            if flashcard._user_id != g.current_user.id:
                print(f"❌ Unauthorized update attempt by User ID: {g.current_user.id}")  # Debug log
                return {'message': 'Unauthorized to update this flashcard'}, 403

            # Apply updates
            if 'title' in data:
                flashcard._title = data['title']
            if 'content' in data:
                flashcard._content = data['content']

            db.session.commit()  # Save changes
            print(f"✅ Flashcard ID {flashcard_id} updated successfully!")  # Debug log

            return jsonify(flashcard.read())


        @token_required()
        @cross_origin(origins=["http://127.0.0.1:4887", "https://xaviertho.github.io"], supports_credentials=True)
        def delete(self, flashcard_id):
            """Delete a flashcard."""
            flashcard = Flashcard.query.get(flashcard_id)

            print(f"Attempting to delete Flashcard ID: {flashcard_id}")  # 🔍 Debugging log

            if not flashcard:
                print("Flashcard not found!")  # 🔍 Debugging log
                return {'message': 'Flashcard not found'}, 404

            if flashcard._user_id != g.current_user.id:
                print(f"Unauthorized delete attempt by User ID: {g.current_user.id}")  # 🔍 Debugging log
                return {'message': 'Unauthorized to delete this flashcard'}, 403

            try:
                flashcard.delete()
                return {'message': 'Flashcard deleted successfully'}, 200
            except Exception as e:
                db.session.rollback()
                print(f"Error while deleting flashcard: {e}")  # 🔍 Debugging log
                return {'message': 'Failed to delete flashcard', 'error': str(e)}, 500



    # ✅ Handle OPTIONS requests for preflight
    @flashcard_api.route('/flashcard/<int:flashcard_id>', methods=['OPTIONS'])
    @cross_origin(origins=["http://127.0.0.1:4887", "https://xaviertho.github.io"], supports_credentials=True)
    def flashcard_options(flashcard_id):
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "https://xaviertho.github.io")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return '', 204  # Return an empty 204 response for preflight

api.add_resource(FlashcardAPI._CRUD, '/flashcard', '/flashcard/<int:flashcard_id>')