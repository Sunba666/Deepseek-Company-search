# -*- coding: utf-8 -*-
from .main import bp as main_bp
from .company import bp as company_bp
from .compare import bp as compare_bp
from .config import bp as config_bp


def register_blueprints(app):
  app.register_blueprint(main_bp)
  app.register_blueprint(company_bp)
  app.register_blueprint(compare_bp)
  app.register_blueprint(config_bp)
