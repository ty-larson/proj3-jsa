import flask
import logging
from letterbag import LetterBag
from vocab import Vocab
from jumble import jumbled
import config

# Standard Flask application setup
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY 
WORDS = Vocab(CONFIG.VOCAB)

@app.route("/")
@app.route("/index")
def index():
    # Initializes the game state and session variables
    flask.g.vocab = WORDS.as_list()
    flask.session["target_count"] = min(len(flask.g.vocab), CONFIG.SUCCESS_AT_COUNT)
    flask.session["jumble"] = jumbled(flask.g.vocab, flask.session["target_count"])
    flask.session["matches"] = []
    return flask.render_template('vocab.html')

@app.route("/keep_going")
def keep_going():
    # Renders the game page without resetting the jumble
    flask.g.vocab = WORDS.as_list()
    return flask.render_template('vocab.html')

@app.route("/success")
def success():
    # Renders the victory page
    return flask.render_template('success.html')

@app.route("/_check")
def check():
    # AJAX handler to validate words on every keystroke
    text = flask.request.args.get("text", default="", type=str)
    jumble = flask.session.get("jumble")
    matches = flask.session.get("matches", [])
    target_count = flask.session.get("target_count", 0)

    in_jumble = LetterBag(jumble).contains(text)
    matched = WORDS.has(text)
    
    rslt = {
        "is_match": False,
        "message": "",
        "finished": False
    }

    if matched and in_jumble and not (text in matches):
        matches.append(text)
        flask.session["matches"] = matches
        rslt["is_match"] = True
        rslt["message"] = "Correct!"
    elif text in matches:
        rslt["message"] = "You already found '{}'".format(text)
    elif not in_jumble and len(text) > 0:
        rslt["message"] = "'{}' cannot be made from the jumble".format(text)

    if len(matches) >= target_count:
        rslt["finished"] = True

    return flask.jsonify(result=rslt)

@app.errorhandler(404)
def error_404(e):
    return flask.render_template('404.html'), 404

@app.errorhandler(500)
def error_500(e):
    return flask.render_template('500.html'), 500

@app.errorhandler(403)
def error_403(e):
    return flask.render_template('403.html'), 403

if __name__ == "__main__":
    if CONFIG.DEBUG:
        app.debug = True
        app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT, host="0.0.0.0")