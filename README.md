# SunoEscribe

SunoEscribe is an AI-powered audio transcription tool. Upload a song or audio file and get the lyrics transcribed in any supported language!

## Features

- Vocal isolation using Spleeter
- Multi-language transcription (Deepgram Nova-3)
- Automatic language detection
- Simple web frontend

## Setup

### Backend

1. Install dependencies:
   ```sh
   cd Backend
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your Deepgram API key.

### Frontend

1. Install dependencies:
   ```sh
   cd frontend
   npm install
   ```
2. Copy `.env.example` to `.env` and set your backend API URL.

## Running Locally

- Start backend:
  ```sh
  cd Backend
  uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
  ```
- Start frontend:
  ```sh
  cd frontend
  npm start
  ```

## Deployment

- Host frontend on Vercel/Netlify.
- Host backend on Render/Heroku.

## Environment Variables

- **Never commit `.env` files with secrets.**
- Use `.env.example` as a template.

## License

MIT