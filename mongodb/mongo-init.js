// Create admin user
db.createUser({
    user: "admin",
    pwd: "admin",
    roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
});

// Switch to "ocr" database
db = db.getSiblingDB('ocr');

// Create a user for "ocr" database
db.createUser({
    user: "ocruser",
    pwd: "ocr",
    roles: [{ role: "readWrite", db: "ocr" }]
});

// Create a collection called "files" in "ocr" database
db.createCollection("files");
