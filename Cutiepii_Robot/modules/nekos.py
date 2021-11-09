import nekos
from Cutiepii_Robot.events import register

arguments = [
    "feet",
    "yuri",
    "trap",
    "futanari",
    "hololewd",
    "lewdkemo",
    "solog",
    "feetg",
    "cum",
    "erokemo",
    "les",
    "wallpaper",
    "lewdk",
    "ngif",
    "tickle",
    "lewd",
    "feed",
    "gecg",
    "eroyuri",
    "eron",
    "cum_jpg",
    "bj",
    "nsfw_neko_gif",
    "solo",
    "nsfw_avatar",
    "gasm",
    "poke",
    "anal",
    "slap",
    "hentai",
    "avatar",
    "erofeet",
    "holo",
    "keta",
    "blowjob",
    "pussy",
    "tits",
    "holoero",
    "lizard",
    "pussy_jpg",
    "pwankg",
    "classic",
    "kuni",
    "waifu",
    "pat",
    "8ball",
    "kiss",
    "femdom",
    "neko",
    "spank",
    "cuddle",
    "erok",
    "fox_girl",
    "boobs",
    "random_hentai_gif",
    "smallboobs",
    "hug",
    "ero",
    "goose",
    "baka",
    "woof",
    "kemonomimi",
    "smug",
]

@register(pattern="^/nekos ?(.*)")
async def nekos_img(event):
    args = event.pattern_match.group(1)
    anos = await event.reply("Fetching from nekos...")
    pic = nekos.img(args)
    await event.client.send_file(event.chat_id,pic)
    await anos.delete()

__mod_name__ = "Nekos"

__help__ = """
*Nekos:*
/nekos <name> : To find nekos from nekos.life
*Available commands:*
-feet
- yuri
- rap
- futanari
- hololewd
- lewdkemo
- solog
- feetg
- cum
- erokemo
- les
- wallpaper
- lewdk
- ngif
- tickle
- lewd
- feed
- gecg
- eroyuri
- eron
- cum_/jpg
- bj
- nsfw_/neko_/gif
- solo
- nsfw_/avatar
- gasm
- poke
- anal
- slap
- hentai
- avatar
- erofeet
- holo
- keta
- blowjob
- pussy
- tits
- holoero
- lizard
- pussy_/jpg
- pwankg
- classic
- kuni
- waifu
- pat
- 8ball
- kiss
- femdom
- neko
- spank
- cuddle
- erok
- fox_/girl
- boobs
- random_/hentai_/gif
- smallboobs
- hug
- ero
- goose
- baka
- woof
- kemonomimi
- smug
"""
