from recipe_scrapers import scrape_file

import requests
import pprint
import os
import sys
import json
import math
import getopt

from getpass import getpass

# Everything else will default to Entrée
COURSE_SIMPLIFICATION = {
    "entree": "Entrée",
    "entrees": "Entrée",
    "entrée": "Entrée",
    "entrées": "Entrée",
    "appetizer": "Appetizer",
    "appetizers": "Appetizer",
    "dessert": "Dessert",
    "desserts": "Dessert",
    "bar": "Dessert",
    "bars": "Dessert",
    "cookie": "Dessert",
    "cookies": "Dessert",
    "cake": "Dessert",
    "cakes": "Dessert",
    "pie": "Dessert",
    "pies": "Dessert",
    "side": "Side",
    "sides": "Side",
    "fruit": "Side",
    "fruits": "Side",
    "vegetables": "Side",
    "vegetable": "Side",
    "veggies": "Side",
    "salad": "Side",
    "salads": "Side",
    "drink": "Beverage",
    "drinks": "Beverage",
    "beverage": "Beverage",
    "beverages": "Beverage",
}

# Everything else defaults to Unknown
CUISINE_SIMPLIFICATION = {
    "beef": "Beef",
    "beefs": "Beef",
    "bread": "Bread",
    "breads": "Bread",
    "bar": "Bars",
    "bars": "Bars",
    "cookie": "Cookies",
    "cookies": "Cookies",
    "cake": "Cake",
    "cakes": "Cake",
    "fruit": "Fruit",
    "fruits": "Fruit",
    "pie": "Pie",
    "pies": "Pie",
    "pasta": "Pasta",
    "pastas": "Pasta",
    "pork": "Pork",
    "porks": "Pork",
    "poultry": "Poultry",
    "poultries": "Poultry",
    "chicken": "Poultry",
    "chickens": "Poultry",
    "turkey": "Poultry",
    "seafood": "Seafood",
    "seafoods": "Seafood",
    "fish": "Seafood",
    "soup": "Soup",
    "soups": "Soup",
    "vegetables": "Vegetables",
    "vegetable": "Vegetables",
    "veggie": "Vegetables",
    "veggies": "Vegetables",
    "salad": "Salad",
    "salads": "Salad",
}

GLUTEN_FREE_TAGS = ["gluten free", "gluten-free", "(gf)"]
CROCKPOT_TAGS = ["crock-pot", "crockpot", "crock pot", "slow cooker", "slow-cooker"]
AIR_FRYER_TAGS = ["air fry", "air-fry", "air fried", "air-fried"]
INSTANT_POT_TAGS = [
    "insta-pot",
    "insta pot",
    "instapot",
    "instant pot",
    "instant-pot",
    "instantpot",
]
SOUS_VIDE_TAGS = ["sous-vide", "sous vide", "sousvide"]

API_HOST = "http://192.168.0.199:8000/"
API_RECIPES = API_HOST + "api/v1/recipe/recipes/"
API_INGREDIENTS = API_HOST + "api/v1/ingredient/"
API_RECIPE_GROUPS = API_HOST + "api/v1/recipe_groups/"
API_CUISINE = API_RECIPE_GROUPS + "cuisine/"
API_COURSE = API_RECIPE_GROUPS + "course/"
TOKEN = getpass(prompt="JWT Token: ")

pp = pprint.PrettyPrinter(indent=2)


def get_recipe_group_dict(api):
    existing = dict()
    headers = {"Authorization": "JWT {}".format(TOKEN)}
    resp = requests.get(api, headers=headers)
    if resp.ok:
        for result in resp.json()["results"]:
            existing[result["title"]] = result["id"]
        return existing
    else:
        raise requests.ConnectionError(
            f"Getting {api} returned {resp.status_code}. {resp.text}"
        )


def get_recipe_group(name, type):
    if type == "course":
        api = API_COURSE
    elif type == "cuisine":
        api = API_CUISINE
    else:
        raise KeyError(f"No recipe group with name {type}")

    existing = get_recipe_group_dict(api)
    if name not in existing:
        data = {"title": name}
        resp = requests.post(
            api, data=data, headers={"Authorization": "JWT {}".format(TOKEN)}
        )
        if not resp.ok:
            raise requests.HTTPError(f"Server returned code {resp.status_code}")
        existing = get_recipe_group_dict(api)

    return {"id": existing[name], "title": name}


# From https://github.com/open-eats/openeats-web/blob/master/modules/recipe_form/utilts/parseIngredient.js
def build_fraction(text_array):
    if isinstance(text_array, str):
        text_array = [text_array]
    numerator = 0
    denominator = 0
    for text in text_array:
        split = text.split("/")
        n = int(float(split[0]))
        d = int(float(split[1])) if len(split) > 1 else 1

        if denominator == 0:
            numerator = n
            denominator = d
        elif len(split) == 1:
            n = n * numerator
            d = d * denominator
            gcd = math.gcd(n, d)
            numerator = n / gcd
            denominator = d / gcd
        else:
            n = numerator * d + denominator * n
            d = denominator * d
            gcd = math.gcd(n, d)
            numerator = n / gcd
            denominator = d / gcd

    return numerator, denominator


