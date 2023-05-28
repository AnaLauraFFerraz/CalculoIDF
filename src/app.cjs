const express = require("express");
const cors = require("cors");
const multer = require("multer");
const axios = require('axios');
const firebase = require('./firebase.cjs');

const app = express();
app.use(cors());

const upload = multer({ storage: multer.memoryStorage() });

app.post('/upload', upload.single('file'), async(req, res) => {
  if (!req.file) {
    res.status(400).send({ message: 'Nenhum arquivo foi enviado' });
    return;
  }

  const csvFilePath = `uploads/${req.file.originalname}`;

  try {
    // Upload the file to Firebase Storage
    await firebase.uploadFile(csvFilePath);

    const functionUrl = process.env.FUNCTION_URL;

    // Call the Google Cloud Function with the path of the CSV file in Firebase Storage
    const response = await axios.post(functionUrl, { csvFilePath });

    console.log(`Response from Google Cloud Function: ${response.data}`);

    // Send the JSON received from the Google Cloud Function to the front-end
    res.status(200).send(response.data);

    // Remove the CSV file from Firebase Storage
    await firebase.deleteFile(csvFilePath);
  } catch (error) {
    console.error(`Error: ${error}`);
    res.status(500).send({ message: 'Ocorreu um erro ao processar o arquivo' });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});