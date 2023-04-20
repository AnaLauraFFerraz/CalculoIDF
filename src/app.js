import express from "express"
import cors from "cors"
import multer from "multer"
import fs from "fs"
import { spawn } from "child_process"
import path from "path"
import { fileURLToPath } from "url"

const app = express();
app.use(cors());

const upload = multer({ dest: 'uploads/' });

// Converta o caminho do arquivo URL em um caminho de arquivo local
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    res.status(400).send({ message: 'Nenhum arquivo foi enviado' });
    return;
  }

  const pythonAppPath = path.join(__dirname, '..', 'python_scripts', 'app.py');
  const csvFilePath = req.file.path;
  const idfDataPath = path.join(__dirname, "..", 'idf_data.json');

  const pythonProcess = spawn('python', [pythonAppPath, csvFilePath]);

  let errorOccurred = false;

  // Lida com erros ao executar o script Python
  pythonProcess.stderr.once('data', (data) => {
    console.error(`Erro ao executar o script Python: ${data}`);
    errorOccurred = true;
    res.status(500).send({ message: 'Erro ao executar o script Python' });
  });

  // Envia a resposta JSON ao cliente quando o script Python terminar
  pythonProcess.on('close', (code) => {
    if (errorOccurred) {
      return;
    }

    if (code !== 0) {
      console.error(`Erro após executar o script Python: ${code}`);
      res.status(500).send({ message: 'Erro ao executar o script Python' });
    } else {
      fs.readFile(idfDataPath, (err, data) => {
        if (err) {
          console.error(`Erro ao ler o arquivo IDF Data: ${err}`);
          res.status(500).send({ message: 'Erro ao ler o arquivo IDF Data' });
        } else {
          const idfData = JSON.parse(data);
          // console.log("JSON recebido:");
          // console.log(JSON.stringify(idfData, null, 2));

          res.status(200).send(idfData);
        }

        // Remove o arquivo CSV e IDF Data após o processamento
        fs.unlink(csvFilePath, (err) => {
          if (err) {
            console.error(`Erro ao remover o arquivo CSV: ${err}`);
          }
        });

        fs.unlink(idfDataPath, (err) => {
          if (err) {
            console.error(`Erro ao remover o arquivo IDF Data: ${err}`);
          }
        });
      });
    }
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
});