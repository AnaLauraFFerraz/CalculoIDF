import express from "express"
import cors from "cors"
import { PythonShell } from "python-shell"

const app = express();

server.use(express.json())
server.use(cors())

const PORT = 5000

app.post('/calculate', async (req, res) => {
    const pythonOptions = {
        scriptPath: './',
        pythonPath: 'python3',
        args: JSON.stringify(req.body.data)
    };

    PythonShell.run('your_python_script.py', pythonOptions, (err, results) => {
        if (err) {
            console.error(err);
            res.status(500).send({ error: 'An error occurred while running the Python script.' });
        } else {
            const output = JSON.parse(results[0]);
            res.status(200).send({ data: output });
        }
    });
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${PORT}`);
});
