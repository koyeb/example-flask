from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = "change-this-to-a-long-random-string"  # required for sessions

# Maps a stable logical name (used in templates) to the actual on-disk folder
# under static/asset/images/. Rename a folder on disk, update it here once,
# and every template that references it via img() keeps working.
IMAGE_FOLDERS = {
    "about": "about",
    "art_direction": "art direction",
    "client": "client",
    "fish": "fish",
    "illustration": "illustration",
    "other": "other",
    "portal": "portal",
    "processing": "processing",
    "recit": "recit",
    "self": "self",
    "street": "street",
    "ux": "ux",
}


@app.context_processor
def inject_image_helper():
    def img(folder, filename=""):
        real_folder = IMAGE_FOLDERS.get(folder, folder)
        path = f"asset/images/{real_folder}/{filename}".rstrip("/")
        return url_for("static", filename=path)

    return dict(img=img)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        finder = request.form.get("finder", "").strip().lower()

        personal_websites = ["afvs", "essays", "fysemr", "gifafvs", "illustration", "portal", "street", "superface"]
        collab_websites = ["highlander", "recit", "olympics"]
        flat = ["about", "collab", "cs171", "personal"]

        # ✅ If user types "t4sg" (or similar), send them to the t4sg page
        if finder in ["t4sg", "t4sg.html", "t4sg case study", "2feet", "t4sg x 2feet","2feet prosthetics", "tech 4 social good", "2ft"]:
            return render_template("t4sg.html")

        if finder in ["commonspirit", "common spirit", "commonspirit health", "common spirit health", "t4sg x commonspirit"]:
            return render_template("commonspirit.html")

        if finder in flat:
            return render_template(f"{finder}.html")
        elif finder in personal_websites:
            return render_template(f"personal websites/{finder}.html")
        elif finder in collab_websites:
            return render_template(f"collab websites/{finder}.html")

        elif finder in ["chi", "pirenily", "me", "chi le", "emily", "iron pig", "chi bell", "myself", "i", "artist"]:
            return render_template("about.html")
        elif finder in ["commission", "client work", "commissioned work", "commissions", "client",
                        "collaborative work", "collaborations", "collaboration", "member", "film",
                        "direction", "director", "collab", "graphic design", "clubs", "club", "design"]:
            return render_template("collab.html")
        elif finder in ["personal work", "self", "person", "mine", "free", "journey", "play"]:
            return render_template("personal.html")

        else:
            finder = random.choice(personal_websites + collab_websites + flat)
            if finder in personal_websites:
                return render_template(f"personal websites/{finder}.html")
            elif finder in collab_websites:
                return render_template(f"collab websites/{finder}.html")
            else:
                return render_template(f"{finder}.html")


@app.route("/t4sg")
def t4sg():
    return render_template("t4sg.html")


@app.route("/commonspirit")
def commonspirit():
    return render_template("commonspirit.html")


# ---- your existing routes ----
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/client")
def client():
    return redirect(url_for("collab"))

@app.route("/personal")
def personal():
    return render_template("personal.html")

@app.route("/collab")
def collab():
    return render_template("collab.html")

@app.route("/illustration")
def illustration():
    return render_template("personal websites/illustration.html")

@app.route("/portal")
def portal():
    return render_template("personal websites/portal.html")

@app.route("/street")
def street():
    return render_template("personal websites/street.html")

@app.route("/superface")
def superface():
    return render_template("personal websites/superface.html")

@app.route("/afvs")
def afvs():
    return render_template("personal websites/afvs.html")

@app.route("/gifafvs")
def gifafvs():
    return render_template("personal websites/gifafvs.html")

@app.route("/fysemr")
def fysemr():
    return render_template("personal websites/fysemr.html")

@app.route("/essays")
def essays():
    return render_template("personal websites/essays.html")

@app.route("/highlander")
def highlander():
    return render_template("collab websites/highlander.html")

@app.route("/recit")
def recit():
    return render_template("collab websites/recit.html")

@app.route("/olympics")
def olympics():
    return render_template("collab websites/olympics.html")

@app.route("/cs1710")
def cs171():
    return render_template("cs171.html")

if __name__ == "__main__":
    app.run(debug=True)
