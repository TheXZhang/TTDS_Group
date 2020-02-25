from flask import Flask, render_template, request
from input_processing import handle
import search
import json

app = Flask(__name__)




with open('index_index_data.json', 'r') as fp:
    inverted_index = json.load(fp)

all_doc_ID=open("all_document_ID.txt").read().split('\n')
del all_doc_ID[-1]


@app.route('/', methods=['GET', 'POST'])
def index():
    global inverted_index
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        recipe_name, processed_dislike_list,dislike_list, processed_list = handle(request)
        context = search.main(inverted_index,recipe_name, processed_dislike_list,dislike_list, processed_list)
        return render_template("results.html", context=context)


@app.route('/results', methods=['GET', 'POST'])
def results():
    global inverted_index
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
        recipe_name, processed_dislike_list,dislike_list, processed_list = handle(request)
        context = search.main(inverted_index,recipe_name, processed_dislike_list,dislike_list, processed_list)
        return render_template("results.html", context=context)


@app.route('/detail', methods=['GET'])
def detail():
    global inverted_index
    global all_doc_ID
    detail_id = request.args.get("id")
    recipe=search.display_info(detail_id,all_doc_ID)
    print("display ready")
    


    return render_template('detail.html',recipe=recipe)


if __name__ == '__main__':
    app.run()
