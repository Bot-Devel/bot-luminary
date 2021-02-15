import re
import discord
from utils.database import manage_infractions


def check_bad_words(message):
    """
    Checks the message for bad words

    # Returns
        bad_word_found {list} : A list of bad words used by the user
    """

    bad_words_list = ['retard', 'retarded', 'faggot', 'dyke', 'tranny', 'cunt',
                      'nigger', 'nigga', 'whore', 'pussy'
                      ]

    bad_word_found = []
    for word in bad_words_list:
        if re.search(word, message.content) is not None:
            bad_word_found.append(word)

    return bad_word_found


def get_mod_message(bot, message, bad_words_found):
    """
    Creates discord.Embed message for current & mod-logs channels

    # Returns
        channel_message {discord.Embed} : Embed message to be sent in the current channel
        mod_log_message {discord.Embed} : Embed message to be sent in the mod-logs channel
    """

    bot_luminary = bot.get_user(808068717585891329)

    curr_channel_message = discord.Embed(
        title=str(message.author) + " has been warned",
        description="**Reason**: Bad word usage"
    )
    user_avatar = message.author.avatar_url
    mod_log_message = discord.Embed()

    mod_log_message.set_author(
        name="[Warned] " + str(message.author),
        icon_url=user_avatar
    )

    mod_log_message.add_field(
        name='User',
        value=f'{message.author.mention}', inline=True)

    mod_log_message.add_field(
        name='Moderator',
        value=f'{bot_luminary.mention}', inline=True)

    mod_log_message.add_field(
        name='Reason',
        value='Bad word usage', inline=True)

    mod_log_message.add_field(
        name='Channel',
        value=f'{message.channel.mention}', inline=True)

    mod_log_message.add_field(
        name='Bad words used',
        value=', '.join(bad_words_found), inline=True)

    mod_log_message.add_field(
        name='Message',
        value=f'{message.content}', inline=False)

    return curr_channel_message, mod_log_message


def get_show_infractions(msg):
    """
    Gets the moderation table from database

    # Returns
        user_id {int} : Contains user id
        user_infractions {int} : Contains the number of infractions for the user
    """
    # select from table, add infractions
    show_infractions = manage_infractions(msg.strip(), 3)

    try:
        user_id = show_infractions[0][0]
        user_infractions = show_infractions[0][1]

    except IndexError:
        """
        If the show_infractions list is empty, it means no infractions found
        """
        user_id = None
        user_infractions = None

    return user_id, user_infractions


def get_infraction_msg(user_name, user_infractions):
    """
    Creates discord.Embed message for show all infraction for the user command

    # Returns
        infraction_msg {discord.Embed} : Embed message to be sent for the ;infraction command
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
