import re, json, time
import requests
from discord.ext import commands
from fuzzywuzzy import fuzz
from discord.commands import slash_command, Option

class HabilitatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utilities = bot.get_cog("UtilitiesCog")
    
    @slash_command(name='actualitza', description='Actualitza el bot amb la versió actual de les habilitats de Llum Negra.')
    async def actualitza(self, ctx):
        await ctx.defer()

        with open("data/ability_pages.json", "r") as f:
            ability_pages = json.load(f)
        with open("user-token.cfg", "r") as f:
            token = f.read()
        with open("application-key.cfg", "r") as f:
            key = f.read()

        for role, id in ability_pages.items():
            url = f"https://www.worldanvil.com/api/external/boromir/article?id={id}&granularity=2"
            print(url)
            headers = {
                "accept": "application/json",
                "x-auth-token": token,
                "x-application-key": key
                }

            response = requests.get(url, headers=headers)
            data = response.json()['content']
            habilitat_regex = r"/\* BOT-HABILITAT-INICI \*/([\s\S]*?)/\* BOT-HABILITAT-FINAL \*/"
            cami_regex = r"/\* BOT-CAMI-INICI \*/([\s\S]*?)/\* BOT-CAMI-FINAL \*/"
            habilitats = re.findall(habilitat_regex, data)
            for hab in habilitats:
                self.utilities.save_abilities(hab, role)
            time.sleep(3)

        await ctx.respond('Fet!')
        return

    @slash_command(name="info", description="Mostra informació sobre l'habilitat especificada de Llum Negra.")
    async def info(self, ctx, habilitat: Option(str, "Nom de l'habilitat", required=True)):
        await ctx.defer()
        with open("data/abilities.json", "r") as f:
            abilities = json.load(f)
        
        fuzzies = {}
        fuzzy = False

        for role, abilities_dict in abilities.items():
            for name, ability in abilities_dict.items():
                fuzz_ratio = fuzz.ratio(name.lower(), habilitat.lower())
                print(f"{name}: {fuzz_ratio}")

                if fuzz_ratio >= 80:
                    fuzzies[name] = {}
                    fuzzies[name]['fuzziness'] = fuzz_ratio
                    fuzzies[name]['role'] = role

        if fuzzies == {}:
            await ctx.respond(f"No trobo l'habilitat `{habilitat}`! Comprova l'ortografia :)")
            return
        else:
            top_fuzz = max(fuzzies, key=lambda k: fuzzies[k]['fuzziness'])

        ability = self.utilities.get_ability(top_fuzz, fuzzies[top_fuzz]['role'])
        msg = f"""
## {top_fuzz.capitalize()}
_Habilitat de {role.capitalize()} de nivell {ability['level']}_
{ability['description']}
                    """
        if len(msg) >= 2000:
            truncated_msg = msg[:1900]
            new_msg =f"""
{truncated_msg} ...
_Pots veure la resta d'aquesta habilitat a la pàgina d'habilitats_
"""
            await ctx.respond(new_msg)
            return
        else:
            await ctx.respond(msg)
        return

def setup(bot):
    bot.add_cog(HabilitatsCog(bot))