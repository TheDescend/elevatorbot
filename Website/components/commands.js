import ContentContainer from "./styling/container";

function Command({command, gridStyle, otherStyleFirst}) {
    return (
        <ContentContainer otherStyle={otherStyleFirst}>
            <details>
                <summary>
                    <code>
                        /{command.name}
                    </code>
                </summary>
                <div className={`${gridStyle}`}>
                    <p>
                        {command.description}
                    </p>
                    {"options" in command &&
                        <ContentContainer otherStyle={!otherStyleFirst}>
                            <details>
                                <summary>
                                    Options
                                </summary>
                                <div className={`${gridStyle}`}>
                                    {
                                        command["options"].map((option) => {
                                            return (
                                                <ContentContainer otherStyle={otherStyleFirst}>
                                                    <details>
                                                        <summary>
                                                            <code className="text-center">
                                                                {option.name}
                                                            </code>
                                                            <span
                                                                className={`${option.required ? '' : 'italic'} self-center text-xs text-descend pl-2`}>
                                                    {option.required ? '' : 'optional'}
                                                </span>
                                                        </summary>
                                                        <div className={`${gridStyle}`}>
                                                            <div>
                                                                <p>
                                                                    {option.description}
                                                                </p>
                                                            </div>
                                                            {"choices" in option &&
                                                                <ContentContainer otherStyle={!otherStyleFirst}>
                                                                    <details>
                                                                        <summary>
                                                                            Choices
                                                                        </summary>
                                                                        <ul className={`${gridStyle} list-disc`}>
                                                                            {
                                                                                option["choices"].map((choices) => {
                                                                                    return (
                                                                                        <li className="ml-4"
                                                                                            key={choices}>
                                                                                            {choices}
                                                                                        </li>
                                                                                    )
                                                                                })
                                                                            }
                                                                        </ul>
                                                                    </details>
                                                                </ContentContainer>
                                                            }
                                                        </div>
                                                    </details>
                                                </ContentContainer>
                                            )
                                        })
                                    }
                                </div>
                            </details>
                        </ContentContainer>
                    }
                </div>
            </details>
        </ContentContainer>
    )
}


export default function ParseCommand({command, gridStyle, otherStyleFirst}) {
    if ("name" in command) {
        return (
            <Command
                command={command}
                gridStyle={gridStyle}
                otherStyleFirst={otherStyleFirst}
            />
        )
    } else {
        return (
            <ContentContainer otherStyle={otherStyleFirst}>
                <details>
                    <summary>
                        {command["base_name"]}
                    </summary>

                    <div className={`${gridStyle}`}>
                        <p>
                            {command["base_description"]}
                        </p>
                        {
                            command["sub_commands"].map((subCommand) => {
                                return (
                                    <Command
                                        command={subCommand}
                                        gridStyle={gridStyle}
                                        otherStyleFirst={!otherStyleFirst}
                                    />
                                )
                            })
                        }
                    </div>
                </details>
            </ContentContainer>
        )
    }

}
