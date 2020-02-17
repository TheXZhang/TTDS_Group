def search(recipe, dislike_list):
    recipe_list= [
    {
        "id":0,
        "name": "bagel111",
        "ingredients": ["onion", 'bread'],
        "description": "this is a description of bagel,this is a description of bagel，this is a description of bagel, bagel,this is a description of bagel，th, bagel,this is a description of bagel，th",
        "url": ""
    },
    {
        "id":1,
        "name": "bagel222",
        "ingredients": ["onion", 'bread'],
        "description": "this is a description of bagel,this is a description of bagel，this is a description of bagel, bagel,this is a description of bagel，th, bagel,this is a description of bagel，th",
        "url": ""
    }
]
    return {
        "recipe_name": recipe,
        "dislike_list": dislike_list,
        "recipe_list": recipe_list
    }
