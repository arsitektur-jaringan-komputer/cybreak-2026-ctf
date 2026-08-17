const express = require('express');
const db = require('../database/db');
const { isAuthenticated, isLecturer, requireOwnership } = require('../middleware/auth');
const router = express.Router();

router.get('/', isAuthenticated, (req, res) => {
  const courses = db.prepare(
    'SELECT c.*, u.username as lecturer_name FROM courses c JOIN users u ON c.lecturer_id = u.id ORDER BY c.created_at DESC'
  ).all();

  res.render('courses/index', { courses, user: req.session.user });
});

router.get('/:id', isAuthenticated, (req, res) => {
  const course = db.prepare(
    'SELECT c.*, u.username as lecturer_name FROM courses c JOIN users u ON c.lecturer_id = u.id WHERE c.id = ?'
  ).get(req.params.id);

  if (!course) {
    return res.status(404).render('error', {
      message: 'Course not found.',
      user: req.session.user,
    });
  }

  res.render('courses/view', { course, user: req.session.user });
});

router.get('/create/form', isLecturer, (req, res) => {
  res.render('courses/create', { error: null, user: req.session.user });
});

router.post('/create', isLecturer, (req, res) => {
  const { name, description } = req.body;

  if (!name) {
    return res.render('courses/create', {
      error: 'Course name is required.',
      user: req.session.user,
    });
  }

  db.prepare('INSERT INTO courses (name, description, lecturer_id) VALUES (?, ?, ?)').run(
    name,
    description || '',
    req.session.user.id
  );

  res.redirect('/courses');
});

router.post('/:id/delete', isLecturer, requireOwnership('courses', 'id', 'lecturer_id'), (req, res) => {
  db.prepare('DELETE FROM courses WHERE id = ?').run(req.params.id);
  res.redirect('/courses');
});

router.get('/import/form', isLecturer, (req, res) => {
  res.render('courses/import', {
    result: null,
    error: null,
    user: req.session.user,
  });
});

router.post('/import', isLecturer, (req, res) => {
  const { xmlData } = req.body;

  if (!xmlData || !xmlData.trim()) {
    return res.render('courses/import', {
      result: null,
      error: 'Please provide XML data to import.',
      user: req.session.user,
    });
  }

  try {
    const libxmljs = require('libxmljs2');
    const xmlDoc = libxmljs.parseXml(xmlData, {
      noent: true,
      dtdload: true,
      dtdvalid: false,
    });

    const students = [];
    const root = xmlDoc.root();

    if (root) {
      const studentNodes = root.find('//student');

      if (studentNodes && studentNodes.length > 0) {
        studentNodes.forEach((node) => {
          const name = node.attr('name')?.value() || 'Unknown';
          const text = node.text() || '';

          students.push({
            name: name,
            detail: text.trim(),
          });
        });
      }

      const rootText = root.text() || '';
      if (rootText.trim() && students.length === 0) {
        students.push({
          name: '(root content)',
          detail: rootText.trim(),
        });
      }
    }

    const result = {
      totalImported: students.length,
      timestamp: new Date().toISOString(),
      importedBy: req.session.user.username,
      students: students,
    };

    res.render('courses/import', {
      result: result,
      error: null,
      user: req.session.user,
    });
  } catch (err) {
    res.render('courses/import', {
      result: null,
      error: 'XML Parse Error: ' + err.message.replace(/\/.*?\//g, '[path]/'),
      user: req.session.user,
    });
  }
});

module.exports = router;
