import discord


def welcome_message(member, status):

    user_avatar = member.avatar_url

    if status == 1:
        date = str(member.created_at)

        mod_welcome_message = discord.Embed(
            title="Member joined", description=f"{member.mention}, member no. {member.guild.member_count}.\nAccount created on {date}.", colour=0x2ecc71)

    elif status == 0:
        date = str(member.joined_at)

        roles = ""
        for i in member.roles:
            roles += str(i)+"\n"

        mod_welcome_message = discord.Embed(
            title="Member left", description=f"{member.mention} joined on {date}.\n**Roles:** {roles}", colour=0xe74c3c)

    mod_welcome_message.set_author(
        name=str(member),
        icon_url=user_avatar
    )

    mod_welcome_message.set_footer(
        text="ID: "+str(member.id)
    )

    return mod_welcome_message
