import request from "../../../../lib/http";
import {checkOk} from "../update/[role_id]";

export default async function handler(req, res) {
    const { role_id } = req.query
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
        "DELETE",
        `/destiny/roles/${guild_id}/delete/${role_id}`,
    )

    if (data.status_code === 200) {
        res.status(200).json({
            content: "Role has been deleted!"
        })
    } else {
        res.status(500).json({
            content: data.content
        })
    }
}
