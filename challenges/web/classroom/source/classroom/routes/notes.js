const express = require('express');
const db = require('../database/db');
const { isAuthenticated } = require('../middleware/auth');
const router = express.Router();

router.get('/', isAuthenticated, (req, res) => {
  const notes = db.prepare(
    'SELECT n.*, u.username as author FROM notes n JOIN users u ON n.user_id = u.id WHERE n.user_id = ? ORDER BY n.created_at DESC'
  ).all(req.session.user.id);

  res.render('notes/index', { notes, user: req.session.user });
});

router.get('/public', isAuthenticated, (req, res) => {
  const notes = db.prepare(
    'SELECT n.*, u.username as author FROM notes n JOIN users u ON n.user_id = u.id WHERE n.is_private = 0 ORDER BY n.created_at DESC'
  ).all();

  res.render('notes/public', { notes, user: req.session.user });
});

router.get('/:id', isAuthenticated, (req, res) => {
  const note = db.prepare(
    'SELECT n.*, u.username as author FROM notes n JOIN users u ON n.user_id = u.id WHERE n.id = ?'
  ).get(req.params.id);

  if (!note) {
    return res.status(404).render('error', {
      message: 'Note not found.',
      user: req.session.user,
    });
  }

  const isOwner = note.user_id === req.session.user.id;

  res.render('notes/detail', {
    note,
    user: req.session.user,
    isOwner,
  });
});

router.post('/', isAuthenticated, (req, res) => {
  const { title, content, is_private } = req.body;
  const userId = req.session.user.id;

  if (!title) {
    return res.render('notes/index', {
      notes: db.prepare('SELECT n.*, u.username as author FROM notes n JOIN users u ON n.user_id = u.id WHERE n.user_id = ? ORDER BY n.created_at DESC').all(userId),
      error: 'Title is required.',
      user: req.session.user,
    });
  }

  db.prepare('INSERT INTO notes (user_id, title, content, is_private) VALUES (?, ?, ?, ?)').run(
    userId,
    title,
    content || '',
    is_private ? 1 : 0
  );

  res.redirect('/notes');
});

module.exports = router;
