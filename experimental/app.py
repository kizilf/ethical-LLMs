from flask import Flask
from src.experiment_page import experiment_routes

app = Flask(__name__)
app.secret_key = "super secret key"  # Weirdly, needed to use flash messages (e.g. showing guidelines are updated message in Experiment page)


# Register routes from other Python files
app.register_blueprint(experiment_routes)

if __name__ == "__main__":
    # Entry point to the application
    app.run(debug=False)
