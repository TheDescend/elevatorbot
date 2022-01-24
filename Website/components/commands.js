

export default function Command({command, gridStyle, gridItemStyle, gridBackground1, gridBackground2}) {
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
                                                <span className={`${option.required ? '' : 'italic'} self-center text-xs text-descend pl-2`}>
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
                                                                        <li className="ml-4">
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