# From https://github.com/open-eats/openeats-web/blob/master/modules/recipe_form/utilts/parseIngredient.js
def number_split(number):
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    last = max([number.rfind(n) for n in numbers])
    if len(number) == last + 1:
        return number, ""
    else:
        return number[: last + 1], number[last + 1 :]


# From https://github.com/open-eats/openeats-web/blob/master/modules/recipe_form/utilts/parseIngredient.js
def parse_ingredient(line):
    tags = line.split(" ")

    try:
        if len(tags) == 1:
            return {"title": line}
        elif len(tags) == 2:
            if tags[0][0].isdigit():
                amount, measurement = number_split(tags[0])
                if len(measurement) > 0:
                    numerator, denominator = build_fraction(amount)
                    return {
                        "numerator": numerator,
                        "denominator": denominator,
                        "measurement": measurement,
                        "title": tags[1],
                    }
                else:
                    numerator, denominator = build_fraction(tags[0])
                    return {
                        "numerator": numerator,
                        "denominator": denominator,
                        "title": tags[1],
                    }
            else:
                return {"title": line}
        else:
            if not tags[0][0].isdigit():
                return {"title": line}
            elif not tags[1][0].isdigit():
                # pop(0) equivalent to splice(0,1)[0]
                amount, measurement = number_split(tags.pop(0))
                if len(measurement) == 0:
                    measurement = tags.pop(0)
                numerator, denominator = build_fraction(amount)
                return {
                    "numerator": numerator,
                    "denominator": denominator,
                    "measurement": measurement,
                    "title": " ".join(tags),
                }
            else:
                quantity = tags[0:2]
                tags = tags[2:]
                measurement = ""
                if len(tags) != 1:
                    measurement = tags.pop(0)
                numerator, denominator = build_fraction(quantity)
                return {
                    "numerator": numerator,
                    "denominator": denominator,
                    "measurement": measurement,
                    "title": " ".join(tags),
                }
    except Exception:
        # If it crashes, just submit the whole line as text and don't worry about quantities
        return {"title": line}


def get_ingredient_groups(ingredients):
    """Returns the ingredients group dictionary from the list of ingredients

    Ingredients that end with a colon are treated as a new ingredient group
    and all ingredients below it are placed into that group until another
    group is declared
    """
    if not isinstance(ingredients, list):
        ingredients = list(ingredients)
    groups = list()
    current_group = ""

    # Need to check if the "" group should be included.  If the first item is a group heading, we won't
    if not ingredients[0].endswith(":"):
        groups.append({"title": "", "ingredients": list()})

    for ingredient in ingredients:
        if ingredient.endswith(":"):
            current_group = ingredient[:-1]
            groups.append({"title": current_group, "ingredients": list()})
        elif len(ingredient.strip()) > 0:
            groups[-1]["ingredients"].append(parse_ingredient(ingredient))

    return groups


def upload_image(url, directory, img_filename):
    if len(img_filename) > 0:
        img_file = directory + "/" + img_filename
        headers = {"Authorization": "JWT {}".format(TOKEN)}
        with open(img_file, "rb") as img:
            files = {"photo": (os.path.basename(img_file), img, "image/jpeg")}
            resp = requests.patch(url, files=files, headers=headers)
            if not resp.ok:
                print(
                    f"Problem uploading image for {url}: Server returned status code {resp.status_code}",
                    file=sys.stderr,
                )


def get_tags(tags, filename_with_spaces):
    if any([substring in filename_with_spaces for substring in GLUTEN_FREE_TAGS]):
        tags.add("Gluten Free")
    if any([substring in filename_with_spaces for substring in CROCKPOT_TAGS]):
        tags.add("Crockpot")
    if any([substring in filename_with_spaces for substring in AIR_FRYER_TAGS]):
        tags.add("Air Fryer")
    if any([substring in filename_with_spaces for substring in INSTANT_POT_TAGS]):
        tags.add("Instant Pot")
    if any([substring in filename_with_spaces for substring in SOUS_VIDE_TAGS]):
        tags.add("Sous Vide")


