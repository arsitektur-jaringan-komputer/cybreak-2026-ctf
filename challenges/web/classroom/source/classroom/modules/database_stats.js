
module.exports = {
  name: 'Database Statistics',
  description: 'Shows database statistics',
  run: function() {
    const db = require('../database/db');
    return {
      users: db.prepare('SELECT COUNT(*) as c FROM users').get().c,
      notes: db.prepare('SELECT COUNT(*) as c FROM notes').get().c,
      courses: db.prepare('SELECT COUNT(*) as c FROM courses').get().c,
    };
  }
};