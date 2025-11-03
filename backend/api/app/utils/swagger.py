from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/swagger'
SWAGGER_STATIC = '/static/swagger.json'
SWAGGER_BLUEPRINT = get_swaggerui_blueprint(SWAGGER_URL, SWAGGER_STATIC, config={
                                            'app_name': 'HydroTwin', 'layout': 'BaseLayout'})
