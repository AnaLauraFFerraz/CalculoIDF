const express = require("express");
const cors = require("cors");
const multer = require("multer");
const axios = require('axios');
require('dotenv').config();
const firebase = require('./firebase.cjs');
const rateLimit = require("express-rate-limit");

const app = express();
app.use(cors());

// Limit the size of the incoming requests to 2MB
app.use(express.json({ limit: '2mb' }));
app.use(express.urlencoded({ limit: '2mb', extended: true }));

// Apply rate limits to all requests
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 2 * 1024 * 1024 // limit file size to 2MB
  }
});

app.post('/upload', upload.single('file'), async(req, res) => {
  if (!req.file) {
    res.status(400).send({ message: 'Nenhum arquivo foi enviado' });
    return;
  }

  const csvFileName = req.file.originalname;
  const csvFilePath = `uploads/${csvFileName}`;
  
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
      try {
        const response = await axios.post(functionUrl, { csv_file_url: `${bucketUrl}/${csvFileName}` });
    
        console.log(`Response from Google Cloud Function: ${response.data}`);
    
        // Send the JSON received from the Google Cloud Function to the front-end
        res.status(200).send(response.data);
      } catch (error) {
        console.error(`Error calling Google Cloud Function: ${error}`);
        res.status(500).send({ message: 'Ocorreu um erro ao chamar a função do Google Cloud' });
      } finally {
        // Remove the CSV file from Firebase Storage
        await firebase.deleteFile(csvFileName);
      }
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