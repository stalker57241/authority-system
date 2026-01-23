CREATE TABLE IF NOT EXISTS Users (
    id INTEGER NOT NULL PRIMARY KEY,
    email TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    isactive BOOLEAN NOT NULL DEFAULT (TRUE)
);

CREATE TABLE IF NOT EXISTS UserTokens (
    id INTEGER NOT NULL,
    token TEXT NOT NULL,
    expired TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Permissions (
    id INTEGER NOT NULL PRIMARY KEY,
    permname TEXT NOT NULL,
    parentpermid INTEGER DEFAULT NULL,
    FOREIGN KEY(parentpermid) REFERENCES Permissions(id),
    CHECK (parentpermid != id)
);

INSERT OR IGNORE INTO Permissions (
    id, permname, parentpermid
) VALUES
    (1, "OPERATOR", NULL),
        (2, "GUEST", 1),
            (3, "REGISTER", 2),
            (4, "LOGIN", 2),
    (5, "ACCOUNT", 1),
        (6, "DELETE", 5);
        (7, "EDIT", 6),
        (8, "VIEW", 7),

CREATE TABLE IF NOT EXISTS GrantedPermissions (
    userid INTEGER NOT NULL,
    permid INTEGER NOT NULL,
    PRIMARY KEY(userid ASC, permid),
    FOREIGN KEY(userid) REFERENCES Users(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    FOREIGN KEY(permid) REFERENCES Permissions(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);