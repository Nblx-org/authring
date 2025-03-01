#!/bin/bash

API_KEY="$1"
# Basic chat completion
curl http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "google/gemini-2.0-flash-thinking-exp:free",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Tell me a short joke about programming."}
    ]
  }'

# Streaming version
curl http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "google/gemini-2.0-flash-thinking-exp:free",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    "stream": true
  }'

# With temperature and max tokens
curl http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "google/gemini-2.0-flash-thinking-exp:free",
    "messages": [
      {"role": "user", "content": "Write a haiku about Python programming."}
    ],
    "temperature": 0.7,
    "max_tokens": 50
  }'

# Multi-turn conversation
curl http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "model": "google/gemini-2.0-flash-thinking-exp:free",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant who speaks like a pirate."},
      {"role": "user", "content": "How do I make pancakes?"},
      {"role": "assistant", "content": "Arr matey! To make fine pancakes ye need: flour, eggs, milk, and a dash o\u0027 salt! Mix \u0027em together till smooth as the calm Caribbean seas!"},
      {"role": "user", "content": "What toppings would you recommend?"}
    ]
  }'
