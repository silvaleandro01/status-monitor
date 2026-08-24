require('dotenv').config();

const http = require('http');
const app = require('./app');
const { setupWebSocket, startRedisSubscriber } = require('./websocket');

const httpServer = http.createServer(app);
const { broadcast } = setupWebSocket(httpServer);
startRedisSubscriber(broadcast);

const PORT = process.env.PORT || 3000;
httpServer.listen(PORT, () => {
  console.log(`API rodando em http://localhost:${PORT}`);
});
