export default function Command({name, description}) {
    return (
        <li key={name}>
            <p>{name}</p>
            <p>{description}</p>
        </li>
    )
}
