// Vercel Serverless Function — Gemini API 프록시
// API 키는 Vercel 환경변수에 저장 (GEMINI_IMAGE_API_KEY)

// body 파싱 한도 확장 (이미지 base64 포함 시 크기가 큼)
export const config = {
  api: {
    bodyParser: {
      sizeLimit: '20mb',
    },
  },
};

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'POST만 허용' });
  }

  const apiKey = process.env.GEMINI_IMAGE_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: '서버 API 키 미설정' });
  }

  try {
    // body가 문자열일 수 있음 (Vercel이 자동 파싱 못한 경우)
    let body = req.body;
    if (typeof body === 'string') {
      body = JSON.parse(body);
    }

    const { parts } = body;
    if (!parts || !Array.isArray(parts)) {
      return res.status(400).json({ error: `parts 배열이 필요합니다. 받은 body 타입: ${typeof req.body}` });
    }

    const model = 'gemini-3-pro-image-preview';
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts }],
        generationConfig: {
          responseModalities: ['TEXT', 'IMAGE'],
          temperature: 1.0,
        }
      })
    });

    const data = await response.json();

    if (data.error) {
      return res.status(response.status).json({ error: data.error.message || '생성 실패' });
    }

    return res.status(200).json(data);

  } catch (err) {
    return res.status(500).json({ error: `${err.message} | body type: ${typeof req.body} | body length: ${JSON.stringify(req.body).length}` });
  }
}
