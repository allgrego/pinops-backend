SHELL := /bin/bash

# Start the development server (dependencies installation and .env.local file are required)
.PHONY: up
up:
	source .env && uvicorn app.main:app --host 0.0.0.0 --port 8200 --reload

# # Build and start the next project in prod mode
# .PHONY: prod
# prod:
# 	npm run build && npm start


