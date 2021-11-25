from pyrogram import filters

from Natsunagi import app
from Natsunagi.utils.errors import capture_err
from Natsunagi.utils.http import get


@app.on_message(filters.command("repo") & ~filters.edited)
@capture_err
async def repo(_, message):
    users = await get(
        "https://api.github.com/repos/aryazakaria01/natsunagi-nagisa/contributors"
    )
    list_of_users = ""
    count = 1
    for user in users:
        list_of_users += (
            f"**{count}.** [{user['login']}]({user['html_url']})\n"
        )
        count += 1

    text = f"""[Github](https://github.com/aryazakaria01) | [Group](t.me/BlackKnightsUnion_DevChat)
```----------------
| Contributors |
----------------```
{list_of_users}"""
    await app.send_message(
        message.chat.id, text=text, disable_web_page_preview=True
    )