def upload_file(
    path, cookbook_name=None, course=None, cuisine=None, tags=set(), source=None
):
    if not isinstance(tags, set):
        tags = set(tags)
    scraper = scrape_file(path, "cookn_html")
    data = dict()
    data["errors"] = dict()
    data["id"] = 0
    data["slug"] = ""

    filename = os.path.basename(path)
    filename_wo_cookbook = (
        filename.replace(cookbook_name.replace(" ", "_") + "_", "")
        if cookbook_name is not None
        else filename
    )

    category = filename_wo_cookbook.split("_")[0]

    # Make educated guesses at course, cuisine, and tags
    if course is None:
        course = COURSE_SIMPLIFICATION.get(category.lower(), "Entrée")

    if cuisine is None:
        cuisine = CUISINE_SIMPLIFICATION.get(category.lower(), "Unknown")

    filename_with_spaces = filename.lower().replace("_", " ")
    get_tags(tags, filename_with_spaces)

    data["course"] = get_recipe_group(course, "course")
    data["cuisine"] = get_recipe_group(cuisine, "cuisine")

    data["errors"]["course"] = ""
    data["errors"]["cuisine"] = ""
    if len(tags) > 0:
        data["tags"] = list([{"title": tag} for tag in tags])
        data["errors"]["tags"] = ""

    try:
        prep_time = int(scraper.prep_time())
    except Exception:
        prep_time = 0
    data["prep_time"] = str(prep_time)
    data["errors"]["prep_time"] = ""

    try:
        cook_time = int(scraper.cook_time())
    except Exception:
        cook_time = 0
    data["cook_time"] = str(cook_time)
    data["errors"]["cook_time"] = ""

    try:
        servings = int(scraper.yields_num())
    except Exception:
        servings = 4
    data["servings"] = str(servings)
    data["errors"]["servings"] = ""

    source = scraper.source()
    if isinstance(source, str) and len(source) > 0:
        data["source"] = source
        data["errors"]["source"] = ""

    data["title"] = scraper.title()
    data["errors"]["title"] = ""

    info = scraper.summary()
    if isinstance(info, str) and len(info) > 0:
        data["info"] = info
        data["errors"]["info"] = ""

    data["ingredient_groups"] = get_ingredient_groups(scraper.ingredients())
    data["errors"]["ingredient_groups"] = ""
    instructions = scraper.instructions()
    data["directions"] = (
        instructions if isinstance(instructions, str) else "\n".join(instructions)
    )
    data["errors"]["directions"] = ""
    data["public"] = True

    headers = {
        "Authorization": "JWT {}".format(TOKEN),
        "content-type": "application/json",
    }
    try:
        resp = requests.post(API_RECIPES, data=json.dumps(data), headers=headers)
        if resp.ok:
            url = API_RECIPES + resp.json()["slug"] + "/"
            directory = os.path.dirname(path)
            upload_image(url, directory, scraper.image())
        else:
            print(
                f"Problem uploading {path}: Server returned status code {resp.status_code}",
                file=sys.stderr,
            )

    except Exception as e:
        print(f"Problem uploading {path}: {e}", file=sys.stderr)


def upload_cookbook(path, course=None, cuisine=None, tags=set(), source=None):
    cookbook_name = os.path.basename(path)
    print(f"Importing all recipes form {cookbook_name} at path: {path}")
    _, _, filenames = next(os.walk(path))
    for filename in filenames:
        _, file_extension = os.path.splitext(filename)
        if file_extension == ".html":
            try:
                upload_file(
                    os.path.join(path, filename),
                    cookbook_name=cookbook_name,
                    course=course,
                    cuisine=cuisine,
                    tags=set(tags),
                    source=source,
                )
            except Exception as e:
                print(f"Unable to upload {filename} due to {e}")


IMPORT_HELP = """Imports an entire cookbook from Cook'n to the OpenEats server

Provide a path to a folder containing all the html files in the cookbook.  The folder
should have the same name as the cookbook

Optional Args:
--course  The course to assign all the recipes to.  Will guess if not provided
--cuisine The cuisine to assign all the recipes to.  Will guess if not provided
--tags    Any tags to supply to every one of the recipes in the cookbook
--source  Override of the source for all the recipes in the cookbook
"""


def import_cookn(argv):
    course = None
    cuisine = None
    tags = set()
    source = None
    try:
        opts, args = getopt.getopt(
            argv[1:], "c:u:t:s:h", ["course=", "cuisine=", "tags=", "source=", "help"]
        )
        for opt, arg in opts:
            if opt == "-h":
                print(IMPORT_HELP)
                exit()
            elif opt in ("--course", "-c"):
                course = arg
            elif opt in ("--cuisine", "-u"):
                cuisine = arg
            elif opt in ("--tags", "-t"):
                tags = set(arg.split(","))
            elif opt in ("--source", "-s"):
                source = arg
        folder = argv[0]
        upload_cookbook(
            folder, course=course, cuisine=cuisine, tags=tags, source=source
        )
    except getopt.GetoptError:
        print(IMPORT_HELP)
        exit(2)


if __name__ == "__main__":
    import_cookn(sys.argv[1:])
