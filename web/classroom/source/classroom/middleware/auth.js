function isAuthenticated(req, res, next) {
  if (req.session && req.session.user) {
    return next();
  }
  return res.redirect('/auth/login?error=Please login first');
}

function isStudent(req, res, next) {
  if (req.session && req.session.user && req.session.user.role === 'student') {
    return next();
  }
  if (!req.session || !req.session.user) {
    return res.redirect('/auth/login');
  }
  return res.status(403).render('error', {
    message: 'Access denied. Student role required.',
    user: req.session.user,
  });
}

function isLecturer(req, res, next) {
  if (req.session && req.session.user && req.session.user.role === 'lecturer') {
    return next();
  }
  if (!req.session || !req.session.user) {
    return res.redirect('/auth/login');
  }
  return res.status(403).render('error', {
    message: 'Access denied. Lecturer role required.',
    user: req.session.user,
  });
}

function isAdmin(req, res, next) {
  if (req.session && req.session.user && req.session.user.role === 'admin') {
    return next();
  }
  if (!req.session || !req.session.user) {
    return res.redirect('/auth/login');
  }
  return res.status(403).render('error', {
    message: 'Access denied. Administrator role required.',
    user: req.session.user,
  });
}

function isStaff(req, res, next) {
  if (req.session && req.session.user &&
      (req.session.user.role === 'lecturer' || req.session.user.role === 'admin')) {
    return next();
  }
  if (!req.session || !req.session.user) {
    return res.redirect('/auth/login');
  }
  return res.status(403).render('error', {
    message: 'Access denied. Lecturer or Administrator role required.',
    user: req.session.user,
  });
}

function requireOwnership(table, idParam, userIdCol) {
  return (req, res, next) => {
    const db = require('../database/db');
    const resourceId = req.params[idParam];
    const userId = req.session.user.id;

    const row = db.prepare(`SELECT ${userIdCol} FROM ${table} WHERE id = ?`).get(resourceId);

    if (!row) {
      return res.status(404).render('error', {
        message: 'Resource not found.',
        user: req.session.user,
      });
    }

    if (row[userIdCol] !== userId && req.session.user.role !== 'admin') {
      return res.status(403).render('error', {
        message: 'Access denied. You do not own this resource.',
        user: req.session.user,
      });
    }

    next();
  };
}

module.exports = {
  isAuthenticated,
  isStudent,
  isLecturer,
  isAdmin,
  isStaff,
  requireOwnership,
};
