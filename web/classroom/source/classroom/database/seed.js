const bcrypt = require('bcryptjs');
const path = require('path');
const fs = require('fs');
const db = require('./db');

const ADMIN_USERNAME = 'admin-' + Math.random().toString(36).substring(2, 10);
const LECTURER_USERNAME = 'lecturer-' + Math.random().toString(36).substring(2, 10);
const ADMIN_PASSWORD = 'gymclassheroes';
const LECTURER_PASSWORD = 'L3ctur3rS3cur3P@ss2026!';

function seed() {
  console.log('Seeding database...');

  const existingAdmin = db.prepare('SELECT id FROM users WHERE username = ?').get(ADMIN_USERNAME);
  if (existingAdmin) {
    console.log('Database already seeded.');
    return;
  }

  const adminHash = bcrypt.hashSync(ADMIN_PASSWORD, 10);
  const lecturerHash = bcrypt.hashSync(LECTURER_PASSWORD, 10);

  const insertUser = db.prepare('INSERT INTO users (username, password, role) VALUES (?, ?, ?)');

  const adminResult = insertUser.run(ADMIN_USERNAME, adminHash, 'admin');
  const lecturerResult = insertUser.run(LECTURER_USERNAME, lecturerHash, 'lecturer');

  const adminId = adminResult.lastInsertRowid;
  const lecturerId = lecturerResult.lastInsertRowid;

  const insertNote = db.prepare('INSERT INTO notes (user_id, title, content, is_private) VALUES (?, ?, ?, ?)');

  insertNote.run(
    lecturerId,
    'IMPORTANT: Backup Credentials',
    `Don't forget your login details!\n\nUsername: ${LECTURER_USERNAME}\nPassword: ${LECTURER_PASSWORD}\n`,
    1
  );

  insertNote.run(
    lecturerId,
    'Course Schedule Planning',
    'Monday: Advanced Web Security\nTuesday: Network Penetration Testing\nWednesday: Cryptography Workshop\nThursday: CTF Preparation\nFriday: Student Presentations',
    1
  );

  insertNote.run(
    lecturerId,
    'Welcome to Web Security Course',
    'This semester we will cover OWASP Top 10 vulnerabilities, with hands-on labs covering XSS, SQL Injection, CSRF, SSRF, XXE, and more. Please review the syllabus before the first class.',
    0
  );

  insertNote.run(
    adminId,
    'Server Maintenance Notes',
    'SSH port changed to 2222.\nBackup script runs daily at 2AM.\nLegacy credentials stored in /app/backup/admin_credentials.json (TODO: remove this file).',
    1
  );

  insertNote.run(
    adminId,
    'System Announcement',
    'Welcome to the Classroom Management System v2.1. All users must update their profiles. Report any issues via the announcements page.',
    0
  );

  const insertCourse = db.prepare('INSERT INTO courses (name, description, lecturer_id) VALUES (?, ?, ?)');

  const webCourse = insertCourse.run('Web Application Security', 'Comprehensive study of web vulnerabilities including XSS, CSRF, SQLi, and more.', lecturerId);
  const netCourse = insertCourse.run('Network Security Fundamentals', 'Introduction to network protocols, firewalls, IDS/IPS, and packet analysis.', lecturerId);
  const cryptoCourse = insertCourse.run('Cryptography in Practice', 'Applied cryptography covering symmetric/asymmetric encryption, hashing, and PKI.', lecturerId);

  const insertAnnouncement = db.prepare('INSERT INTO announcements (author_id, title, content) VALUES (?, ?, ?)');
  insertAnnouncement.run(lecturerId, 'Welcome to the New Semester!', 'Welcome back everyone! Classes begin next week. Please review the course syllabi and complete your profiles before the first session.');
  insertAnnouncement.run(adminId, 'System Maintenance Window', 'The classroom system will undergo maintenance on Saturday 02:00-04:00 AM. Please save your work in advance.');
  insertAnnouncement.run(lecturerId, 'CTF Competition Announcement', 'This semester we will host an internal CTF competition. Students who solve all challenges will receive extra credit. Stay tuned for details!');

  const insertAssignment = db.prepare('INSERT INTO assignments (course_id, title, description, due_date) VALUES (?, ?, ?, ?)');
  insertAssignment.run(webCourse.lastInsertRowid, 'OWASP Top 10 Report', 'Write a report analyzing the OWASP Top 10 vulnerabilities, including real-world examples and mitigation strategies for each.', '2026-09-15');
  insertAssignment.run(webCourse.lastInsertRowid, 'XXE Vulnerability Lab', 'Complete the XXE lab exercise. Document how external entities can be exploited for file disclosure, and describe prevention techniques.', '2026-09-30');
  insertAssignment.run(netCourse.lastInsertRowid, 'Packet Analysis Lab', 'Analyze the provided pcap file and identify suspicious traffic. Submit your findings with evidence.', '2026-09-22');
  insertAssignment.run(cryptoCourse.lastInsertRowid, 'RSA Implementation', 'Implement RSA key generation, encryption, and decryption in your preferred language. Explain the math in your write-up.', '2026-10-05');

  const insertSchedule = db.prepare('INSERT INTO schedules (lecturer_id, day_of_week, start_time, end_time, subject) VALUES (?, ?, ?, ?, ?)');
  insertSchedule.run(lecturerId, 'Monday', '09:00', '11:00', 'Web Application Security');
  insertSchedule.run(lecturerId, 'Tuesday', '13:00', '15:00', 'Network Security Fundamentals');
  insertSchedule.run(lecturerId, 'Wednesday', '09:00', '10:30', 'Cryptography in Practice');
  insertSchedule.run(lecturerId, 'Thursday', '14:00', '16:00', 'CTF Preparation Lab');
  insertSchedule.run(lecturerId, 'Friday', '10:00', '12:00', 'Student Presentations');

  const insertForumPost = db.prepare('INSERT INTO forum_posts (course_id, author_id, content) VALUES (?, ?, ?)');
  insertForumPost.run(webCourse.lastInsertRowid, lecturerId, 'Welcome to the Web Application Security forum! Feel free to ask questions about the lectures or assignments here.');
  insertForumPost.run(webCourse.lastInsertRowid, adminId, 'Reminder: keep the forum discussion focused on course material. General questions go to the announcements page.');

  const backupDir = path.join(__dirname, '..', 'backup');
  if (!fs.existsSync(backupDir)) {
    fs.mkdirSync(backupDir, { recursive: true });
  }

  const adminBackup = {
    username: ADMIN_USERNAME,
    password_hash: adminHash,
    role: 'administrator',
    note: 'Legacy configuration backup. Migrated to database. TODO: Delete this file after migration.',
    created: '2025-06-15',
    system: 'Classroom Management System v1.0',
  };

  try {
    fs.writeFileSync(
      path.join(backupDir, 'admin_credentials.json'),
      JSON.stringify(adminBackup, null, 2)
    );
  } catch (err) {
    if (err.code !== 'EACCES' && err.code !== 'EPERM') throw err;
    console.log('Backup file already managed by watchdog - skipped write.');
  }
}

seed();
