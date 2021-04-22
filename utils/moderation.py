import re
import os
import discord
from utils.database import manage_infractions, check_infractions, \
    check_muted_users
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
BOT_LUMINARY = int(os.getenv("BOT_LUMINARY"))


def check_banned_words(message):
    """
    Checks the message for bad words

    # Returns

    bad_word_found {list} : A list of bad words used by the user
    """

    banned_words_list = [
        'retard', 'retarded', 'faggot', 'dyke', 'tranny', 'cunt',
        'nigger', 'nigga', 'whore', 'pussy'
    ]

    banned_word_found = []
    for word in banned_words_list:
        if re.search(word, message.content) is not None:
            banned_word_found.append(word)

    return banned_word_found


def get_banned_wrd_message(bot, message, banned_word_found):
    """
    Creates discord.Embed message for current & mod-logs channels

    # Returns

    channel_message {discord.Embed} : Embed message to be sent in the
                                      current channel

    mod_log_warn_message {discord.Embed} : Embed message to be sent in the
                                           mod-logs channel
    """

    bot_luminary = bot.get_user(BOT_LUMINARY)  # bot's user id

    curr_channel_message = discord.Embed(
        title=str(message.author) + " has been warned",
        description="**Reason**: Bad word usage"
    )

    user_avatar = message.author.avatar_url

    mod_log_warn_message = discord.Embed()
    mod_log_warn_message.set_author(
        name="[Warned] " + str(message.author),
        icon_url=user_avatar
    )

    mod_log_warn_message.add_field(
        name='User',
        value=f'{message.author.mention}', inline=True)

    mod_log_warn_message.add_field(
        name='Moderator',
        value=f'{bot_luminary.mention}', inline=True)

    mod_log_warn_message.add_field(
        name='Reason',
        value='Bad word usage', inline=True)

    mod_log_warn_message.add_field(
        name='Channel',
        value=f'{message.channel.mention}', inline=True)

    mod_log_warn_message.add_field(
        name='Bad words used',
        value=', '.join(banned_word_found), inline=True)

    mod_log_warn_message.add_field(
        name='Message',
        value=f'{message.content}', inline=False)

    return curr_channel_message, mod_log_warn_message


def get_modlog_mute_msg(bot, member, moderator, timeout_mute, reason):
    """
    Creates discord.Embed message for mod-logs channels for muted events

    # Returns

    mod_log_mute_message {discord.Embed} : Embed message to be sent in the
                                           mod-logs channel
    """

    user_avatar = member.avatar_url

    mod_log_mute_message = discord.Embed()
    mod_log_mute_message.set_author(
        name="[Muted] " + str(member),
        icon_url=user_avatar
    )

    mod_log_mute_message.add_field(
        name='User',
        value=f'{member.mention}', inline=True)

    mod_log_mute_message.add_field(
        name='Moderator',
        value=f'{moderator.mention}', inline=True)

    mod_log_mute_message.add_field(
        name='Reason',
        value=reason, inline=True)

    mod_log_mute_message.add_field(
        name='Muted for',
        value=f'{timeout_mute} mins', inline=False)

    return mod_log_mute_message


def get_infractions(msg):
    """
    Gets the user infractions table from database

    # Returns

    user_id {int} : Contains user id

    user_infractions {int} : Contains the number of infractions for the user
    """

    if isinstance(msg, str):
        msg = msg.strip()

    show_infractions = manage_infractions(msg, 3)
    try:
        user_id = show_infractions[0][0]
        user_infractions = show_infractions[0][1]

    except IndexError:
        """
        If the show_infractions list is empty,
        it means no infractions found
        """
        user_id = None
        user_infractions = 0

    return user_id, user_infractions


def get_infraction_msg(user_name, user_infractions):
    """
    Creates discord.Embed message for show all infraction for the user command

    # Returns

    infraction_msg {discord.Embed} : Embed message to be sent for the 
                                     infraction command
    """

    infraction_msg = discord.Embed()

    infraction_msg.set_author(
        name="All infractions for the User: " + str(user_name),
    )

    infraction_msg.add_field(
        name='User',
        value=f'{user_name}', inline=True)

    infraction_msg.add_field(
        name='Total infractions',
        value=f'{user_infractions}', inline=True)

    return infraction_msg


