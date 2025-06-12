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

print("Step 1: Uploading MP3 to S3...")
s3.upload_file(filename, bucket, input_key)

print("Step 2: Starting transcription job...")
job_name = f"transcribe_job_{int(time.time())}"
transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': f's3://{bucket}/{input_key}'},
    MediaFormat='mp3',
    LanguageCode='en-US'
)

# Wait for transcription to complete
while True:
    status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    time.sleep(5)

if status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
    print("❌ Transcription failed.")
    exit(1)

# Download transcript
transcript_url = status['TranscriptionJob']['Transcript'].get('TranscriptFileUri')
print("Downloading transcript...")
response = requests.get(transcript_url).json()
text = response['results']['transcripts'][0]['transcript']
print("Transcribed Text:", text)

# Save transcript locally
with open('transcript.txt', 'w') as f:
    f.write(text)

# Upload transcript to S3
s3.upload_file('transcript.txt', bucket, f'{output_prefix}/transcripts/{filename}.txt')
print(f"Uploaded transcript to S3: {bucket}/{output_prefix}/transcripts/{filename}.txt")

print("Step 3: Translating text to Spanish...")
translated_text = translate.translate_text(
    Text=text,
    SourceLanguageCode='en',
    TargetLanguageCode='es'
)['TranslatedText']
print("Translated Text:", translated_text)

# Save translation
with open('translation.txt', 'w') as f:
    f.write(translated_text)

# Upload translation to S3
s3.upload_file('translation.txt', bucket, f'{output_prefix}/translations/{filename}_es.txt')
print(f"Uploaded translation to S3: {bucket}/{output_prefix}/translations/{filename}_es.txt")

print("Step 4: Generating audio with Amazon Polly...")
response = polly.synthesize_speech(
    Text=translated_text,
    OutputFormat='mp3',
    VoiceId='Penelope'
)

# Save synthesized audio
with open('translated_audio.mp3', 'wb') as f:
    f.write(response['AudioStream'].read())

# Upload final audio to S3
s3.upload_file('translated_audio.mp3', bucket, f'{output_prefix}/audio_outputs/{filename}_es.mp3')
print(f"Uploaded audio to S3: {bucket}/{output_prefix}/audio_outputs/{filename}_es.mp3")

print("✅ All steps completed successfully!")