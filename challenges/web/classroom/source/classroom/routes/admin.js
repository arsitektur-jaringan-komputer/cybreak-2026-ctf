const express = require('express');
const path = require('path');
const fs = require('fs');
const db = require('../database/db');
const { isAuthenticated, isAdmin } = require('../middleware/auth');
const multer = require('multer');
const router = express.Router();

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, '..', 'public', 'uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, uniqueSuffix + '-' + file.originalname);
  },
});

const fileFilter = (req, file, cb) => {
  const allowedExt = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'];
  const ext = path.extname(file.originalname).toLowerCase();

  if (allowedExt.includes(ext)) {
    cb(null, true);
  } else {
    cb(new Error('Only image files are allowed (jpg, png, gif, bmp, svg)'), false);
  }
};

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: 1 * 1024 * 1024, // 1MB max
  },
});

router.get('/dashboard', isAdmin, (req, res) => {
  const stats = {
    totalUsers: db.prepare('SELECT COUNT(*) as count FROM users').get().count,
    totalNotes: db.prepare('SELECT COUNT(*) as count FROM notes').get().count,
    totalCourses: db.prepare('SELECT COUNT(*) as count FROM courses').get().count,
  };

  const recentUsers = db.prepare('SELECT id, username, role, created_at FROM users ORDER BY created_at DESC LIMIT 10').all();

  res.render('admin/dashboard', {
    stats,
    recentUsers,
    user: req.session.user,
  });
});

router.get('/users', isAdmin, (req, res) => {
  const users = db.prepare('SELECT id, username, role, created_at FROM users ORDER BY created_at DESC').all();
  res.render('admin/users', { users, user: req.session.user });
});

router.post('/users/:id/delete', isAdmin, (req, res) => {
  const target = db.prepare('SELECT id, username, role FROM users WHERE id = ?').get(req.params.id);

  if (!target) {
    return res.status(404).render('error', {
      message: 'User not found.',
      user: req.session.user,
    });
  }

  if (target.role === 'admin' || target.role === 'lecturer') {
    return res.status(403).render('error', {
      message: 'Cannot delete administrator or lecturer accounts. Protected for CTF integrity.',
      user: req.session.user,
    });
  }

  db.prepare('DELETE FROM notes WHERE user_id = ?').run(req.params.id);
  db.prepare('DELETE FROM users WHERE id = ?').run(req.params.id);

  const { logActivity } = require('../lib/activity');
  logActivity(req, `Deleted user #${req.params.id} (${target.username})`);
  res.redirect('/admin/users');
});

router.get('/modules', isAdmin, (req, res) => {
  const moduleName = req.query.name || '';
  const debug = req.query.debug === 'true';

  const modulesDir = path.join(__dirname, '..', 'modules');

  if (!fs.existsSync(modulesDir)) {
    fs.mkdirSync(modulesDir, { recursive: true });
  }

  const defaultModules = {
    'system_info.js': `
module.exports = {
  name: 'System Information',
  description: 'Displays system information',
  run: function() {
    return {
      platform: process.platform,
      arch: process.arch,
      nodeVersion: process.version,
      uptime: process.uptime(),
      memory: process.memoryUsage(),
    };
  }
};`,
    'database_stats.js': `
module.exports = {
  name: 'Database Statistics',
  description: 'Shows database statistics',
  run: function() {
    const db = require('../database/db');
    return {
      users: db.prepare('SELECT COUNT(*) as c FROM users').get().c,
      notes: db.prepare('SELECT COUNT(*) as c FROM notes').get().c,
      courses: db.prepare('SELECT COUNT(*) as c FROM courses').get().c,
    };
  }
};`,
    'cleanup_temp.js': `
module.exports = {
  name: 'Temporary File Cleanup',
  description: 'Cleans up temporary files',
  run: function() {
    return { cleaned: 0, message: 'No temporary files to clean.' };
  }
};`,
  };

  Object.entries(defaultModules).forEach(([filename, content]) => {
    const filePath = path.join(modulesDir, filename);
    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, content);
    }
  });

  const availableModules = fs.readdirSync(modulesDir)
    .filter(f => f.endsWith('.js'))
    .map(f => ({ name: f, path: `/admin/modules?name=${encodeURIComponent(f)}` }));

  if (!moduleName) {
    return res.render('admin/modules', {
      modules: availableModules,
      result: null,
      error: null,
      debug: false,
      user: req.session.user,
    });
  }

  try {
    const fullPath = path.resolve(path.join(modulesDir, moduleName));

    if (!fs.existsSync(fullPath)) {
      return res.render('admin/modules', {
        modules: availableModules,
        result: null,
        error: `Module not found: ${moduleName}`,
        debug: debug,
        user: req.session.user,
      });
    }

    delete require.cache[require.resolve(fullPath)];

    const mod = require(fullPath);

    let result;
    if (mod && typeof mod.run === 'function') {
      result = mod.run();
    } else if (mod) {
      result = mod;
    } else {
      result = { message: 'Module loaded but exports nothing.' };
    }

    res.render('admin/modules', {
      modules: availableModules,
      result: result,
      error: null,
      debug: debug,
      loadedModule: moduleName,
      user: req.session.user,
    });
  } catch (err) {
    res.render('admin/modules', {
      modules: availableModules,
      result: null,
      error: `Module execution error: ${err.message}`,
      debug: debug,
      loadedModule: moduleName,
      user: req.session.user,
    });
  }
});

