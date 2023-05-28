const express = require("express");
const cors = require("cors");
const multer = require("multer");
const axios = require('axios');
require('dotenv').config();
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
    const file = firebase.bucket.file(csvFileName);
    const stream = file.createWriteStream({
      metadata: {
        contentType: req.file.mimetype
      }
    });

    stream.end(req.file.buffer);

    stream.on('error', (error) => {
      console.error(`Error: ${error}`);
      res.status(500).send({ message: 'Ocorreu um erro ao fazer o upload do arquivo' });
    });

    stream.on('finish', async() => {
      console.log(`${csvFileName} uploaded to Firebase Storage.`);

      const functionUrl = process.env.FUNCTION_URL;

      // Call the Google Cloud Function with the path of the CSV file in Firebase Storage
      const bucketUrl = process.env.FIREBASE_STORAGE_BUCKET_URL;
      const response = await axios.post(functionUrl, { csvFilePath: `${bucketUrl}/${csvFileName}` });

      console.log(`Response from Google Cloud Function: ${response.data}`);

      // Send the JSON received from the Google Cloud Function to the front-end
      res.status(200).send(response.data);

      // Remove the CSV file from Firebase Storage
      await firebase.deleteFile(csvFileName);
    });
  } catch (error) {
    console.error(`Error: ${error}`);
    res.status(500).send({ message: 'Ocorreu um erro ao processar o arquivo' });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});