require('dotenv').config();

const http = require('http');
const express = require('express');
const cors = require('cors');
const pool = require('./db');
const { setupWebSocket, startRedisSubscriber } = require('./websocket');

const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/services', async (req, res) => {
  const result = await pool.query('SELECT id, name, url, is_active FROM services ORDER BY id');
  res.json(result.rows);
});

app.post('/api/services', async (req, res) => {
  const { name, url } = req.body;

  if (!name || !url) {
    return res.status(400).json({ error: 'name e url são obrigatórios' });
  }

  const result = await pool.query(
    'INSERT INTO services (name, url) VALUES ($1, $2) RETURNING id, name, url, is_active',
    [name, url]
  );
  res.status(201).json(result.rows[0]);
});

app.get('/api/services/:id/checks', async (req, res) => {
  const { id } = req.params;

  const result = await pool.query(
    `SELECT status, status_code, response_time_ms, error_message, checked_at
     FROM checks
     WHERE service_id = $1
     ORDER BY checked_at DESC
     LIMIT 50`,
    [id]
  );
  res.json(result.rows);
});

const httpServer = http.createServer(app);
const { broadcast } = setupWebSocket(httpServer);
startRedisSubscriber(broadcast);

const PORT = process.env.PORT || 3000;
httpServer.listen(PORT, () => {
  console.log(`API rodando em http://localhost:${PORT}`);
});
