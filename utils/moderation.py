import re
import discord


def check_bad_words(message):
    """ 
    Checks the message for bad words

    ## Returns
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

    ## Returns
        channel_message {discord.Embed} : Embed message to be sent in the current channel
        mod_log_message {discord.Embed} : Embed message to be sent in the mod-logs channel
    """

    bot_luminary = bot.get_user(808068717585891329)

    channel_message = discord.Embed(
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

    return channel_message, mod_log_message
