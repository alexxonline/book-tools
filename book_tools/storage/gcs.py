from pathlib import Path

from book_tools.paths import OUTPUT_DIR


def download_all_files_from_bucket(bucket_name, destination_folder=None):
    from google.cloud import storage

    destination = Path(destination_folder) if destination_folder else OUTPUT_DIR / "downloads"
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    paths = []
    for blob in storage.Client().bucket(bucket_name).list_blobs():
        if blob.name.endswith("/"):
            continue
        path = destination / blob.name
        if not path.resolve().is_relative_to(root) or path.resolve() == root:
            raise ValueError(f"Unsafe blob path: {blob.name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(str(path))
        paths.append(path)
    return paths
