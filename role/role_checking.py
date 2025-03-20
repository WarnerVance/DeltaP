import discord


async def check_vp_internal_role(interaction: discord.Interaction) -> bool:
    """
    Checks if the user who triggered the interaction has the "VP Internal" role

    :param interaction: The interaction object representing the command or event in
        Discord. This is used to access details about the user and their roles.
    :type interaction: discord.Interaction
    :return: Returns ``True`` if the user has the "VP Internal" role; otherwise, sends
        an ephemeral message to the user and returns ``False``.
    :rtype: bool
    """
    vp_role = discord.utils.get(interaction.guild.roles, name="VP Internal")
    if vp_role is None or vp_role not in interaction.user.roles:
        await interaction.response.send_message(
            "You must have the VP Internal role to use this command.",
            ephemeral=True
        )
        return False
    return True


async def check_brother_role(interaction: discord.Interaction) -> bool:
    """
    Checks if the user who triggered the interaction has the "Brother" role.

    :param interaction: The interaction object representing the command or event in
        Discord. This is used to access details about the user and their roles.
    :type interaction: discord.Interaction
    :return: Returns ``True`` if the user has the "Brother" role; otherwise, sends
        an ephemeral message to the user and returns ``False``.
    :rtype: bool
    """
    brother_role = discord.utils.get(interaction.guild.roles, name="Brother")
    if brother_role is None or brother_role not in interaction.user.roles:
        await interaction.response.send_message("You must have the Brother role to use this command.", ephemeral=True)
        return False
    return True
