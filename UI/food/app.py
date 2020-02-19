from flask import Flask, render_template, request
from input_processing import handle
from search import search

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        recipe_name, dislike_list, processed_list = handle(request)
        context = search(recipe_name, dislike_list, processed_list)
        return render_template("results.html", context=context)


@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == "GET":
        recipe_name = ""
        dislike_list = []
        recipe_list = []
        context = {
            "recipe_name": recipe_name,
            "dislike_list": dislike_list,
            "recipe_list": recipe_list
        }
        return render_template("results.html", context=context)
    if request.method == "POST":
        recipe_name, dislike_list, processed_list = handle(request)
        context = search(recipe_name, dislike_list, processed_list)
        return render_template("results.html", context=context)


@app.route('/detail', methods=['GET'])
def detail():
    detail_id = request.args.get("id")

    recipe_name, dislike_list, processed_list = handle(request)
    context = search(recipe_name, dislike_list, processed_list)
    recipe = context["recipe_list"][int(detail_id)]

    return render_template('detail.html',recipe=recipe)


if __name__ == '__main__':
    app.run()
