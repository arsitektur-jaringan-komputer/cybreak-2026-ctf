const express = require('express');
const db = require('../database/db');
const { isAuthenticated, isStaff, requireOwnership } = require('../middleware/auth');
const { logActivity } = require('../lib/activity');
const router = express.Router();

router.get('/bookmarks', isAuthenticated, (req, res) => {
  const bookmarks = db.prepare(
    'SELECT b.id, b.course_id, c.name as course_name, c.description, u.username as lecturer_name ' +
    'FROM bookmarks b JOIN courses c ON b.course_id = c.id JOIN users u ON c.lecturer_id = u.id ' +
    'WHERE b.user_id = ? ORDER BY b.created_at DESC'
  ).all(req.session.user.id);

  res.render('bookmarks', { bookmarks, user: req.session.user });
});

router.post('/bookmarks/toggle/:courseId', isAuthenticated, (req, res) => {
  const course = db.prepare('SELECT id FROM courses WHERE id = ?').get(req.params.courseId);
  if (!course) {
    return res.status(404).render('error', { message: 'Course not found.', user: req.session.user });
  }

  const existing = db.prepare(
    'SELECT id FROM bookmarks WHERE user_id = ? AND course_id = ?'
  ).get(req.session.user.id, course.id);

  if (existing) {
    db.prepare('DELETE FROM bookmarks WHERE id = ?').run(existing.id);
  } else {
    db.prepare('INSERT INTO bookmarks (user_id, course_id) VALUES (?, ?)').run(
      req.session.user.id, course.id
    );
  }

  res.redirect(req.get('referer') || '/courses');
});

router.get('/forum/:courseId', isAuthenticated, (req, res) => {
  const course = db.prepare(
    'SELECT c.*, u.username as lecturer_name FROM courses c JOIN users u ON c.lecturer_id = u.id WHERE c.id = ?'
  ).get(req.params.courseId);

  if (!course) {
    return res.status(404).render('error', { message: 'Course not found.', user: req.session.user });
  }

  const posts = db.prepare(
    'SELECT p.*, u.username as author FROM forum_posts p JOIN users u ON p.author_id = u.id ' +
    'WHERE p.course_id = ? ORDER BY p.created_at ASC'
  ).all(course.id);

  res.render('forum', { course, posts, user: req.session.user });
});

router.post('/forum/:courseId', isAuthenticated, (req, res) => {
  const { content } = req.body;
  const course = db.prepare('SELECT id FROM courses WHERE id = ?').get(req.params.courseId);

  if (!course) {
    return res.status(404).render('error', { message: 'Course not found.', user: req.session.user });
  }

  if (!content || !content.trim()) {
    return res.redirect(`/classroom/forum/${course.id}`);
  }

  db.prepare('INSERT INTO forum_posts (course_id, author_id, content) VALUES (?, ?, ?)').run(
    course.id, req.session.user.id, content
  );

  logActivity(req, `Posted in forum of course #${course.id}`);
  res.redirect(`/classroom/forum/${course.id}`);
});

router.get('/schedule', isAuthenticated, (req, res) => {
  const entries = db.prepare(
    "SELECT s.*, u.username as lecturer_name FROM schedules s JOIN users u ON s.lecturer_id = u.id " +
    "ORDER BY CASE s.day_of_week WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 " +
    "WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 ELSE 7 END, s.start_time"
  ).all();

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const grouped = {};
  days.forEach((d) => { grouped[d] = entries.filter((e) => e.day_of_week === d); });

  res.render('schedule', {
    days, grouped, user: req.session.user, error: null, success: null,
  });
});

router.post('/schedule', isStaff, (req, res) => {
  const { day_of_week, start_time, end_time, subject } = req.body;

  if (!day_of_week || !start_time || !end_time || !subject) {
    return res.redirect('/classroom/schedule?error=All fields are required.');
  }

  db.prepare(
    'INSERT INTO schedules (lecturer_id, day_of_week, start_time, end_time, subject) VALUES (?, ?, ?, ?, ?)'
  ).run(req.session.user.id, day_of_week, start_time, end_time, subject);

  logActivity(req, `Added schedule entry: ${subject} (${day_of_week})`);
  res.redirect('/classroom/schedule?success=Schedule entry added.');
});

router.post('/schedule/:id/delete', isAuthenticated, requireOwnership('schedules', 'id', 'lecturer_id'), (req, res) => {
  db.prepare('DELETE FROM schedules WHERE id = ?').run(req.params.id);
  res.redirect('/classroom/schedule');
});

router.get('/stats', isAuthenticated, (req, res) => {
  const uid = req.session.user.id;
  const stats = {
    myNotes: db.prepare('SELECT COUNT(*) as c FROM notes WHERE user_id = ?').get(uid).c,
    mySubmissions: db.prepare('SELECT COUNT(*) as c FROM submissions WHERE student_id = ?').get(uid).c,
    myBookmarks: db.prepare('SELECT COUNT(*) as c FROM bookmarks WHERE user_id = ?').get(uid).c,
    myForumPosts: db.prepare('SELECT COUNT(*) as c FROM forum_posts WHERE author_id = ?').get(uid).c,
  };

  const recentActivity = db.prepare(
    'SELECT action, created_at FROM activity_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 10'
  ).all(uid);

  res.render('stats', { stats, recentActivity, user: req.session.user });
});

module.exports = router;
