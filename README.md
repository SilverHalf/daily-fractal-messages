# Daily Fractals Script

This is a simple script that sends a message to a discord webhook with information on daily fractals.

Set the webhook url in a `.env` file:

```
WEBHOOK = 'https://discord.com/api/webhooks/...'
```

Install required libraries using `uv venv && uv sync`.

Fractal instabilities are calculated using [this data](https://github.com/Invisi/gw2-fotm-instabilities/tree/master).