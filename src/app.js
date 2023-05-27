import express from "express"
import cors from "cors"
import multer from "multer"
import fs from "fs"
import path from "path"
import { fileURLToPath } from "url"
import axios from 'axios';
import bucket from './firebase';

const app = express();
app.use(cors());

const upload = multer({ dest: 'uploads/' });

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

app.post('/upload', upload.single('file'), async(req, res) => {
  if (!req.file) {
    res.status(400).send({ message: 'Nenhum arquivo foi enviado' });
    return;
  }

  const csvFilePath = req.file.path;

  const functionUrl = 'https://us-central1-calculoidf.cloudfunctions.net/process_request';

  try {
      const response = await axios.post(functionUrl, { csvFilePath });
      console.log(`Response from Google Cloud Function: ${response.data}`);
  } catch (error) {
      console.error(`Error calling Google Cloud Function: ${error}`);
  }

  res.status(200).send({ message: 'Arquivo enviado com sucesso' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});