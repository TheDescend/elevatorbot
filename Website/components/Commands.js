import utilStyles from "../styles/utils.module.css";

export default function Command({name, description}) {
    return (
        <li className={utilStyles.listItem} key={name}>
            <p>{name}</p>
            <p>{description}</p>
        </li>
    )
}