router.get('/upload', isAdmin, (req, res) => {
  const uploadDir = path.join(__dirname, '..', 'public', 'uploads');
  let uploadedFiles = [];

  if (fs.existsSync(uploadDir)) {
    uploadedFiles = fs.readdirSync(uploadDir)
      .map(f => ({
        name: f,
        path: `/uploads/${f}`,
        size: fs.statSync(path.join(uploadDir, f)).size,
      }))
      .sort((a, b) => b.name.localeCompare(a.name))
      .slice(0, 20);
  }

  res.render('admin/upload', {
    uploadedFiles,
    success: null,
    error: null,
    user: req.session.user,
  });
});

const handleUpload = (req, res, next) => {
  upload.single('image')(req, res, (err) => {
    if (!err) return next();

    const uploadDir = path.join(__dirname, '..', 'public', 'uploads');
    const uploadedFiles = fs.existsSync(uploadDir)
      ? fs.readdirSync(uploadDir).map(f => ({ name: f, path: `/uploads/${f}`, size: fs.statSync(path.join(uploadDir, f)).size }))
      : [];

    const message = err.code === 'LIMIT_FILE_SIZE'
      ? 'File is too large. Maximum allowed size is 1 MB.'
      : err.message;

    return res.render('admin/upload', {
      uploadedFiles,
      success: null,
      error: message,
      user: req.session.user,
    });
  });
};

router.post('/upload', isAdmin, handleUpload, (req, res) => {
  const uploadDir = path.join(__dirname, '..', 'public', 'uploads');

  if (!req.file) {
    const uploadedFiles = fs.existsSync(uploadDir)
      ? fs.readdirSync(uploadDir).map(f => ({ name: f, path: `/uploads/${f}`, size: fs.statSync(path.join(uploadDir, f)).size }))
      : [];

    return res.render('admin/upload', {
      uploadedFiles,
      success: null,
      error: 'Please select a file to upload.',
      user: req.session.user,
    });
  }

  const uploadedFiles = fs.readdirSync(uploadDir)
    .map(f => ({
      name: f,
      path: `/uploads/${f}`,
      size: fs.statSync(path.join(uploadDir, f)).size,
    }))
    .sort((a, b) => b.name.localeCompare(a.name))
    .slice(0, 20);

  res.render('admin/upload', {
    uploadedFiles,
    success: `File uploaded successfully: ${req.file.filename} (${(req.file.size / 1024).toFixed(1)} KB)`,
    error: null,
    uploadedFile: {
      name: req.file.filename,
      path: `/uploads/${req.file.filename}`,
      size: req.file.size,
    },
    user: req.session.user,
  });
});

router.get('/config', isAdmin, (req, res) => {
  const backupDir = path.join(__dirname, '..', 'backup');
  let configs = [];

  if (fs.existsSync(backupDir)) {
    configs = fs.readdirSync(backupDir)
      .filter(f => f.endsWith('.json'))
      .map(f => ({
        name: f,
        path: `/backup/${f}`,
      }));
  }

  res.render('admin/config', {
    configs,
    user: req.session.user,
  });
});

router.get('/logs', isAdmin, (req, res) => {
  const logs = db.prepare(
    'SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT 200'
  ).all();

  res.render('admin/logs', { logs, user: req.session.user });
});

router.get('/settings', isAdmin, (req, res) => {
  const maintenance = db.prepare("SELECT value FROM system_settings WHERE key = 'maintenance_mode'").get();
  res.render('admin/settings', {
    maintenanceMode: maintenance && maintenance.value === '1',
    user: req.session.user,
    error: null,
    success: null,
  });
});

router.post('/settings/maintenance', isAdmin, (req, res) => {
  const enabled = req.body.enabled === '1' ? '1' : '0';
  db.prepare("UPDATE system_settings SET value = ? WHERE key = 'maintenance_mode'").run(enabled);

  const { logActivity } = require('../lib/activity');
  logActivity(req, enabled === '1' ? 'Enabled maintenance mode' : 'Disabled maintenance mode');

  res.render('admin/settings', {
    maintenanceMode: enabled === '1',
    user: req.session.user,
    error: null,
    success: enabled === '1' ? 'Maintenance mode ENABLED.' : 'Maintenance mode DISABLED.',
  });
});

module.exports = router;
