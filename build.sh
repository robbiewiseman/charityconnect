#!/usr/bin/env bash
# VERSION 6 START
# Render build script — runs during each deploy
# Reference: Render Build and Start Commands (Render, 2025)
# https://docs.render.com/deploy-flask

# Install Python dependencies
pip install -r requirements.txt

# Create database tables if they don't already exist
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all(); print('Database tables ready.')"
# VERSION 6 END