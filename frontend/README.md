# ClipBrain Frontend

Next.js PWA frontend for ClipBrain.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local`:
```bash
cp .env.local.example .env.local
```

3. Update `NEXT_PUBLIC_API_URL` to point to your backend.

## Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Build

```bash
npm run build
npm start
```

## Deploy

Deploy to Vercel:
```bash
vercel
```

## Features

- PWA with Share Target API
- Search interface
- Video player
- Collections management
- Tag editing
- Export functionality
