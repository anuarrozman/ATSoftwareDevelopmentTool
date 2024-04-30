const express = require('express');
const app = express();

// Mock device data
const devices = [
    { mac_address: "00:11:22:33:44:55", serial_number: "SN123" },
    { mac_address: "AA:BB:CC:DD:EE:FF", serial_number: "SN456" },
    { mac_address: "11:22:33:44:55:66", serial_number: "SN789" }
];

// Endpoint to retrieve device data
app.get('/serialnumber', (req, res) => {
    res.json(devices);
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
