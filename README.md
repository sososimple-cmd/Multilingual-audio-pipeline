# Pixel Learning Co. Multilingual Audio Pipeline

This project automates the conversion of English audio into multiple languages using AWS services and GitHub Actions.

## 📋 What This Project Does

- Takes an `.mp3` file as input
- Uses **Amazon Transcribe** to convert speech to text
- Uses **Amazon Translate** to translate the transcript into Spanish
- Uses **Amazon Polly** to generate translated audio
- Uploads all outputs to **Amazon S3** in structured folders

---

## 🔧 How to Set Up the Required AWS Resources

### 1. Amazon S3 (Storage)
- Go to the S3 Console 
- Create a new bucket (e.g., `pixel-learning-audio-bucket`)
- Inside the bucket, create these folders:
  - `beta/transcripts/`
  - `beta/translations/`
  - `beta/audio_outputs/`
  - `prod/transcripts/`
  - `prod/translations/`
  - `prod/audio_outputs/`

### 2. IAM User (Permissions)
- Go to IAM Console
- Create a new user with programmatic access
- Attach these policies:
  - `AmazonS3FullAccess`
  - `AmazonTranscribeFullAccess`
  - `AmazonTranslateFullAccess`
  - `AmazonPollyFullAccess`

> Save the **Access Key ID** and **Secret Access Key** — you’ll use them in GitHub Secrets.

### 3. No Extra Setup Needed for AWS Services
- Amazon Transcribe, Translate, and Polly are fully managed services
- You can use them directly via Python script without additional configuration

---

## 🧾 How to Configure GitHub Secrets

GitHub Actions securely accesses AWS using secrets.

### Steps:
1. Go to your GitHub repository → **Settings**
2. Click on **Secrets and variables → Actions**
3. Add these secrets:

| Secret Name | Description |
|-------------|-------------|
| `AWS_ACCESS_KEY_ID` | From your AWS IAM user |
| `AWS_SECRET_ACCESS_KEY` | From your AWS IAM user |
| `AWS_REGION` | Your AWS region (e.g., `us-east-1`) |
| `AWS_S3_BUCKET` | Your S3 bucket name (e.g., `pixel-learning-audio-bucket`)

These allow your workflows to interact with AWS without hardcoding credentials.

---

## 🎬 How to Trigger Workflows by Adding `.mp3` Files

### 1. Add `.mp3` files to your local repo:
- Place your audio files in the `audio_inputs/` folder
- Example: `audio_inputs/sample.mp3`

### 2. Run Locally (Optional):
You can test locally before pushing:
```bash
cp audio_inputs/sample.mp3 .
python process_audio.py

```

### 3. Push to GitHub to Trigger Workflow
For Pull Request (Beta Environment):
Create a new branch

``` bash
git checkout -b feature/test
```
Make any small change (e.g., add a space to README.md)
Commit and push

```bash
git add .
git commit -m "Test workflow"
git push origin feature/test

```
Open a Pull Request targeting main
Go to Actions tab to see the workflow run
For Merge to Main (Production Environment):
After reviewing the PR, click Merge pull request
The on_merge.yml workflow will run automatically
Outputs will be uploaded to the prod/ prefix in S3



### 📁 How to Verify Results in S3 Folders
After the workflow runs successfully, check your S3 bucket for output files:

For Beta (via Pull Request):
beta/transcripts/sample.mp3.txt
beta/translations/sample.mp3_es.txt
beta/audio_outputs/sample.mp3_es.mp3
For Production (via Merge to Main):
prod/transcripts/sample.mp3.txt
prod/translations/sample.mp3_es.txt
prod/audio_outputs/sample.mp3_es.mp3
Steps:
Go to the S3 Console
Open your bucket (e.g., pixel-learning-audio-bucket)
Navigate to the appropriate folder (beta/ or prod/)
Confirm the files were uploaded correctly


### 📁 Folder Structure Summary
 And Finally this is how the overall structure should look:

``` bash

multilingual-audio-pipeline/
├── audio_inputs/
│   └── sample.mp3       # Your MP3 file
├── .github/
│   └── workflows/
│       ├── on_pull_request.yml   # Runs when you open a PR
│       └── on_merge.yml          # Runs when you merge to main
├── process_audio.py              # Main Python script
└── README.md                     # This file

```
