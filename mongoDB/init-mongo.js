use admin
db.createUser(
    {
        user: "nodeClient",
        pwd: "mongo2pass",
        roles: [
            {
                role: "readWrite",
                db: "minGPT"
            }
            , { role: "readWrite", db: "chat_history" }
        ]
    }
);