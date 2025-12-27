from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import uuid
import boto3
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar la aplicación Flask
app = Flask(__name__)

# Configuración desde variables de entorno
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/video_platform')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Configuración de CORS
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
CORS(app, origins=CORS_ORIGINS)

# Inicializar extensiones
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Configuración de AWS S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION', 'us-east-1')
)
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', 'video-platform-bucket')

# Modelos de Base de Datos
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    videos = db.relationship('Video', backref='uploader', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    video_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500))
    duration = db.Column(db.Integer)  # Duración en segundos
    size = db.Column(db.BigInteger)   # Tamaño en bytes
    format = db.Column(db.String(20)) # Formato del video
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    
    embed_configs = db.relationship('EmbedConfig', backref='video', lazy=True)

class EmbedConfig(db.Model):
    __tablename__ = 'embed_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    width = db.Column(db.Integer, default=800)
    height = db.Column(db.Integer, default=450)
    theme = db.Column(db.String(20), default='default')
    controls = db.Column(db.Boolean, default=True)
    autoplay = db.Column(db.Boolean, default=False)
    loop = db.Column(db.Boolean, default=False)
    preload = db.Column(db.String(10), default='metadata')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Funciones de utilidad
def upload_to_s3(file, filename):
    """Subir archivo a S3"""
    try:
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            filename,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': file.content_type
            }
        )
        return f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}"
    except Exception as e:
        logger.error(f"Error uploading to S3: {e}")
        return None

def generate_unique_slug(title):
    """Generar slug único para el video"""
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    while Video.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug

# Rutas de la API

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registrar un nuevo usuario"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Faltan datos requeridos'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'El nombre de usuario ya existe'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El email ya está registrado'}), 400
    
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Usuario registrado exitosamente'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Iniciar sesión"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Faltan datos requeridos'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }
    }), 200

@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Obtener lista de videos"""
    videos = Video.query.filter_by(is_public=True).all()
    
    return jsonify([{
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'slug': video.slug,
        'thumbnail_url': video.thumbnail_url,
        'duration': video.duration,
        'size': video.size,
        'format': video.format,
        'views': video.views,
        'created_at': video.created_at.isoformat()
    } for video in videos]), 200

@app.route('/api/videos/<int:video_id>', methods=['GET'])
def get_video(video_id):
    """Obtener información de un video específico"""
    video = Video.query.get_or_404(video_id)
    
    if not video.is_public:
        return jsonify({'error': 'Video no disponible'}), 404
    
    video.views += 1
    db.session.commit()
    
    return jsonify({
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'slug': video.slug,
        'video_url': video.video_url,
        'thumbnail_url': video.thumbnail_url,
        'duration': video.duration,
        'size': video.size,
        'format': video.format,
        'views': video.views,
        'created_at': video.created_at.isoformat()
    }), 200

@app.route('/api/videos', methods=['POST'])
@jwt_required()
def upload_video():
    """Subir un nuevo video"""
    current_user_id = get_jwt_identity()
    
    if 'video' not in request.files:
        return jsonify({'error': 'No se proporcionó archivo de video'}), 400
    
    file = request.files['video']
    title = request.form.get('title', 'Video sin título')
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    # Generar nombres de archivo únicos
    filename = secure_filename(file.filename)
    file_extension = filename.split('.')[-1] if '.' in filename else 'mp4'
    unique_filename = f"videos/{uuid.uuid4()}.{file_extension}"
    thumbnail_filename = f"thumbnails/{uuid.uuid4()}.jpg"
    
    # Subir video a S3
    video_url = upload_to_s3(file, unique_filename)
    if not video_url:
        return jsonify({'error': 'Error al subir el video'}), 500
    
    # Crear miniatura (simulación)
    thumbnail_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{thumbnail_filename}"
    
    # Crear registro en la base de datos
    video = Video(
        title=title,
        description=description,
        slug=generate_unique_slug(title),
        video_url=video_url,
        thumbnail_url=thumbnail_url,
        uploader_id=current_user_id
    )
    
    db.session.add(video)
    db.session.commit()
    
    return jsonify({
        'message': 'Video subido exitosamente',
        'video': {
            'id': video.id,
            'title': video.title,
            'slug': video.slug,
            'video_url': video.video_url,
            'thumbnail_url': video.thumbnail_url
        }
    }), 201

@app.route('/api/videos/<int:video_id>/embed', methods=['POST'])
def create_embed_config(video_id):
    """Crear configuración de embed para un video"""
    video = Video.query.get_or_404(video_id)
    
    data = request.get_json()
    
    embed_config = EmbedConfig(
        video_id=video.id,
        width=data.get('width', 800),
        height=data.get('height', 450),
        theme=data.get('theme', 'default'),
        controls=data.get('controls', True),
        autoplay=data.get('autoplay', False),
        loop=data.get('loop', False),
        preload=data.get('preload', 'metadata')
    )
    
    db.session.add(embed_config)
    db.session.commit()
    
    # Generar código iframe
    embed_code = f'<iframe src="/embed/{video.slug}?config={embed_config.id}" width="{embed_config.width}" height="{embed_config.height}" frameborder="0" allowfullscreen></iframe>'
    
    return jsonify({
        'embed_code': embed_code,
        'embed_url': f"/embed/{video.slug}?config={embed_config.id}"
    }), 201

@app.route('/embed/<slug>', methods=['GET'])
def embed_player(slug):
    """Página de embed del reproductor"""
    video = Video.query.filter_by(slug=slug).first_or_404()
    config_id = request.args.get('config')
    
    if config_id:
        config = EmbedConfig.query.get(config_id)
    else:
        config = EmbedConfig(
            width=800,
            height=450,
            theme='default',
            controls=True,
            autoplay=False,
            loop=False,
            preload='metadata'
        )
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{video.title}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ margin: 0; padding: 0; background: #000; }}
            .artplayer-app {{ width: 100%; height: 100vh; }}
        </style>
    </head>
    <body>
        <div class="artplayer-app"></div>
        <script src="https://cdn.jsdelivr.net/npm/artplayer/dist/artplayer.js"></script>
        <script>
            var art = new Artplayer({{
                container: '.artplayer-app',
                url: '{video.video_url}',
                poster: '{video.thumbnail_url}',
                title: '{video.title}',
                fullscreen: true,
                fullscreenWeb: true,
                setting: true,
                pip: true,
                screenshot: true,
                theme: '{config.theme}',
                autoplay: {str(config.autoplay).lower()},
                loop: {str(config.loop).lower()},
                controls: {str(config.controls).lower()},
                preload: '{config.preload}',
                width: {config.width},
                height: {config.height},
            }});
        </script>
    </body>
    </html>
    '''

@app.route('/api/user/videos', methods=['GET'])
@jwt_required()
def get_user_videos():
    """Obtener videos del usuario actual"""
    current_user_id = get_jwt_identity()
    videos = Video.query.filter_by(uploader_id=current_user_id).all()
    
    return jsonify([{
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'slug': video.slug,
        'thumbnail_url': video.thumbnail_url,
        'views': video.views,
        'created_at': video.created_at.isoformat()
    } for video in videos]), 200

@app.route('/api/admin/videos', methods=['GET'])
@jwt_required()
def get_all_videos():
    """Obtener todos los videos (solo administradores)"""
    current_user = User.query.get(get_jwt_identity())
    
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403
    
    videos = Video.query.all()
    
    return jsonify([{
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'slug': video.slug,
        'uploader': video.uploader.username,
        'views': video.views,
        'is_public': video.is_public,
        'created_at': video.created_at.isoformat()
    } for video in videos]), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)