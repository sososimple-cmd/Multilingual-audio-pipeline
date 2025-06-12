# process_audio.py

import boto3
import os
import time
import requests

# Get environment variables from GitHub Actions
bucket = os.getenv('AWS_S3_BUCKET')
aws_region = os.getenv('AWS_REGION')

# Set up AWS clients
s3 = boto3.client('s3', region_name=aws_region)
transcribe = boto3.client('transcribe', region_name=aws_region)
translate = boto3.client('translate', region_name=aws_region)
polly = boto3.client('polly', region_name=aws_region)

# File info
filename = 'sample.mp3'
input_key = f'audio_inputs/{filename}'
output_prefix = 'beta'  # Will be 'prod' when merged to main

print("🚀 Starting Multilingual Audio Pipeline...")

# Step 1: Upload MP3 to S3
print("1️⃣ Uploading MP3 to S3...")
try:
    s3.upload_file(filename, bucket, input_key)
    print(f"✅ Uploaded {filename} to s3://{bucket}/{input_key}")
except Exception as e:
    print(f"❌ Failed to upload MP3: {e}")
    exit(1)

# Step 2: Start Transcription Job
print("2️⃣ Starting transcription job...")
job_name = f"transcribe_job_{int(time.time())}"
try:
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': f's3://{bucket}/{input_key}'},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )
except Exception as e:
    print(f"❌ Failed to start transcription job: {e}")
    exit(1)

# Wait for transcription to complete
while True:
    try:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("⏳ Waiting for transcription to complete...")
        time.sleep(5)
    except Exception as e:
        print(f"❌ Error checking transcription status: {e}")
        exit(1)

if status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
    print("❌ Transcription failed.")
    exit(1)

# Download transcript
print("📥 Downloading transcript...")
try:
    transcript_url = status['TranscriptionJob']['Transcript'].get('TranscriptFileUri')
    response = requests.get(transcript_url).json()
    text = response['results']['transcripts'][0]['transcript']
    print(f"📝 Transcribed Text: {text[:100]}...")  # Print first 100 chars
except Exception as e:
    print(f"❌ Failed to download transcript: {e}")
    exit(1)

# Save transcript locally
try:
    with open('transcript.txt', 'w') as f:
        f.write(text)
    print("💾 Transcript saved locally")
except Exception as e:
    print(f"❌ Failed to save transcript: {e}")
    exit(1)

# Upload transcript to S3
try:
    s3.upload_file('transcript.txt', bucket, f'{output_prefix}/transcripts/{filename}.txt')
    print(f"✅ Transcript uploaded to S3: s3://{bucket}/{output_prefix}/transcripts/{filename}.txt")
except Exception as e:
    print(f"❌ Failed to upload transcript: {e}")
    exit(1)

# Step 3: Translate to Spanish
print("3️⃣ Translating to Spanish...")
try:
    translated_text = translate.translate_text(
        Text=text,
        SourceLanguageCode='en',
        TargetLanguageCode='es'
    )['TranslatedText']
    print(f"🇪🇸 Translated Text: {translated_text[:100]}...")  # First 100 chars
except Exception as e:
    print(f"❌ Translation failed: {e}")
    exit(1)

# Save translation locally
try:
    with open('translation.txt', 'w') as f:
        f.write(translated_text)
    print("💾 Translation saved locally")
except Exception as e:
    print(f"❌ Failed to save translation: {e}")
    exit(1)

# Upload translation to S3
try:
    s3.upload_file('translation.txt', bucket, f'{output_prefix}/translations/{filename}_es.txt')
    print(f"✅ Translation uploaded to S3: s3://{bucket}/{output_prefix}/translations/{filename}_es.txt")
except Exception as e:
    print(f"❌ Failed to upload translation: {e}")
    exit(1)

# Step 4: Generate audio from translated text
print("4️⃣ Generating translated audio with Amazon Polly...")
try:
    response = polly.synthesize_speech(
        Text=translated_text,
        OutputFormat='mp3',
        VoiceId='Penelope'
    )
except Exception as e:
    print(f"❌ Polly synthesis failed: {e}")
    exit(1)

# Save synthesized audio locally
try:
    with open('translated_audio.mp3', 'wb') as f:
        f.write(response['AudioStream'].read())
    print("💾 Translated audio saved locally")
except Exception as e:
    print(f"❌ Failed to save translated audio: {e}")
    exit(1)

# Confirm file exists before upload
if not os.path.exists('translated_audio.mp3'):
    print("❌ Local audio file not found. Audio synthesis failed.")
    exit(1)

# Upload final audio to S3
try:
    s3.upload_file('translated_audio.mp3', bucket, f'{output_prefix}/audio_outputs/{filename}_es.mp3')
    print(f"✅ Audio uploaded to S3: s3://{bucket}/{output_prefix}/audio_outputs/{filename}_es.mp3")
except Exception as e:
    print(f"❌ Failed to upload audio: {e}")
    exit(1)

print("🎉 All steps completed successfully!")