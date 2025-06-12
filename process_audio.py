# process_audio.py

import boto3
import os
import time
import requests

# Get environment variables (from GitHub Secrets)
bucket = os.getenv('AWS_S3_BUCKET')
aws_region = os.getenv('AWS_REGION')

# Connect to AWS services
s3 = boto3.client('s3', region_name=aws_region)
transcribe = boto3.client('transcribe', region_name=aws_region)
translate = boto3.client('translate', region_name=aws_region)
polly = boto3.client('polly', region_name=aws_region)

# File info
filename = 'sample.mp3'
input_key = f'audio_inputs/{filename}'
output_prefix = 'beta'

print("Uploading MP3 to S3...")
s3.upload_file(filename, bucket, input_key)

print("Starting transcription...")
job_name = f"job_{int(time.time())}"
transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': f's3://{bucket}/{input_key}'},
    MediaFormat='mp3',
    LanguageCode='en-US'
)

# Wait for transcription
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
response = requests.get(transcript_url).json()
text = response['results']['transcripts'][0]['transcript']
print("Transcribed Text:", text)

# Save transcript
with open('transcript.txt', 'w') as f:
    f.write(text)
s3.upload_file('transcript.txt', bucket, f'{output_prefix}/transcripts/{filename}.txt')

# Translate to Spanish
translated_text = translate.translate_text(Text=text, SourceLanguageCode='en', TargetLanguageCode='es')['TranslatedText']
print("Translated Text:", translated_text)

# Save translation
with open('translation.txt', 'w') as f:
    f.write(translated_text)
s3.upload_file('translation.txt', bucket, f'{output_prefix}/translations/{filename}_es.txt')

# Generate audio from translated text
response = polly.synthesize_speech(
    Text=translated_text,
    OutputFormat='mp3',
    VoiceId='Penelope'
)

# Save and upload new audio
with open('translated_audio.mp3', 'wb') as f:
    f.write(response['AudioStream'].read())
s3.upload_file('translated_audio.mp3', bucket, f'{output_prefix}/audio_outputs/{filename}_es.mp3')

print("✅ All steps completed!")