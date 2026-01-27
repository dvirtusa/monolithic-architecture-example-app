db = db.getSiblingDB('monolithic_app_db');

db.createUser({
  user: 'appuser',
  pwd: 'apppassword',
  roles: [
    {
      role: 'readWrite',
      db: 'monolithic_app_db'
    }
  ]
});

db.createCollection('users');

db.users.createIndex({ email: 1 }, { unique: true });

print('MongoDB initialization completed successfully');
