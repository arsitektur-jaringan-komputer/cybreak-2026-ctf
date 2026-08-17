
module.exports = {
  name: 'System Information',
  description: 'Displays system information',
  run: function() {
    return {
      platform: process.platform,
      arch: process.arch,
      nodeVersion: process.version,
      uptime: process.uptime(),
      memory: process.memoryUsage(),
    };
  }
};