import markovify
from random import randint, sample, choice

MEATS = ['Beef', 'Pork', 'Bacon', 'Venison', 'Chicken', 'Turkey', 'Vegetarian', 'Bean','White', 'Green']

class RecipeGenerator:
    def __init__(self):

        with open("adjectives.txt") as f:
            self.adjs = f.read().strip().split("\n")
        with open("adverbs.txt") as f:
            self.advs = f.read().strip().split("\n")

        # make ingredient model
        ingr = self.load_ingredient_corpus()
        self.ingr_model = markovify.NewlineText(ingr, state_size=1)

        # load poetry

        with open("poetry_corpus.txt") as f:
            poetry = f.read()
        self.poem_model = markovify.Text(poetry, state_size=2)

        # make the instructions

        with open("instr_corpus.txt") as f:
            text = f.read()
        self.raw_text_model = markovify.Text(text)

        # combined recipe/poetry model
        self.text_model = markovify.combine([self.poem_model, self.raw_text_model], (1, 1.5))

    def recipe_name(self):
        return "%s %s %s Chili" % (choice(self.advs),
                                    choice(self.adjs),
                                    choice(MEATS))

    def ingredients(self):
        # build a set to avoid duplicates
        s = set()
        for i in range(20):
            s.add(self.ingr_model.make_sentence(test_output=False))
        return sample(s, randint(5,14))

    def instructions(self):
        s = set()

        # make 10 long and short randomly-generated sentences
        for i in range(20):
            s.add(self.text_model.make_sentence(test_output=False))
            s.add(self.text_model.make_short_sentence(140, test_output=False))


        # remove serving instructions for later
        servings = {x for x in s if x.startswith("Serve")}
        s = s - servings

        l = []

        for i in range(randint(3,6)):
            # between 3 and 6 steps with 1-3 instructions per
            sam = sample(s, randint(1,3))
            l.append(" ".join(sam))
            # don't repeat instructions
            s = s - set(sam)

        if servings:
            l.append(choice(list(servings)))
        return l

    def markdown_recipe(self):
        print("# " + self.recipe_name().upper() + "\n\n")

        for ingredient in self.ingredients():
            print("* " + ingredient)

        print("\n\n")

        for i, instruction in enumerate(self.instructions()):
            print("%i. %s" % (i+1, instruction))

    def load_ingredient_corpus(self):
        # make ingredient list
        with open("ingr_corpus.txt") as f:
            ingr = f.read().strip()
        #ingr = ingr.replace(","," ,")
        s = set(ingr.split("\n"))

        # add some jumbled up ingredients, for fun
        REPLACES = (("1 cup","%i cups"),
                    ("1 can", "%i cans"),
                    ("1 tablespoon","%i tablespoons"),
                    ("1 teaspoon","%i teaspoons"),
                    ("2 pounds","%i pounds"),
                    ("1 can","%i pounds"),
                    ("1 cup","%i cans"),
                    ("1 teaspooon","%i cans"),
                    ("1/2 teaspoon", "%i cups"))

        v = s.copy()
        for elt in s:
            for R,V in REPLACES:
                if elt.startswith(R):
                    for i in range(2,randint(2,6)):
                        n = elt.replace(R, V % i)
                        v.add(n)

        # find the end phrases, set off with commas, and repeat them a bit.
        end_phrases = set()
        for elt in s:
            if "," in elt and not "and" in elt:
                end_phrases.add(elt[elt.index(","):])
        q = [x for x in v if "," not in x]
        for phrase in end_phrases:
            for i in range(2):
                n = choice(q)+phrase
                v.add(n)
        return v

def main():
    M = RecipeGenerator()
    print("\pagenumbering{gobble}\n\n")
    M.markdown_recipe()

if __name__ == '__main__':
    main()
