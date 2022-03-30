import json
from copy import copy
from typing import Optional

from dis_snek import CommandTypes, ContextMenu, SlashCommand, SlashCommandOption

from ElevatorBot.misc.formatting import capitalize_string
from Shared.functions.readSettingsFile import get_setting


class NoValidatorOption:
    def __init__(self, obj: SlashCommandOption):
        self.name = obj.name
        self.description = obj.description
        self.required = obj.required
        self.autocomplete = obj.autocomplete
        self.choices = obj.choices


def create_command_docs(client):
    """Create user documentation for commands and context menus in ./ElevatorBot/docs"""

    commands = {}
    context_menus = {}

    # loop through all commands to get global and guild commands
    for scope, command in client.interactions.items():
        # only show descend and global scope
        match scope:
            case 0:
                scope = "Available Globally"
            case _ if scope == get_setting("COMMAND_GUILD_SCOPE")[0]:
                scope = "Only Available in the Descend Server"
            case _:
                continue

        for resolved_name, data in command.items():
            # ignore the reload command
            if resolved_name == "reload":
                continue

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
                        "description": convert_markdown(str(docstring)),
                    }

                    match data.type:
                        case CommandTypes.USER:
                            topic = "User Context Menus"
                        case _:
                            topic = "Message Context Menus"

                    if topic not in context_menus:
                        context_menus.update({topic: {}})
                    if scope not in context_menus[topic]:
                        context_menus[topic].update({scope: []})
                    context_menus[topic][scope].append(doc)

                case SlashCommand():
                    # get the topic. The folder names are starting with numbers to define the order for this
                    topic = f"""{capitalize_string(data.scale.extension_name.split(".")[2][2:])} Commands"""

                    # get the actual description
                    actual_description = data.sub_cmd_description if data.sub_cmd_name else data.description

                    doc = {
                        "name": resolved_name,
                        "description": convert_markdown(docstring or actual_description),
                    }
                    if options:
                        doc.update({"options": []})

                    for option in options:
                        option_dict = {
                            "name": option.name,
                            "description": convert_markdown(option.description),
                            "required": option.required,
                            "autocomplete": option.autocomplete,
                        }

                        if option.choices:
                            option_dict.update({"choices": []})
                            for choice in option.choices:
                                option_dict["choices"].append(choice.name)

                        doc["options"].append(option_dict)

                    if topic not in commands:
                        commands.update({topic: {}})
                    if scope not in commands[topic]:
                        commands[topic].update({scope: []})

                    if data.is_subcommand:
                        # this ignores groups and only splits them into base / sub
                        base_name = (
                            " ".join([part.capitalize() for part in resolved_name.split(" ")[0].split("_")])
                            + " Commands"
                        )

                        found = False
                        for entry in commands[topic][scope]:
                            if "base_name" in entry and entry["base_name"] == base_name:
                                entry["sub_commands"].append(doc)
                                found = True
                        if not found:
                            commands[topic][scope].append(
                                {
                                    "base_name": base_name,
                                    "base_description": convert_markdown(data.description),
                                    "sub_commands": [doc],
                                }
                            )

                    else:
                        commands[topic][scope].append(doc)

    # sort the commands
    # sub commands first, then normal commands
    # everything alphabetical
    for topic in commands:
        for scope, c in commands[topic].items():
            temp_s = []
            temp_c = []
            for command in c:
                if "name" in command:
                    temp_c.append(command)
                else:
                    temp_s.append(command)

            # first sort the subcommands internally
            for base_command in temp_s:
                base_command["sub_commands"] = sorted(
                    base_command["sub_commands"], key=lambda item: item["name"], reverse=False
                )

            # sort them
            temp_c = sorted(temp_c, key=lambda item: item["name"], reverse=False)
            temp_s = sorted(temp_s, key=lambda item: item["base_name"], reverse=False)

            # overwrite the old data
            commands[topic][scope] = temp_s + temp_c

    # write those to files
    with open("./ElevatorBot/docs/commands.json", "w+", encoding="utf-8") as file:
        json.dump(commands, file, indent=4)
    with open("./ElevatorBot/docs/contextMenus.json", "w+", encoding="utf-8") as file:
        json.dump(context_menus, file, indent=4)


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


def convert_markdown(text: str) -> str:
    """Removes the markdown tags"""

    return text.replace("`", "")
