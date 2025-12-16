import os
from google.cloud import storage

def download_all_files_from_bucket(bucket_name, destination_folder):
    """
    Downloads all files from the specified Google Cloud Storage bucket to the destination folder.
    """
    # Set up credentials if needed
    #TODO: SETUP outside to credentials file|
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    print(f"Downloading files from bucket: {bucket_name}")
    for blob in blobs:
        dest_path = os.path.join(destination_folder, blob.name)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        print(f"Downloading {blob.name} to {dest_path}")
        blob.download_to_filename(dest_path)
    print("Download complete.")

if __name__ == "__main__":
    # Change these as needed
    BUCKET_NAME = "audio_generation_folder"  # Replace with your bucket name
    DESTINATION_FOLDER = "downloaded_files"  # Local folder to save files
    download_all_files_from_bucket(BUCKET_NAME, DESTINATION_FOLDER)
