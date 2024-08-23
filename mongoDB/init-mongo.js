db.createUser(
    {
        user: "nodeClient",
        pwd: "mongo2pass",
        roles: [
            {
                role: "readWrite",
                db: "minGPT"
            }
        ]
    }
);