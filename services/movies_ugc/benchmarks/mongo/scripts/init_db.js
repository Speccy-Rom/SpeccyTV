const dbName = "ugc_db";
const conn = new Mongo();
const db = conn.getDB(dbName);

const collectionSettings = [
    {name: "movies"},
    {name: "users", shardKey: "_id"},
    {
        name: "movie_ratings",
        shardKey: "user_id",
        indexFields: ["movie_id", "score"]
    },
    {
        name: "reviews",
        shardKey: "author_id",
        indexFields: [
            "movie_id",
            "pub_date",
            "movie_rating_score",
        ]
    },
];

sh.enableSharding(dbName);

collectionSettings.forEach((collection) => {
    const collectionName = collection.name;
    const shardKey = collection.shardKey;
    const indexFields = collection.indexFields;

    db.createCollection(collectionName);
    if (shardKey !== undefined) {
        sh.shardCollection(`${dbName}.${collectionName}`, {[shardKey]: "hashed"});
    }
    if (indexFields !== undefined) {
        indexFields.forEach((field) => {
            db[collectionName].createIndex({[field]: -1});
        })
    }
});
