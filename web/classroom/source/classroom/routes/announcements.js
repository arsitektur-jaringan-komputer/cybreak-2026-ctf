const express = require('express');
const db = require('../database/db');
const { isAuthenticated, isStaff, isAdmin } = require('../middleware/auth');
const { logActivity } = require('../lib/activity');
const router = express.Router();

router.get('/', isAuthenticated, (req, res) => {
  const announcements = db.prepare(
    'SELECT a.*, u.username as author FROM announcements a JOIN users u ON a.author_id = u.id ORDER BY a.created_at DESC'
  ).all();

  res.render('announcements/index', {
    announcements,
    user: req.session.user,
    error: null,
    success: null,
  });
});

router.post('/', isStaff, (req, res) => {
  const { title, content } = req.body;

  if (!title || !content) {
    const announcements = db.prepare(
      'SELECT a.*, u.username as author FROM announcements a JOIN users u ON a.author_id = u.id ORDER BY a.created_at DESC'
    ).all();
    return res.render('announcements/index', {
      announcements,
      user: req.session.user,
      error: 'Title and content are required.',
      success: null,
    });
  }

  db.prepare('INSERT INTO announcements (author_id, title, content) VALUES (?, ?, ?)').run(
    req.session.user.id, title, content
  );

  logActivity(req, `Posted announcement: ${title}`);
  res.redirect('/announcements');
});

router.post('/:id/delete', isAdmin, (req, res) => {
  db.prepare('DELETE FROM announcements WHERE id = ?').run(req.params.id);
  logActivity(req, `Deleted announcement #${req.params.id}`);
  res.redirect('/announcements');
});

module.exports = router;
