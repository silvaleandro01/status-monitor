const { WebSocketServer } = require('ws');
const { createClient } = require('redis');

const CHANNEL_NAME = 'service_status_updates';

function setupWebSocket(httpServer) {
  const wss = new WebSocketServer({ server: httpServer });

  wss.on('connection', (ws) => {
    console.log(`Cliente WebSocket conectado (${wss.clients.size} total)`);

    ws.on('close', () => {
      console.log(`Cliente WebSocket desconectado (${wss.clients.size} total)`);
    });
  });

  function broadcast(message) {
    for (const client of wss.clients) {
      if (client.readyState === client.OPEN) {
        client.send(message);
      }
    }
  }

  return { wss, broadcast };
}

async function startRedisSubscriber(broadcast) {
  const subscriber = createClient({
    socket: {
      host: process.env.REDIS_HOST,
      port: Number(process.env.REDIS_PORT),
    },
  });

  subscriber.on('error', (err) => console.error('Erro no Redis subscriber:', err));

  await subscriber.connect();

  await subscriber.subscribe(CHANNEL_NAME, (message) => {
    broadcast(message);
  });

  console.log(`Inscrito no canal Redis '${CHANNEL_NAME}'`);
}

module.exports = { setupWebSocket, startRedisSubscriber };
