import json
from copy import copy
from typing import Optional

from dis_snek.models import CommandTypes, ContextMenu, SlashCommand, SlashCommandOption

from ElevatorBot.elevator import ElevatorSnake


class NoValidatorOption:
    def __init__(self, obj: SlashCommandOption):
        self.name = obj.name
        self.description = obj.description
        self.required = obj.required
        self.autocomplete = obj.autocomplete
        self.choices = obj.choices


def create_command_docs(client: ElevatorSnake):
    """Create user documentation for commands and context menus in ./ElevatorBot/docs"""

    commands = {}
    sub_commands = {}
    context_menus_user = {}
    context_menus_message = {}

    # loop through all commands to get global and guild commands
    for scope, command in client.interactions.items():
        for resolved_name, data in command.items():
            # get the docstring
            docstring = data.scale.__doc__
            options = copy(data.options) if hasattr(data, "options") and data.options else []
            # todo
            permissions = copy(data.permissions)

            docstring, options = overwrite_options_text(options=options, docstring=docstring)

            # check what type of interaction this is
            match data:
                case ContextMenu():
                    doc = {
                        "name": resolved_name,
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

                case SlashCommand():
                    name = " ".join(resolved_name.split()[1:]) if data.is_subcommand else resolved_name

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
                            "autocomplete": option.autocomplete,
                        }

                        if option.choices:
                            option_dict.update({"choices": []})
                            for choice in option.choices:
                                option_dict["choices"].append(choice.name)

                        doc["options"].append(option_dict)

                    if data.is_subcommand:
                        # this ignores groups and only splits them into base / sub
                        base_name = resolved_name.split(" ")[0]

                        if scope not in sub_commands:
                            sub_commands.update({scope: []})

                        found = False
                        for entry in sub_commands[scope]:
                            if entry["base_name"] == base_name:
                                entry["sub_commands"].append(doc)
                                found = True
                        if not found:
                            sub_commands[scope].append(
                                {"base_name": base_name, "base_description": data.description, "sub_commands": [doc]}
                            )

                    else:
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


def overwrite_options_text(
    options: list[SlashCommandOption], docstring: Optional[str] = None
) -> tuple[Optional[str], list[SlashCommandOption] | list[SlashCommandOption | NoValidatorOption]]:
    """Overwrite the options if there is extra info in the docstring"""

    # loop through the options and see if we have an override
    if isinstance(docstring, str):
        new_options = []
        if ":option:" in docstring:
            docstring_lines = docstring.split("\n")

            for line in docstring_lines:
                if ":option:" in line:
                    docstring = docstring.replace(line, "")

                    option_data = line.split(":")

                    # loop through the options to edit the wanted one
                    for option in options:
                        if option.name == option_data[2].strip():
                            new_option = NoValidatorOption(obj=option)
                            new_option.description = option_data[3].strip()
                            new_options.append(new_option)
                        else:
                            new_options.append(option)

        return docstring.replace("\n", "").strip(), new_options or options
    return None, options
