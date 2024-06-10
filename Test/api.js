const express = require('express');
const app = express();

// Mock device data
const devices = [
    { serial_no: "A00000001", mac_address: "xxxx" , matter_cert_id: "4ca99816-2e3d-4e6b-804b-ec27b9034298"},
    { serial_no: "A00000002", mac_address: "yyyy" , matter_cert_id: "b109915d-687b-4513-9f4a-a56f7e8f9073"},
    { serial_no: "A00000003", mac_address: "zzzz" , matter_cert_id: "a20671ec-9329-488a-9fbc-c5e7e19f2d79"}
];

// Endpoint to retrieve device data
app.get('/devices', (req, res) => {
    res.json(devices);
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

