export default function handler(req, res) {
    // todo check that start time > end time

    console.log(req.body)

    res.status(200).json({user: 'Ada Lovelace'})
}
