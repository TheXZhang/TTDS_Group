recipe_database = [
    {
        "name": "bagel",
        "ingredients": ["onion", 'bread'],
        "description": "this is a description of bagel",
        "url": "http://www.baidu.com"
    }
]


def handle(request):
    recipe_name = request.form.get("recipe")
    dislike_list = []
    if request.form.get("dislike_list"):
        dislike_list = request.form.get("dislike_list").split(",")
    return [recipe_name, dislike_list]
