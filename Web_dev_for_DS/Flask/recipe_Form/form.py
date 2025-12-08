
from flask import Flask, render_template, request

app = Flask(__name__)

# handle both "/" and "/recipe" so there's no mismatch
@app.route("/", methods=["GET", "POST"])
@app.route("/recipe", methods=["GET", "POST"])
def recipe():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        ingredient = request.form.get("ingredient", "").strip()
        time = request.form.get("time", "").strip()

        if not name or not ingredient or not time:
            return render_template("recipe.html", error="Please fill all fields.")

        return render_template("summary.html", name=name, ingredient=ingredient, time=time)

    return render_template("recipe.html")

if __name__ == "__main__":
    app.run(debug=True)
