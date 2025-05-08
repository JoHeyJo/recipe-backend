from environment import Development, Production, os

def set_environment(app):
    if "ENV" not in os.environ:
        app.config["ENV"] = "DEVELOPMENT"

    if app.config['ENV'] == "DEVELOPMENT":
        app.config.from_object(Development)

    if app.config['ENV'] == "PRODUCTION":
        app.config.from_object(Production)
