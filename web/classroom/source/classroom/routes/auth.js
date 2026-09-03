const express = require('express');
const bcrypt = require('bcryptjs');
const db = require('../database/db');
const { logActivity } = require('../lib/activity');
const router = express.Router();

router.get('/login', (req, res) => {
  if (req.session.user) return res.redirect('/dashboard');
  res.render('login', {
    error: req.query.error || null,
    success: req.query.success || null,
    user: null,
  });
});

router.post('/login', (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.render('login', { error: 'Username and password are required.', success: null, user: null });
  }

  const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);

  if (!user) {
    return res.render('login', { error: 'Invalid username or password.', success: null, user: null });
  }

  const valid = bcrypt.compareSync(password, user.password);
  if (!valid) {
    logActivity(req, `Failed login attempt for username: ${username}`);
    return res.render('login', { error: 'Invalid username or password.', success: null, user: null });
  }

  req.session.user = {
    id: user.id,
    username: user.username,
    role: user.role,
  };

  logActivity(req, `Logged in as ${user.role}`);

  switch (user.role) {
    case 'admin':
      return res.redirect('/dashboard');
    case 'lecturer':
      return res.redirect('/dashboard');
    default:
      return res.redirect('/dashboard');
  }
});

router.get('/register', (req, res) => {
  if (req.session.user) return res.redirect('/dashboard');
  res.render('register', { error: req.query.error || null, user: null });
});

router.post('/register', (req, res) => {
  const { username, password, confirmPassword } = req.body;

  if (!username || !password) {
    return res.render('register', { error: 'All fields are required.', user: null });
  }

  if (password !== confirmPassword) {
    return res.render('register', { error: 'Passwords do not match.', user: null });
  }

  if (password.length < 6) {
    return res.render('register', { error: 'Password must be at least 6 characters.', user: null });
  }

  const existing = db.prepare('SELECT id FROM users WHERE username = ?').get(username);
  if (existing) {
    return res.render('register', { error: 'Username already taken.', user: null });
  }

  const hash = bcrypt.hashSync(password, 10);
  db.prepare('INSERT INTO users (username, password, role) VALUES (?, ?, ?)').run(username, hash, 'student');

  logActivity(req, `Registered new account: ${username}`);
  res.redirect('/auth/login?success=Registration successful! Please login.');
});

router.get('/logout', (req, res) => {
  logActivity(req, 'Logged out');
  req.session.destroy();
  res.redirect('/auth/login');
});

router.get('/profile', require('../middleware/auth').isAuthenticated, (req, res) => {
  const user = db.prepare('SELECT id, username, role, created_at FROM users WHERE id = ?').get(req.session.user.id);
  res.render('profile', {
    profile: user,
    error: null,
    success: req.query.success || null,
    user: req.session.user,
  });
});

router.post('/change-password', require('../middleware/auth').isAuthenticated, (req, res) => {
  const { currentPassword, newPassword, confirmPassword } = req.body;
  const userId = req.session.user.id;
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);

  if (user.role === 'lecturer' || user.role === 'admin') {
    return res.render('profile', {
      profile: user,
      error: 'This account is protected. Password changes are disabled.',
      user: req.session.user,
    });
  }

  if (!currentPassword || !newPassword) {
    return res.render('profile', {
      profile: user,
      error: 'All fields are required.',
      user: req.session.user,
    });
  }

  if (newPassword !== confirmPassword) {
    return res.render('profile', {
      profile: user,
      error: 'New passwords do not match.',
      user: req.session.user,
    });
  }

  const valid = bcrypt.compareSync(currentPassword, user.password);
  if (!valid) {
    return res.render('profile', {
      profile: user,
      error: 'Current password is incorrect.',
      user: req.session.user,
    });
  }

  const newHash = bcrypt.hashSync(newPassword, 10);
  db.prepare('UPDATE users SET password = ? WHERE id = ?').run(newHash, userId);

  res.render('profile', {
    profile: user,
    error: 'Password changed successfully!',
    user: req.session.user,
  });
});

module.exports = router;
