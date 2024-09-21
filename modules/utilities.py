import re, json
from discord.ext import commands

class UtilitiesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def save_abilities(self, ability, role):
        name_regex = r"\[h3.*?\]([\s\S]*?)\[\/h3\]"
        level_regex = r"\[var:nivell-(.)-ondo\]"
        description_regex = r"\[var:nivell-.-ondo\]([\s\S]*)"


        ability_name = re.findall(name_regex, ability)[0]
        ability_level = re.findall(level_regex, ability)[0]
        ability_description = re.findall(description_regex, ability)[0]

        if ability_level == "l":
            ability_level = "llegendari"
        if ability_level == "o":
            ability_level = "habilitat d'origen"

        ability_description = self.clean_up_ability(ability_description)
        self.ability_to_json(ability_name, ability_level, ability_description, role)

        msg = f"""
        \n
--------------------------------
HABILITAT: {ability_name}
NIVELL: {ability_level}
DESCRIPCIÓ: {ability_description}
--------------------------------
        """
        print(msg)

        return

    def clean_up_ability(self, description):
        cost_replacements = {
            "1": ":one:",
            "2": ":two:",
            "3": ":three:",
            "4": ":four:",
            "5": ":five:",
            "6": ":six:",
            "7": ":seven:",
            "8": ":eight:",
            "9": ":nice:",
            "10": ":one::two:",
            "x": ":regional_indicator_x:"
        }
        for cost, replacement in cost_replacements.items():
            description = description.replace(f"[section:cost]{cost}[/section]", replacement)

        format_replacements = {
            "[b]": "**",
            "[/b]": "**",
            "[i]": "*",
            "[/i]": "*",
            "[u]": "__",
            "[/u]": "__",
            "[ul]": "",
            "[/ul]": "",
            "[li]": "- ",
            "[/li]": "",
            "[ol]": "",
            "[/ol]": "",
            "[br]": "",
            "[row]": "",
            "[/row]": "",
            "[col]": "",
            "[/col]": ""
        }
        for bbcode, markdown in format_replacements.items():
            description = description.replace(bbcode, markdown)

        smallcaps_regex = r"\[section:smallcaps\]([\s\S]*?)\[\/section\]"
        smallcaps_replace = r"`\1`"
        description = re.sub(smallcaps_regex, smallcaps_replace, description)

        bloc_apart_regex = r"\[container:bloc-apart\]([\s\S]*?)\[/container\]"
        bloc_apart_replacement = lambda match: re.sub(r"^", r"> ", match.group(1).strip(), flags=re.MULTILINE)
        description = re.sub(bloc_apart_regex, bloc_apart_replacement, description, flags=re.DOTALL)

        return description

    def ability_to_json(self, name, level, description, role):
        ability_dict = {
            "level": level,
            "description": description
        }
        
        with open("data/abilities.json", "r") as f:
            abilities = json.load(f)
        
        abilities[role][name] = ability_dict
        with open("data/abilities.json", "w") as f:
            json.dump(abilities, f)

        return
    
    def get_ability(self, name, role):
        with open("data/abilities.json", "r") as f:
            abilities = json.load(f)
        
        print(abilities[role])
        return abilities[role][name]

def setup(bot):
    bot.add_cog(UtilitiesCog(bot))