import discord
import os
from dotenv import load_dotenv

load_dotenv()
RX_HOUSES = int(os.getenv("RXHOUSES"))
RX_ANNOUNCEMENTS = int(os.getenv("RXANNOUNCEMENTS"))


rx_dict_houses = {
    "gryffindor": "Gryffindor",
    "ravenclaw": "Ravenclaw",
    "slytherin": "Slytherin",
    "hufflepuff": "Hufflepuff"
}

rx_dict_announcements = {
    "🗒️": "Story News",
    "📣": "Announcements"
}

rx_dict_master = {
    "RX_HOUSES": [RX_HOUSES, rx_dict_houses],
    "RX_ANNOUNCEMENTS": [RX_ANNOUNCEMENTS, rx_dict_announcements]
}

#status: 1 (adding) or 2 (removing)


def role_update(member, role, status):

    user_avatar = member.avatar_url

    if status == 1:
        role_update_message = discord.Embed(
            title="Role added", description=role.mention)
    elif status == 0:
        role_update_message = discord.Embed(
            title="Role removed", description=role.mention)

    role_update_message.set_author(
        name=str(member),
        icon_url=user_avatar
    )

    role_update_message.set_footer(
        text="ID: "+str(member.id)
    )

    return role_update_message
