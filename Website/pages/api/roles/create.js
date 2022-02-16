import request from "../../../lib/http";
import {checkOk} from "./update/[role_id]";

export default async function handler(req, res) {
    const guild_id = req.body.guild_id
    const checkFailure = await checkOk(req, res)

    if (checkFailure != null) {
        res.status(500).json({
            content: checkFailure
        })
        return
    }

    // post to backend
    const data = await request(
        "POST",
        `/destiny/roles/${guild_id}/create`,
        req.body,
    )

    if (data.status_code === 200) {
        res.status(200).json({
            content: "Role has been created!"
        })
    } else {
        res.status(500).json({
            content: data.content
        })
    }

}
