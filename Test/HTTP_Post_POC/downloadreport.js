const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = 4000; // Change the port number to avoid conflicts

// Middleware to parse JSON bodies
app.use(bodyParser.json());

// Define a route to receive JSON data via POST
app.post('/api/endpoint', (req, res) => {
    // Receive JSON data from the request body
    const jsonData = req.body;
    
    // Log received JSON data
    console.log("Received JSON data:", jsonData);
    
    // Send a response (echo the received data)
    res.json(jsonData);
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
