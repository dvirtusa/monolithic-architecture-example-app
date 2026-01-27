const express = require('express');
const app = express();
const mongoose = require('mongoose');
const cors = require('cors');
const bodyParser = require("body-parser");

// This will allow our presentation layer to retrieve data from this API without
// running into cross-origin issues (CORS)
app.use(cors());
app.use(bodyParser.json());

// Connect to running database
const mongoHost = process.env.MONGODB_HOST || '127.0.0.1';
const mongoUri = `mongodb://${process.env.DB_USER}:${process.env.DB_PW}@${mongoHost}:27017/monolithic_app_db?authSource=monolithic_app_db`;

mongoose.connect(mongoUri)
    .then(() => {
        console.log('Successfully connected to MongoDB');
    })
    .catch((err) => {
        console.error('MongoDB connection error:', err.message);
    });

// Handle connection events
mongoose.connection.on('error', (err) => {
    console.error('MongoDB error:', err.message);
});

mongoose.connection.on('disconnected', () => {
    console.log('MongoDB disconnected');
});

// User schema for mongodb
const UserSchema = mongoose.Schema({
    name: { type: String },
    email: { type: String }
}, { collection: 'users' });

// Define the mongoose model for use below in method
const User = mongoose.model('User', UserSchema);

function getUserByEmail(email, callback) {
    try {
        User.findOne({ email: email }, callback);
    } catch (err) {
        callback(err);
    }
};

// set the view engine to ejs
app.set('view engine', 'ejs');

// index page 
app.get('/', function(req, res) {
    res.render('home');
});

// Health check endpoint
app.get('/health', function(req, res) {
    res.status(200).json({ status: 'healthy' });
});

app.post('/register', async function(req, res) {
    try {
        const newUser = new User({
            name: req.body.name,
            email: req.body.email
        });

        const savedUser = await newUser.save();
        res.status(200).json(savedUser);
    } catch (err) {
        console.error('Registration error:', err.message);
        res.status(500).json({ 
            error: 'Registration failed', 
            message: err.message 
        });
    }
});

app.listen(8080);
console.log("Visit app at http://localhost:8080");
