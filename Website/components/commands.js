function Command({command, gridStyle, gridItemStyle, gridBackground1, gridBackground2}) {
    return (
        <details className={`${gridItemStyle} ${gridBackground1}`}>
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
                    <details className={`${gridItemStyle} ${gridBackground2}`}>
                        <summary>
                            Options
                        </summary>
                        <div className={`${gridStyle}`}>
                            {
                                command["options"].map((option) => {
                                    return (
                                        <details className={`${gridItemStyle} ${gridBackground1}`}>
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
                                                    <details className={`${gridItemStyle} ${gridBackground2}`}>
                                                        <summary>
                                                            Choices
                                                        </summary>
                                                        <ul className={`${gridStyle} list-disc`}>
                                                            {
                                                                option["choices"].map((choices) => {
                                                                    return (
                                                                        <li className="ml-4" key={choices}>
                                                                            {choices}
                                                                        </li>
                                                                    )
                                                                })
                                                            }
                                                        </ul>
                                                    </details>
                                                }
                                            </div>
                                        </details>
                                    )
                                })
                            }
                        </div>
                    </details>
                }
            </div>
        </details>
    )
}


export default function ParseCommand({command, gridStyle, gridItemStyle, gridBackground1, gridBackground2}) {
    if ("name" in command) {
        return (
            <Command
                command={command}
                gridStyle={gridStyle}
                gridItemStyle={gridItemStyle}
                gridBackground1={gridBackground1}
                gridBackground2={gridBackground2}
            />
        )
    } else {
        return (
            <details className={`${gridItemStyle} ${gridBackground1}`}>
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
                                    gridItemStyle={gridItemStyle}
                                    gridBackground1={gridBackground2}
                                    gridBackground2={gridBackground1}
                                />
                            )
                        })
                    }
                </div>
            </details>
        )
    }

}
