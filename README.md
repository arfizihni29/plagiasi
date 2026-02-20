---
title: Plagiasi
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# 🔍 Plagiarism Detection API

A FastAPI-based plagiarism detection service that compares user-submitted text against web sources using **Google Search (Serper.dev)** and **TF-IDF cosine similarity**.

Built for student thesis/demo use — clean, modular, and ready to integrate with any frontend (PHP, JavaScript, etc.).

## 📁 Project Structure

```
plagiasi/
├── app/
│   ├── main.py                    # FastAPI application & endpoints
│   ├── services/
│   │   ├── serper_client.py       # Serper.dev Google Search client
│   │   ├── similarity.py         # TF-IDF cosine similarity
│   │   └── plagiarism_service.py  # Orchestration service
│   └── utils/
│       └── text_processing.py     # NLTK sentence splitting
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/plagiasi.git
cd plagiasi
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your Serper.dev API key
# SERPER_API_KEY=your_key_here
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

## 📡 API Endpoints

### `POST /check-plagiarism`

Check text for plagiarism.

**Request:**
```json
{
  "text": "Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data."
}
```

**Response:**
```json
{
  "overall_similarity": 78.5,
  "sentences": [
    {
      "sentence": "Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.",
      "similarity": 78.5,
      "source": "web"
    }
  ]
}
```

### `GET /health`

Health check endpoint — returns `{"status": "ok"}`.

## 🧪 Test with cURL

```bash
curl -X POST http://localhost:8000/check-plagiarism \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.\"}"
```

## 🔗 Integration with PHP

```php
$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL => 'http://localhost:8000/check-plagiarism',
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => json_encode(['text' => $userText]),
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
]);
$response = json_decode(curl_exec($ch), true);
curl_close($ch);

echo "Plagiarism Score: " . $response['overall_similarity'] . "%";
```

## ⚙️ How It Works

1. **Text Splitting** — Input text is split into individual sentences using NLTK
2. **Web Search** — Each sentence is searched on Google via Serper.dev API
3. **Similarity Scoring** — TF-IDF cosine similarity is computed between the sentence and each search result snippet
4. **Aggregation** — The highest similarity score across all sentences becomes the overall plagiarism score

## 📋 Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Server | Uvicorn |
| NLP | NLTK |
| ML | scikit-learn (TF-IDF + Cosine Similarity) |
| Search | Serper.dev API |

## 📝 Notes

- Sentences shorter than 5 words are skipped
- A 1-second delay is added between Serper queries to avoid rate limits
- HTTP requests to Serper have a 10-second timeout
- CORS is enabled for all origins (suitable for cross-domain API calls)
