const db = require('../database/db');

function logActivity(req, action, extraUser) {
  try {
    const userId = (req.session && req.session.user && req.session.user.id) || null;
    const username = (req.session && req.session.user && req.session.user.username) || (extraUser || null);
    const ip = req.headers && (req.headers['x-forwarded-for'] || req.socket.remoteAddress) || null;
    const ua = req.headers && req.headers['user-agent'] ? req.headers['user-agent'].substring(0, 200) : null;

    db.prepare(
      'INSERT INTO activity_logs (user_id, username, action, ip, user_agent) VALUES (?, ?, ?, ?, ?)'
    ).run(userId, username, action, ip, ua);
  } catch (e) {
    console.error('[ACTIVITY] Failed to log:', e.message);
  }
}

module.exports = { logActivity };