def get_inf_muted_diff():
    """
    Gets all infractions & muted_users data and creates two lists which
    contains the user_id and the the time difference between current time and
    last triggerd infraction and mute for the users

    # Returns

    infraction_diff_min {list} : List containing the user_id and the
                                 difference between current time & last
                                 triggered user infraction

    muted_diff_min {list} : List containing the user_id and the difference
                                 between current time & last triggered mute
                                 user event

    """

    curr_time = datetime.utcnow()
    infractions = check_infractions()
    muted_users = check_muted_users()

    infraction_diff_min = []
    muted_diff_min = []

    for user in infractions:
        time = user[2]  # last_triggered column

        # to convert each list element into int, remove non-numeric characters
        replace_sym = ['-', ' ', ':']
        for i in replace_sym:
            time = time.replace(i, ',')

        time = time.split(",")

        time = list(map(int, time))
        last_infraction = datetime(*time)

        infraction_diff_min.append(
            tuple((
                user[0], user[1], ((curr_time - last_infraction).total_seconds() / 60.0))
            )
        )

    for user in muted_users:
        time = user[2]  # last_triggered column

        # to convert each list element into int, remove non-numeric characters
        replace_sym = ['-', ' ', ':']
        for i in replace_sym:
            time = time.replace(i, ',')

        time = time.split(",")

        time = list(map(int, time))
        last_muted = datetime(*time)

        muted_diff_min.append(
            tuple((
                user[0], user[1], ((curr_time - last_muted).total_seconds() / 60.0))
            )
        )

    return infraction_diff_min, muted_diff_min


def get_user_inf_muted_timeout():
    """
    Compares the user's difference in last infraction and mute with the
    timeout and creates two lists containg the users whose infractions
    or mute role should be cleared/removed

    # Returns

        users_inf_timeout {list} : List containing the user_id and the
                                   difference between current time & last
                                   triggered user infraction

        users_muted_timeout {list} : List containing the user_id and the
                                     difference between current time & last
                                     triggered mute user event

    """

    infraction_diff_min, muted_diff_min = get_inf_muted_diff()

    timeout_inf = 30
    users_inf_timeout = []
    users_muted_timeout = []

    for user in infraction_diff_min:

        if user[2] > timeout_inf:
            users_inf_timeout.append(user[0])

    for user in muted_diff_min:

        if user[2] > user[1]:  # user[1] is the time_out in the db

            users_muted_timeout.append(user[0])

    return users_inf_timeout, users_muted_timeout


def get_modlog_kick_ban_msg(bot, user, moderator, reason, msg_type):
    """
    Creates discord.Embed message for mod-logs channels for ban events

    # Returns

    mod_log_ban_message {discord.Embed} : Embed message to be sent in the
                                           mod-logs channel
    """

    user_avatar = user.avatar_url

    mod_log_ban_message = discord.Embed()

    if msg_type == 1:
        mod_log_ban_message.set_author(
            name="[Banned] " + str(user),
            icon_url=user_avatar
        )
    elif msg_type == 2:
        mod_log_ban_message.set_author(
            name="[Unbanned] " + str(user),
            icon_url=user_avatar
        )
    elif msg_type == 3:
        mod_log_ban_message.set_author(
            name="[Kicked] " + str(user),
            icon_url=user_avatar
        )

    mod_log_ban_message.add_field(
        name='User',
        value=f'{user.mention}', inline=True)

    mod_log_ban_message.add_field(
        name='Moderator',
        value=f'{moderator.mention}', inline=True)

    mod_log_ban_message.add_field(
        name='Reason',
        value=reason, inline=True)

    return mod_log_ban_message


def get_mod_log_warn_message(moderator, member, reason):

    mod_log_warn_message = discord.Embed()

    mod_log_warn_message.set_author(
        name="[Warned] " + str(member),
        icon_url=member.avatar_url
    )

    mod_log_warn_message.add_field(
        name='User',
        value=f'{member.mention}', inline=True)

    mod_log_warn_message.add_field(
        name='Moderator',
        value=f'{moderator.mention}', inline=True)

    mod_log_warn_message.add_field(
        name='Reason',
        value=reason, inline=True)

    return mod_log_warn_message
