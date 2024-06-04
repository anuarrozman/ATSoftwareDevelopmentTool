const express = require('express');
const app = express();

// Mock device data
const devices = [
    { serial_no: "A00000001", mac_address: "xxxx" , matter_cert_id: "54a1121b-dc1a-4b87-93f3-c7e5139c71c5"},
    { serial_no: "A00000002", mac_address: "yyyy" , matter_cert_id: "c2efeba3-abfd-4191-87d7-42985ab1747c"},
    { serial_no: "A00000003", mac_address: "zzzz" , matter_cert_id: "b1b05aa7-0697-4fb9-8277-2aee3d10854a"}
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

