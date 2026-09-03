const express = require('express');
const session = require('express-session');
const path = require('path');
const fs = require('fs');

const dbPath = path.join(__dirname, 'classroom.db');
if (!fs.existsSync(dbPath)) {
  console.log('First startup detected. Running database seed...');
  require('./database/seed');
}

const db = require('./database/db');

const authRoutes = require('./routes/auth');
const notesRoutes = require('./routes/notes');
const coursesRoutes = require('./routes/courses');
const adminRoutes = require('./routes/admin');
const announcementsRoutes = require('./routes/announcements');
const assignmentsRoutes = require('./routes/assignments');
const classroomRoutes = require('./routes/classroom');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(session({
  secret: 'c7f4a8e2b1d6k9m3p5r0t4w8y2x6z1n5',
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    sameSite: 'lax',
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
  },
}));

app.use(express.static(path.join(__dirname, 'public')));

app.set('view engine', 'ejs');
app.set('views', [path.join(__dirname, 'views')]);

app.use((req, res, next) => {
  res.locals.user = req.session.user || null;
  next();
});

app.use((req, res, next) => {
  const setting = db.prepare("SELECT value FROM system_settings WHERE key = 'maintenance_mode'").get();
  const isOn = setting && setting.value === '1';
  const isAdmin = req.session.user && req.session.user.role === 'admin';
  const isAllowed = req.path.startsWith('/auth') || req.path.startsWith('/admin') || req.path.startsWith('/assets');

  if (isOn && !isAdmin && !isAllowed) {
    return res.status(503).render('error', {
      message: 'System is under maintenance. Please try again later.',
      user: req.session.user,
    });
  }
  next();
});

app.use('/auth', authRoutes);

app.use('/notes', notesRoutes);

app.use('/courses', coursesRoutes);

app.use('/admin', adminRoutes);

app.use('/announcements', announcementsRoutes);

app.use('/assignments', assignmentsRoutes);

app.use('/classroom', classroomRoutes);

app.get('/', (req, res) => {
  if (!req.session.user) return res.redirect('/auth/login');
  res.redirect('/dashboard');
});

app.get('/dashboard', (req, res) => {
  if (!req.session.user) return res.redirect('/auth/login');
  res.render('dashboard', { user: req.session.user });
});

app.use((req, res) => {
  res.status(404).render('error', {
    message: 'Page not found.',
    user: req.session.user,
  });
});

app.use((err, req, res, _next) => {
  console.error('[ERROR]', err.stack || err.message);
  res.status(500).render('error', {
    message: 'Internal server error.',
    user: req.session.user,
  });
});


app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

module.exports = app;
