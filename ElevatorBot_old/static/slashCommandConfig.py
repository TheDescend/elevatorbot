from discord_slash.utils.manage_commands import generate_permissions


"""
This defines the permissions.
They are in this file, because otherwise Kigstn's dev version could not run, this it is on different servers
Anyways, these permissions disallow everyone to run the commands and only allow those specified
"""

# this allows people with the role admin or mod or dev to run this command
permissions_admin = {
    280456587464933376: generate_permissions(
        allowed_roles=[280459773428891648]
    ),  # @Admin id
}

# this allows socialists to run the command
permissions_socialist = {
    280456587464933376: generate_permissions(
        allowed_users=[238388130581839872]
    ),  # @Kigstn id
}

# this allows kigstn to run the command. Currently used for the /day1race command
permissions_kigstn = {
    280456587464933376: generate_permissions(
        allowed_users=[238388130581839872]
    ),  # @Kigstn id
}

permissions_kigstn_hali = {
    280456587464933376: generate_permissions(
        allowed_users=[238388130581839872, 219517105249189888]
    ),  # @Kigstn id, @hali id
}
