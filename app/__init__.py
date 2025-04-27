from flask import Flask
from flasgger import Swagger
from swagger_config import swagger_template
from .auth import auth_bp



# In app/__init__.py
from flask import Flask
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    app.config['SWAGGER'] = {
        'title': 'CoinGecko API',
        'uiversion': 3
    }
    swagger = Swagger(app)
    
    # Register the main blueprint
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
