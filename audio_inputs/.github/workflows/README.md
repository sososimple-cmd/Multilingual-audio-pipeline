# Pixel Learning Co. Multilingual Audio Pipeline

## Overview
This pipeline automates converting English audio into multiple languages using AWS services and GitHub Actions.

## Requirements
- AWS Account with access to:
  - S3
  - Transcribe
  - Translate
  - Polly
- GitHub Repository
- `sample.mp3` in `audio_inputs/` folder

## Setup Instructions

### 1. AWS Setup
- Create an S3 bucket (e.g., `pixel-learning-audio-bucket`)
- Ensure your IAM user has full access to AWS services used.

### 2. GitHub Secrets
Add these secrets to your repo:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `S3_BUCKET`

### 3. Trigger Workflows
- Open a **pull request** to `main` branch to test in beta.
- **Merge to main** to deploy to production.

### 4. Outputs
All outputs are uploaded to S3:
- Transcripts → `beta/transcripts/`
- Translations → `beta/translations/`
- Audio Outputs → `beta/audio_outputs/`

This is to test the workflow