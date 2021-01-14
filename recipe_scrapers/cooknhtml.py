from bs4 import BeautifulSoup

from ._abstract import AbstractFileScraper
from ._schemaorg import SchemaOrg
from ._utils import get_minutes, normalize_string

import re


class CooknHtml(AbstractFileScraper):
    def __init__(
        self,
        path,
        exception_handling=True,
        encoding="utf-8",
        instruction_separator="  ",
    ):
        super().__init__(path, exception_handling=exception_handling, encoding=encoding)

        self.soup = BeautifulSoup(self.file_data, "html.parser")
        self.schema = SchemaOrg(self.file_data)
        self.instruction_separator = instruction_separator

    def title(self):
        return self.soup.find("h1", {"itemprop": "name"}).get_text().strip()

    def prep_time(self):
        return get_minutes(self.soup.find("time", {"itemprop": "prepTime"}))

    def cook_time(self):
        return get_minutes(self.soup.find("time", {"itemprop": "cookTime"}))

    def total_time(self):
        return self.prep_time() + self.cook_time()

    def yields(self):
        return self.soup.find("span", {"itemprop": "yield"}).get_text().strip()

    def ingredients(self):
        ingredients = self.soup.findAll("span", {"itemprop": "ingredient"})

        return [
            normalize_string(ingredient.get_text()).strip()
            for ingredient in ingredients
        ]

    def instructions(self):
        instruction_groups = list()
        instructions = self.soup.findAll("div", {"itemprop": "instructions"})
        for instruction in instructions:
            s = instruction.get_text().strip()
            removed_watermark = re.sub(
                "Recipe formatted with the Cook'n .* from DVO Enterprises.", "", s
            ).strip()
            instruction_groups.extend(
                removed_watermark.split(self.instruction_separator)
            )
        return "".join(instruction_groups)

    def image(self):
        return self.soup.find("img", {"itemprop": "photo"}).attrs["src"]

    def summary(self):
        summary_text = (
            self.soup.find("span", {"itemprop": "summary"}).get_text().strip()
        )
        return (
            ""
            if summary_text.startswith("from ") and len(summary_text) < 100
            else summary_text
        )

    def source(self):
        summary_text = (
            self.soup.find("span", {"itemprop": "summary"}).get_text().strip()
        )
        if summary_text.lower().startswith("from ") and len(summary_text) < 100:
            return summary_text[5:]
        instructions = self.soup.find("div", {"itemprop": "instructions"})
        if "source:" in [
            (s.strip().lower() if isinstance(s, str) else "")
            for s in instructions.contents
        ]:
            link = instructions.find(
                "a", href=re.compile(r"^(?!http://www\.dvo\.com).*$")
            )
            return link.attrs["href"]
        return ""

    def ratings(self):
        return None
