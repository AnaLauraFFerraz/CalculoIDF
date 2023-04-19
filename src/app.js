import express from "express"
import cors from "cors"
import multer from "multer"
import { PythonShell } from "python-shell"
import fs from "fs"
import { spawn } from"child_process"

const app = express();
const PORT = 5000

app.use(cors())
app.use(express.json())

const upload = multer({ dest: 'uploads/' });

// Cria o diretório 'uploads' se ele não existir
if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

app.post("/upload", upload.single("csv"), (req, res) => {
  // Executar o script Python
  const pythonOptions = {
    args: [req.file.path], // Passar o caminho do arquivo CSV como argumento
  };
  PythonShell.run("../../python_app/app.py", pythonOptions, (err) => {
    if (err) {
      console.error("Python error:", err);
      res.status(500).send("Error executing Python script");
      return;
    }

    // Ler o arquivo JSON gerado pelo script Python
    fs.readFile("ventechow_data.json", "utf8", (err, data) => {
      if (err) {
        console.error("File read error:", err);
        res.status(500).send("Error reading JSON file");
        return;
      }

      // Enviar o JSON para o front-end
      res.json(JSON.parse(data));
    });
  });
});


app.listen(PORT, () => {
  console.log(`Server listening at http://localhost:${PORT}`);
});
