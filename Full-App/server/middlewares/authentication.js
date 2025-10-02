function checkAuthenticated(req, res, next) {
    if (req.isAuthenticated()) {
      return next();
    }
    res.status(401).json({ message: 'Not authenticated' });
  }
  
  function checkNotAuthenticated(req, res, next) {
    if (req.isAuthenticated()) {
      return res.status(403).json({ message: 'Already authenticated' });
    }
    next();
  }
  
  module.exports = { checkAuthenticated, checkNotAuthenticated };
  