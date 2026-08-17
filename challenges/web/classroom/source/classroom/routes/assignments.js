const express = require('express');
const db = require('../database/db');
const { isAuthenticated, isLecturer, isStaff } = require('../middleware/auth');
const { logActivity } = require('../lib/activity');
const router = express.Router();

router.get('/', isAuthenticated, (req, res) => {
  const assignments = db.prepare(
    'SELECT a.*, c.name as course_name, c.lecturer_id, u.username as lecturer_name ' +
    'FROM assignments a JOIN courses c ON a.course_id = c.id JOIN users u ON c.lecturer_id = u.id ' +
    'ORDER BY a.created_at DESC'
  ).all();

  res.render('assignments/index', { assignments, user: req.session.user });
});

router.get('/create/form', isLecturer, (req, res) => {
  const courses = db.prepare('SELECT * FROM courses WHERE lecturer_id = ?').all(req.session.user.id);
  res.render('assignments/create', { courses, error: null, user: req.session.user });
});

router.post('/create', isLecturer, (req, res) => {
  const { course_id, title, description, due_date } = req.body;

  const course = db.prepare('SELECT * FROM courses WHERE id = ?').get(course_id);
  if (!course || course.lecturer_id !== req.session.user.id) {
    return res.status(403).render('error', {
      message: 'You can only create assignments for your own courses.',
      user: req.session.user,
    });
  }

  if (!title) {
    const courses = db.prepare('SELECT * FROM courses WHERE lecturer_id = ?').all(req.session.user.id);
    return res.render('assignments/create', {
      courses, error: 'Title is required.', user: req.session.user,
    });
  }

  db.prepare('INSERT INTO assignments (course_id, title, description, due_date) VALUES (?, ?, ?, ?)').run(
    course_id, title, description || '', due_date || ''
  );

  logActivity(req, `Created assignment: ${title}`);
  res.redirect('/assignments');
});

router.get('/gradebook', isAuthenticated, (req, res) => {
  let entries = [];
  let title = '';

  if (req.session.user.role === 'student') {
    title = 'My Grades';
    entries = db.prepare(
      'SELECT s.*, a.title as assignment_title, a.due_date, c.name as course_name ' +
      'FROM submissions s JOIN assignments a ON s.assignment_id = a.id JOIN courses c ON a.course_id = c.id ' +
      'WHERE s.student_id = ? ORDER BY s.submitted_at DESC'
    ).all(req.session.user.id);
  } else if (req.session.user.role === 'lecturer') {
    title = 'My Course Submissions';
    entries = db.prepare(
      'SELECT s.*, a.title as assignment_title, c.name as course_name, u.username as student_name ' +
      'FROM submissions s JOIN assignments a ON s.assignment_id = a.id JOIN courses c ON a.course_id = c.id ' +
      'JOIN users u ON s.student_id = u.id WHERE c.lecturer_id = ? ORDER BY s.submitted_at DESC'
    ).all(req.session.user.id);
  } else {
    title = 'All Submissions';
    entries = db.prepare(
      'SELECT s.*, a.title as assignment_title, c.name as course_name, u.username as student_name ' +
      'FROM submissions s JOIN assignments a ON s.assignment_id = a.id JOIN courses c ON a.course_id = c.id ' +
      'JOIN users u ON s.student_id = u.id ORDER BY s.submitted_at DESC'
    ).all();
  }

  res.render('assignments/gradebook', { entries, title, user: req.session.user });
});

router.get('/:id', isAuthenticated, (req, res) => {
  const assignment = db.prepare(
    'SELECT a.*, c.name as course_name, c.lecturer_id, u.username as lecturer_name ' +
    'FROM assignments a JOIN courses c ON a.course_id = c.id JOIN users u ON c.lecturer_id = u.id ' +
    'WHERE a.id = ?'
  ).get(req.params.id);

  if (!assignment) {
    return res.status(404).render('error', { message: 'Assignment not found.', user: req.session.user });
  }

  const isOwner = assignment.lecturer_id === req.session.user.id;
  const mySubmission = db.prepare(
    'SELECT * FROM submissions WHERE assignment_id = ? AND student_id = ?'
  ).get(assignment.id, req.session.user.id);

  let allSubmissions = [];
  if (isOwner || req.session.user.role === 'admin') {
    allSubmissions = db.prepare(
      'SELECT s.*, u.username as student_name FROM submissions s JOIN users u ON s.student_id = u.id WHERE s.assignment_id = ? ORDER BY s.submitted_at DESC'
    ).all(assignment.id);
  }

  res.render('assignments/view', {
    assignment,
    mySubmission,
    allSubmissions,
    isOwner,
    user: req.session.user,
    error: null,
    success: null,
  });
});

router.post('/:id/submit', isAuthenticated, (req, res) => {
  const { content } = req.body;
  const assignment = db.prepare('SELECT * FROM assignments WHERE id = ?').get(req.params.id);

  if (!assignment) {
    return res.status(404).render('error', { message: 'Assignment not found.', user: req.session.user });
  }

  if (req.session.user.role !== 'student') {
    return res.status(403).render('error', { message: 'Only students can submit assignments.', user: req.session.user });
  }

  if (!content || !content.trim()) {
    return res.redirect(`/assignments/${assignment.id}?error=Submission content is required.`);
  }

  db.prepare('INSERT INTO submissions (assignment_id, student_id, content) VALUES (?, ?, ?)').run(
    assignment.id, req.session.user.id, content
  );

  logActivity(req, `Submitted assignment #${assignment.id}`);
  res.redirect(`/assignments/${assignment.id}?success=Submission received!`);
});

router.post('/submissions/:id/grade', isLecturer, (req, res) => {
  const { grade } = req.body;
  const submission = db.prepare(
    'SELECT s.*, a.course_id, c.lecturer_id FROM submissions s ' +
    'JOIN assignments a ON s.assignment_id = a.id JOIN courses c ON a.course_id = c.id WHERE s.id = ?'
  ).get(req.params.id);

  if (!submission) {
    return res.status(404).render('error', { message: 'Submission not found.', user: req.session.user });
  }

  if (submission.lecturer_id !== req.session.user.id && req.session.user.role !== 'admin') {
    return res.status(403).render('error', {
      message: 'You can only grade submissions for your own courses.',
      user: req.session.user,
    });
  }

  db.prepare('UPDATE submissions SET grade = ?, graded_by = ? WHERE id = ?').run(
    grade || '', req.session.user.id, submission.id
  );

  logActivity(req, `Graded submission #${submission.id}: ${grade || '(cleared)'}`);
  res.redirect(`/assignments/${submission.assignment_id}`);
});

module.exports = router;
