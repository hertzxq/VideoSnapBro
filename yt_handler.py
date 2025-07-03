import os
import re
import yt_dlp
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    if not filename:
        return "unnamed_file"
    
    # Replace invalid characters (including ｜ and standard |)
    filename = re.sub(r'[<>:"/\\|?*｜]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Remove non-ASCII characters (optional, remove if you want to keep Cyrillic)
    filename = re.sub(r'[^\x00-\x7F]+', '', filename)
    # Replace multiple underscores with a single one
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    # Convert to lowercase
    filename = filename.lower()
    # Limit filename length
    max_length = 100
    filename = filename[:max_length]
    
    if not filename:
        return "unnamed_file"
    
    return filename

def download_video(url, output_path='videos'):
    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(id)s_%(title)s.%(ext)s'),  
        'format': 'best[height<=1080]',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            sanitized_title = sanitize_filename(info.get('title') or 'unnamed_file')
            video_info = {
                'id': info.get('id'),
                'title': sanitized_title,
                'description': info.get('description'),
                'uploader': info.get('uploader'),
                'upload_date': info.get('upload_date'),
                'duration': info.get('duration'),
                'view_count': info.get('view_count'),
                'like_count': info.get('like_count'),
                'filename': os.path.join(output_path, f"{info.get('id')}_{sanitized_title}.mp4")
            }

            if os.path.exists(video_info['filename']):
                logger.info(f"Video already exists: {video_info['filename']}")
                return video_info
                
            ydl.download([url])
            logger.info(f"Successfully downloaded: {url}")
            return video_info
        except Exception as e:
            logger.error(f"Error downloading {url}: {str(e)}")
            raise

def find_video_by_id(video_id, output_path='videos'):
    """Find a video file in the output_path by its video ID."""
    logger.info(f"Searching for video with ID {video_id} in {output_path}")
    logger.info(f"Files found: {os.listdir(output_path)}")
    for file in os.listdir(output_path):
        if file.startswith(video_id) and file.endswith('.mp4'):
            return os.path.join(output_path, file)
    return None