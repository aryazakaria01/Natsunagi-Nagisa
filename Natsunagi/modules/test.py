from html import escape
from pyrogram import Client, filters
from pyrogram.types import Message
from EmikoRobot import pbot


@pbot.on_message(filters.command("staff"))
def staff(client: Client, message: Message):
    creator = []
    co_founder = []
    admin = []
    admin_check = pbot.get_chat_members(message.chat.id, filter="administrators")
    for x in admin_check:
        # Ini buat nyari co-founder
        if x.status == "administrator" and x.can_promote_members and x.title:
            title = escape(x.title)
            co_founder.append(
                f" <b>├</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a> <i>- {title}</i>"
            )
        elif x.status == "administrator" and x.can_promote_members and not x.title:
            co_founder.append(
                f" <b>├</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a>"
            )
        # ini buat nyari admin
        elif x.status == "administrator" and not x.can_promote_members and x.title:
            title = escape(x.title)
            admin.append(
                f" <b>├</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a> <i>- {title}</i>"
            )
        elif x.status == "administrator" and not x.can_promote_members and not x.title:
            admin.append(
                f" <b>├</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a>"
            )
        # ini buat nyari creator
        elif x.status == "creator" and x.title:
            title = escape(x.title)
            creator.append(
                f" <b>└</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a> <i>- {title}</i>"
            )
        elif x.status == "creator" and not x.title:
            creator.append(
                f" <b>└</b> <a href='tg://user?id={x.user.id}'>{x.user.first_name}</a>"
            )

    if len(co_founder) == 0 and len(admin) == 0:
        result = "🤴 <b><i>Founder</i></b>\n" + "\n".join(creator)

    elif len(co_founder) == 0 and len(admin) > 0:
        res_admin = admin[-1].replace("├", "└")
        admin.pop(-1)
        admin.append(res_admin)
        result = "🤴 <b><i>Founder</i></b>\n" + "\n".join(
            creator
        ) + "\n\n" "👮‍♂ <b><i>Admin</i></b>\n" + "\n".join(admin)

    elif len(co_founder) > 0 and len(admin) == 0:
        resco_founder = co_founder[-1].replace("├", "└")
        co_founder.pop(-1)
        co_founder.append(resco_founder)
        result = "🤴 <b><i>Founder</i></b>\n" + "\n".join(
            creator
        ) + "\n\n" "👨‍✈️ <b><i>Co-Founder</i></b>\n" + "\n".join(co_founder)

    else:
        resco_founder = co_founder[-1].replace("├", "└")
        res_admin = admin[-1].replace("├", "└")
        co_founder.pop(-1)
        admin.pop(-1)
        co_founder.append(resco_founder)
        admin.append(res_admin)
        result = (
            "🤴 <b><i>Founder</i></b>\n" + "\n".join(creator) + "\n\n"
            "👨‍✈️ <b><i>Co-Founder</i></b>\n" + "\n".join(co_founder) + "\n\n"
            "👮‍♂ <b><i>Admin</i></b>\n" + "\n".join(admin)
        )
    message.reply(result)
