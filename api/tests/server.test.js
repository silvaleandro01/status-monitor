require('dotenv').config();

const request = require('supertest');
const app = require('../app');
const pool = require('../db');

const TEST_URL = 'https://jest.exemplo.invalid';

afterEach(async () => {
  await pool.query('DELETE FROM services WHERE url = $1', [TEST_URL]);
});

afterAll(async () => {
  await pool.end();
});

describe('GET /api/services', () => {
  test('retorna uma lista de serviços', async () => {
    const res = await request(app).get('/api/services');

    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});

describe('POST /api/services', () => {
  test('cria um serviço novo e retorna 201', async () => {
    const res = await request(app)
      .post('/api/services')
      .send({ name: 'Serviço de Teste (jest)', url: TEST_URL });

    expect(res.status).toBe(201);
    expect(res.body.id).toBeDefined();
    expect(res.body.name).toBe('Serviço de Teste (jest)');
    expect(res.body.url).toBe(TEST_URL);
  });

  test('retorna 400 quando falta um campo obrigatório', async () => {
    const res = await request(app).post('/api/services').send({ name: 'Sem URL' });

    expect(res.status).toBe(400);
  });
});

describe('GET /api/services/:id/checks', () => {
  test('retorna uma lista (vazia para um id inexistente)', async () => {
    const res = await request(app).get('/api/services/999999999/checks');

    expect(res.status).toBe(200);
    expect(res.body).toEqual([]);
  });
});
