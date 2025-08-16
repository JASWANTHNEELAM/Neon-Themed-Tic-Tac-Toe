from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

SYMBOLS = ["X", "O", "⭐", "❤️", "🐱", "⚡", "🍀", "🌀", "🔥", "🌙"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/setup")
def setup():
    mode = request.args.get("mode", "PvP")
    return render_template("setup.html", mode=mode, symbols=SYMBOLS)

@app.route("/game")
def game():
    mode = request.args.get("mode", "PvP")
    ai_level = request.args.get("ai_level", "easy") if mode == "PvC" else ""
    p1 = request.args.get("p1", "X")
    p2 = request.args.get("p2", "O")

    # basic safety: ensure valid & different symbols
    if p1 not in SYMBOLS:
        p1 = "X"
    if p2 not in SYMBOLS or p2 == p1:
        # pick first different symbol
        for s in SYMBOLS:
            if s != p1:
                p2 = s
                break

    return render_template("game.html", mode=mode, ai_level=ai_level, p1=p1, p2=p2)

if __name__ == "__main__":
    app.run(debug=True)
