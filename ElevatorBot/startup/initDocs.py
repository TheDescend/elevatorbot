import json
from copy import copy
from typing import Optional

from dis_snek.client import Snake
from dis_snek.models import (
    CommandTypes,
    ContextMenu,
    OptionTypes,
    SlashCommand,
    SlashCommandOption,
)


def create_command_docs(client: Snake):
    """Create user documentation for commands and context menus in ./ElevatorBot/docs"""

    commands = {}
    sub_commands = {}
    context_menus_user = {}
    context_menus_message = {}

    # loop through all commands to get global and guild commands
    for scope, command in client.interactions.items():
        for name, data in command.items():
            # get the docstring
            docstring = data.__doc__
            options = copy(data.options) if hasattr(data, "options") and data.options else []
            # todo
            permissions = copy(data.permissions)

            docstring = overwrite_options_text(docstring, options)

            # check what type of interaction this is
            match data:
                case ContextMenu():
                    doc = {
                        "name": name,
                        "description": str(docstring),
                    }

                    match data.type:
                        case CommandTypes.USER:
                            if scope not in context_menus_user:
                                context_menus_user.update({scope: []})
                            context_menus_user[scope].append(doc)

                        case CommandTypes.MESSAGE:
                            if scope not in context_menus_message:
                                context_menus_message.update({scope: []})
                            context_menus_message[scope].append(doc)

                case SubCommand():
                    # todo docstrings are used where?
                    doc = {"name": name, "description": data.description, "groups": [], "sub_commands": []}

                    for group in data.options:
                        if group["type"] == OptionTypes.SUB_COMMAND_GROUP:
                            subcommand_group_dict = {
                                "name": group["name"],
                                "description": group["description"],
                                "sub_commands": [],
                            }

                            for sub_command in group["options"]:
                                subcommand_dict = {
                                    "name": sub_command["name"],
                                    "description": sub_command["description"],
                                    "options": [],
                                }

                                for option in sub_command["options"]:
                                    option_dict = {
                                        "name": option["name"],
                                        "description": option["description"],
                                        "required": option["required"],
                                    }

                                    if "choices" in option:
                                        option_dict.update({"choices": []})
                                        for choice in option["choices"]:
                                            option_dict["choices"].append(
                                                {
                                                    "name": choice.name,
                                                }
                                            )

                                    subcommand_dict["options"].append(option_dict)
                                subcommand_group_dict["sub_commands"].append(subcommand_dict)
                            doc["groups"].append(subcommand_group_dict)

                        else:
                            subcommand_dict = {
                                "name": group["name"],
                                "description": group["description"],
                                "options": [],
                            }

                            for option in group["options"]:
                                option_dict = {
                                    "name": option["name"],
                                    "description": option["description"],
                                    "required": option["required"],
                                }

                                if "choices" in option:
                                    option_dict.update({"choices": []})
                                    for choice in option["choices"]:
                                        option_dict["choices"].append(
                                            {
                                                "name": choice["name"],
                                            }
                                        )

                                subcommand_dict["options"].append(option_dict)
                            doc["sub_commands"].append(subcommand_dict)

                    if scope not in sub_commands:
                        sub_commands.update({scope: []})
                    sub_commands[scope].append(doc)

                case SlashCommand():
                    # todo docstrings are wierd
                    doc = {
                        "name": name,
                        "description": docstring or data.description,
                        "options": [],
                    }

                    for option in options:
                        option_dict = {
                            "name": option.name,
                            "description": option.description,
                            "required": option.required,
                        }

                        if option.choices:
                            option_dict.update({"choices": []})
                            for choice in option.choices:
                                option_dict["choices"].append(
                                    {
                                        "name": choice.name,
                                    }
                                )

                        doc["options"].append(option_dict)

                    if scope not in commands:
                        commands.update({scope: []})
                    commands[scope].append(doc)

    # write those to files
    with open("./docs/commands.json", "w+", encoding="utf-8") as file:
        json.dump(commands, file, indent=4)
    with open("./docs/subCommands.json", "w+", encoding="utf-8") as file:
        json.dump(sub_commands, file, indent=4)
    with open("./docs/contextMenusUser.json", "w+", encoding="utf-8") as file:
        json.dump(context_menus_user, file, indent=4)
    with open("./docs/contextMenusMessage.json", "w+", encoding="utf-8") as file:
        json.dump(context_menus_message, file, indent=4)


def overwrite_options_text(docstring: Optional[str], options: list[SlashCommandOption]) -> str:
    """Overwrite the options if there is extra info in the docstring"""

    # loop through the options and see if we have an override
    if isinstance(docstring, str) and ":option:" in docstring:
        docstring_lines = docstring.split("\n")
        for line in docstring_lines:
            if ":option:" in line:
                docstring = docstring.replace(line, "")

                option_data = line.split(":")

                # loop through the options to edit the wanted one
                for option in options:
                    if option.name == option_data[2].strip():
                        option.description = option_data[3].strip()
                        break
                break

    return docstring
