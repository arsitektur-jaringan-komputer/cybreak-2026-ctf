const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');

const DB_PATH = '/app/classroom.db';
const BACKUP_DIR = '/app/backup';
const BACKUP_FILE = path.join(BACKUP_DIR, 'admin_credentials.json');

const INTERVAL_MS = 5000;

function ensureBackupFile() {
  if (!fs.existsSync(DB_PATH)) return;

  let db;
  try {
    db = new Database(DB_PATH, { fileMustExist: true });
    const admin = db.prepare("SELECT username, password FROM users WHERE role = 'admin' LIMIT 1").get();
    if (!admin) return;

    let current = null;
    try {
      current = JSON.parse(fs.readFileSync(BACKUP_FILE, 'utf8'));
    } catch (err) {
      current = null;
    }

    if (!current || current.password_hash !== admin.password) {
      fs.mkdirSync(BACKUP_DIR, { recursive: true });
      const backup = {
        username: admin.username,
        password_hash: admin.password,
        role: 'administrator',
        note: 'Legacy configuration backup. Migrated to database. TODO: Delete this file after migration.',
        created: '2025-06-15',
        system: 'Classroom Management System v1.0',
      };
      fs.writeFileSync(BACKUP_FILE, JSON.stringify(backup, null, 2));
    }
  } catch (err) {
  } finally {
    if (db) db.close();
  }
}

function hardenPermissions() {
  if (!fs.existsSync(BACKUP_FILE)) return;

  try {
    fs.chownSync(BACKUP_DIR, 0, 0);
    fs.chmodSync(BACKUP_DIR, 0o555);
    for (const entry of fs.readdirSync(BACKUP_DIR)) {
      const p = path.join(BACKUP_DIR, entry);
      if (fs.statSync(p).isDirectory()) continue;
      fs.chownSync(p, 0, 0);
      fs.chmodSync(p, 0o444);
    }
  } catch (err) {
  }
}

function tick() {
  ensureBackupFile();
  hardenPermissions();
}

tick();
setInterval(tick, INTERVAL_MS);
