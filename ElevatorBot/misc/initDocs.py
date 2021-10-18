import json
from copy import copy

from dis_snek.client import Snake


# todo
def create_command_docs(client: Snake):
    """Create user documentation for commands and context menus in ./ElevatorBot/docs"""

    commands = {}
    sub_commands = {}
    context_menus = {}

    # loop through all commands and save the docstrings
    for command in client.interactions.values():
        # ignore the empty dict that there for some reason
        if command:
            name = command.name

            if not name.islower():
                # handle context menus. A bit cheaty for now, since they always have a capitalised letter which normal commands don't have
                docstring = str(command.cog.__doc__)
                options = copy(command.options)

                docstring = overwrite_options_text(docstring, options)

                context_menus.update(
                    {
                        name: {
                            "docstring": docstring.replace("\n", "").strip(),
                            "options": options,
                            "permissions": command.permissions,
                            "enabled_in_dms": not bool(command.default_permission),
                        }
                    }
                )

            elif not command.has_subcommands:
                # handle commands
                docstring = str(command.cog.__doc__)
                options = copy(command.options)

                docstring = overwrite_options_text(docstring, options)

                commands.update(
                    {
                        name: {
                            "docstring": docstring.replace("\n", "").strip(),
                            "options": options,
                            "permissions": command.permissions,
                            "enabled_in_dms": not bool(command.default_permission),
                        }
                    }
                )

            else:
                # handle subcommands
                sub_commands.update(
                    {
                        name: {
                            "description": command.description,
                            "sub_commands": [],
                        }
                    }
                )

                # get sub commands data
                s_commands = slash_client.subcommands[name]
                for sub_command in s_commands.values():
                    sub_command_name = sub_command.name
                    sub_command_docstring = str(sub_command.cog.__doc__)
                    options = copy(sub_command.options)

                    sub_command_docstring = overwrite_options_text(sub_command_docstring, options)

                    sub_commands[name]["sub_commands"].append(
                        {
                            sub_command_name: {
                                "docstring": sub_command_docstring.replace("\n", "").strip(),
                                "options": options,
                                "permissions": command.permissions,
                                "enabled_in_dms": not bool(command.default_permission),
                            }
                        }
                    )

    # write those to files
    with open("./docs/commands.json", "w+", encoding="utf-8") as file:
        json.dump(commands, file, indent=4)
    with open("./docs/subCommands.json", "w+", encoding="utf-8") as file:
        json.dump(sub_commands, file, indent=4)
    with open("./docs/contextMenus.json", "w+", encoding="utf-8") as file:
        json.dump(context_menus, file, indent=4)


def overwrite_options_text(docstring: str, options: dict) -> str:
    """Overwrite the options if there is extra info in the docstring"""

    # loop through the options and see if we have an override
    if ":option:" in docstring:
        docstring_lines = docstring.split("\n")
        for line in docstring_lines:
            if ":option:" in line:
                docstring = docstring.replace(line, "")

                option_data = line.split(":")

                # loop through the options to edit the wanted one
                for option in options:
                    if option["name"] == option_data[2].strip():
                        option["description"] = option_data[3].strip()
                        break
                break

    return docstring
