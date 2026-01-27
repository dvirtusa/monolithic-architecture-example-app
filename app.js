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
        // Validate required fields
        const { name, email } = req.body;
        
        if (!name || !name.trim()) {
            return res.status(400).json({ 
                error: 'Validation failed', 
                message: 'Name is required and cannot be empty' 
            });
        }
        
        if (!email || !email.trim()) {
            return res.status(400).json({ 
                error: 'Validation failed', 
                message: 'Email is required and cannot be empty' 
            });
        }
        
        // Basic email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.trim())) {
            return res.status(400).json({ 
                error: 'Validation failed', 
                message: 'Please provide a valid email address' 
            });
        }
        
        // Check if email already exists
        const existingUser = await User.findOne({ email: email.trim() });
        if (existingUser) {
            return res.status(409).json({ 
                error: 'Registration failed', 
                message: 'A user with this email already exists' 
            });
        }

        const newUser = new User({
            name: name.trim(),
            email: email.trim()
        });

        const savedUser = await newUser.save();
        res.status(201).json(savedUser);
    } catch (err) {
        console.error('Registration error:', err.message);
        
        // Handle duplicate key error
        if (err.code === 11000) {
            return res.status(409).json({ 
                error: 'Registration failed', 
                message: 'A user with this email already exists' 
            });
        }
        
        res.status(500).json({ 
            error: 'Registration failed', 
            message: 'An unexpected error occurred. Please try again.' 
        });
    }
});

app.listen(8080);
console.log("Visit app at http://localhost:8080");
