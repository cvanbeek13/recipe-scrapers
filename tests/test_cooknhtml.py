from tests import FileScraperTest

from recipe_scrapers import CooknHtml


class TestCooknHtmlScraper(FileScraperTest):

    scraper_class = CooknHtml

    def test_title(self):
        self.assertEqual(
            self.harvester_class.title(), "Meril's Kicked Up Mac and Cheese"
        )

    def test_total_time(self):
        self.assertEqual(120, self.harvester_class.total_time())

    def test_prep_time(self):
        self.assertEqual(60, self.harvester_class.prep_time())

    def test_cook_time(self):
        self.assertEqual(60, self.harvester_class.cook_time())

    def test_yields(self):
        self.assertEqual("6 to 8 servings", self.harvester_class.yields())

    def test_yields_num(self):
        self.assertEqual(6, self.harvester_class.yields_num())

    def test_image(self):
        self.assertEqual("131.jpg", self.harvester_class.image())

    def test_ingredients(self):
        self.assertCountEqual(
            [
                "2 teaspoons salt",
                "1 teaspoon olive oil",
                "1/2 pound elbow macaroni",
                "9 tablespoons (1 stick plus 1 tablespoon) unsalted butter",
                "1/2 cup all-purpose flour",
                "1/4 cup finely chopped smoked ham",
                "3 cups whole milk",
                "1/4 teaspoon ground white or black pepper",
                "3 cups grated cheddar (about 8 ounces)",
                "1/2 cup frozen green peas",
                "1/2 cup fine bread crumbs",
                "1 teaspoon emeril's original essence, or to taste, recipe follows",
                "2 1/2 tablespoons paprika",
                "2 tablespoons salt",
                "2 tablespoons garlic powder",
                "1 tablespoon black pepper",
                "1 tablespoon onion powder",
                "1 tablespoon cayenne pepper",
                "1 tablespoon dried oregano",
                "1 tablespoon dried thyme",
            ],
            self.harvester_class.ingredients(),
        )

    def test_instructions(self):
        expected = (
            "Make sure the oven rack is in the center position and preheat the oven to 350 degrees F. Bring a large pot of water to a rolling boil over high heat. Add 1 teaspoon of the salt, the oil, and macaroni, and stir to combine. Reduce the heat to medium and cook 10 minutes, stirring occasionally with a long-handled fork or spoon to prevent the macaroni from sticking together. Using oven mitts or pot holders, remove the pot from the stove and drain the macaroni in a colander set in the sink, pouring away from you. Rinse under cold running water and set aside to drain well. Grease a 2-quart casserole dish with 1 tablespoon of the butter. Set aside. Melt the remaining stick of butter in a heavy saucepan over medium heat. Add the flour and cook over medium heat, stirring constantly with a wooden spoon, for 3 to 4 minutes. Do not allow the flour to brown. Add the ham and cook, stirring, for 2 minutes. Using the whisk, add the milk and cook, whisking constantly, until the mixture is thick and smooth, about 4 minutes. Remove from the heat. Add the remaining 1 teaspoon of salt, the pepper, 2 cups of the cheese, and the peas, and stir well. In a mixing bowl, combine the remaining 1 cup of cheese with the bread crumbs and Essence. Add the macaroni to the pot with the milk and cheese. Stir to combine well, then pour the mixture into the buttered casserole. Top with the seasoned cheese mixture. Bake until golden brown and bubbly, about 25 minutes. Using oven mitts or pot holders, remove the dish from the oven and let it rest for 5 minutes before serving.Combine all ingredients thoroughly. Yield: 2/3 cupSource: foodnetwork.com",
        )
        actual = (self.harvester_class.instructions(),)
        return self.assertEqual(expected, actual)

    def test_source(self):
        return self.assertEqual(
            "http://www.foodnetwork.com/recipes/merils-kicked-up-mac-and-cheese-recipe/index.html",
            self.harvester_class.source(),
        )
