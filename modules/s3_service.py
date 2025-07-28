import boto3
import os
import json
import uuid
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
import logging
from typing import Optional, Dict, Any, BinaryIO
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        """Initialize S3 service with Cloudflare R2 configuration"""
        self.bucket_name = os.getenv('R2_BUCKET_NAME', 'coxist-files')
        self.account_id = os.getenv('R2_ACCOUNT_ID')
        self.access_key_id = os.getenv('R2_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
        self.endpoint_url = os.getenv('R2_ENDPOINT_URL', 'https://0d355632f6abe6c1e9312175a17a04bf.r2.cloudflarestorage.com')
        
        # Validate required environment variables
        if not all([self.account_id, self.access_key_id, self.secret_access_key]):
            logger.warning("R2 credentials not fully configured. S3 operations will be disabled.")
            self.client = None
            return
        
        try:
            self.client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name='auto'  # Cloudflare R2 uses 'auto' region
            )
            logger.info(f"S3 client initialized successfully for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if S3 service is available and configured"""
        return self.client is not None
    
    def _generate_file_key(self, presentation_id: str, filename: str, file_type: str = 'presentations') -> str:
        """Generate a unique file key for S3 storage"""
        timestamp = datetime.now().strftime("%Y/%m/%d")
        safe_filename = filename.replace(' ', '_').replace('/', '_')
        return f"{file_type}/{presentation_id}/{timestamp}/{safe_filename}"
    
    def upload_file(self, file_path: str, presentation_id: str, filename: str, 
                   file_type: str = 'presentations', content_type: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to S3
        
        Args:
            file_path: Local path to the file
            presentation_id: Unique presentation identifier
            filename: Name of the file
            file_type: Type of file (presentations, images, etc.)
            content_type: MIME type of the file
            
        Returns:
            S3 URL of the uploaded file or None if failed
        """
        if not self.is_available():
            logger.error("S3 service not available")
            return None
        
        try:
            file_key = self._generate_file_key(presentation_id, filename, file_type)
            
            # Determine content type if not provided
            if not content_type:
                if filename.endswith('.pptx'):
                    content_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                elif filename.endswith('.pdf'):
                    content_type = 'application/pdf'
                elif filename.endswith('.json'):
                    content_type = 'application/json'
                elif filename.endswith(('.jpg', '.jpeg')):
                    content_type = 'image/jpeg'
                elif filename.endswith('.png'):
                    content_type = 'image/png'
                else:
                    content_type = 'application/octet-stream'
            
            # Upload file
            with open(file_path, 'rb') as file:
                self.client.upload_fileobj(
                    file,
                    self.bucket_name,
                    file_key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'Metadata': {
                            'presentation_id': presentation_id,
                            'uploaded_at': datetime.now().isoformat(),
                            'original_filename': filename
                        }
                    }
                )
            
            # Generate public URL
            file_url = f"{self.endpoint_url}/{self.bucket_name}/{file_key}"
            logger.info(f"File uploaded successfully: {file_url}")
            return file_url
            
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            return None
    
    def upload_file_data(self, file_data: bytes, presentation_id: str, filename: str,
                        file_type: str = 'presentations', content_type: Optional[str] = None) -> Optional[str]:
        """
        Upload file data directly to S3
        
        Args:
            file_data: File data as bytes
            presentation_id: Unique presentation identifier
            filename: Name of the file
            file_type: Type of file
            content_type: MIME type of the file
            
        Returns:
            S3 URL of the uploaded file or None if failed
        """
        if not self.is_available():
            logger.error("S3 service not available")
            return None
        
        try:
            file_key = self._generate_file_key(presentation_id, filename, file_type)
            
            # Determine content type if not provided
            if not content_type:
                if filename.endswith('.pptx'):
                    content_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                elif filename.endswith('.pdf'):
                    content_type = 'application/pdf'
                elif filename.endswith('.json'):
                    content_type = 'application/json'
                else:
                    content_type = 'application/octet-stream'
            
            # Upload file data
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_data,
                ContentType=content_type,
                Metadata={
                    'presentation_id': presentation_id,
                    'uploaded_at': datetime.now().isoformat(),
                    'original_filename': filename
                }
            )
            
            # Generate public URL
            file_url = f"{self.endpoint_url}/{self.bucket_name}/{file_key}"
            logger.info(f"File data uploaded successfully: {file_url}")
            return file_url
            
        except Exception as e:
            logger.error(f"Failed to upload file data for {filename}: {e}")
            return None
    
    def download_file(self, file_key: str, local_path: str) -> bool:
        """
        Download a file from S3 to local storage
        
        Args:
            file_key: S3 key of the file
            local_path: Local path where to save the file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("S3 service not available")
            return False
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            self.client.download_file(self.bucket_name, file_key, local_path)
            logger.info(f"File downloaded successfully to {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download file {file_key}: {e}")
            return False
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            file_key: S3 key of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("S3 service not available")
            return False
        
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"File deleted successfully: {file_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_key}: {e}")
            return False
    
    def list_presentation_files(self, presentation_id: str) -> list:
        """
        List all files for a specific presentation
        
        Args:
            presentation_id: Presentation identifier
            
        Returns:
            List of file information
        """
        if not self.is_available():
            logger.error("S3 service not available")
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"presentations/{presentation_id}/"
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'url': f"{self.endpoint_url}/{self.bucket_name}/{obj['Key']}"
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files for presentation {presentation_id}: {e}")
            return []
    
    def delete_presentation_files(self, presentation_id: str) -> bool:
        """
        Delete all files for a specific presentation
        
        Args:
            presentation_id: Presentation identifier
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("S3 service not available")
            return False
        
        try:
            files = self.list_presentation_files(presentation_id)
            
            if files:
                # Delete all files
                objects_to_delete = [{'Key': file['key']} for file in files]
                self.client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects_to_delete}
                )
                logger.info(f"Deleted {len(files)} files for presentation {presentation_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete files for presentation {presentation_id}: {e}")
            return False
    
    def get_file_url(self, file_key: str) -> Optional[str]:
        """
        Get the public URL for a file
        
        Args:
            file_key: S3 key of the file
            
        Returns:
            Public URL or None if not found
        """
        if not self.is_available():
            return None
        
        try:
            # Check if file exists
            self.client.head_object(Bucket=self.bucket_name, Key=file_key)
            return f"{self.endpoint_url}/{self.bucket_name}/{file_key}"
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.warning(f"File not found: {file_key}")
                return None
            else:
                logger.error(f"Error checking file {file_key}: {e}")
                return None
        except Exception as e:
            logger.error(f"Failed to get file URL for {file_key}: {e}")
            return None
    
    def upload_presentation_data(self, presentation_id: str, presentation_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Upload all presentation data to S3
        
        Args:
            presentation_id: Presentation identifier
            presentation_data: Dictionary containing presentation information
            
        Returns:
            Dictionary with URLs of uploaded files
        """
        uploaded_files = {}
        
        try:
            # Upload JSON data
            json_data = json.dumps(presentation_data, indent=2)
            json_url = self.upload_file_data(
                json_data.encode('utf-8'),
                presentation_id,
                f"{presentation_id}_structure.json",
                'presentations',
                'application/json'
            )
            if json_url:
                uploaded_files['json_url'] = json_url
            
            # Upload PowerPoint file if it exists
            if 'ppt_path' in presentation_data and os.path.exists(presentation_data['ppt_path']):
                ppt_url = self.upload_file(
                    presentation_data['ppt_path'],
                    presentation_id,
                    os.path.basename(presentation_data['ppt_path']),
                    'presentations',
                    'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                )
                if ppt_url:
                    uploaded_files['ppt_url'] = ppt_url
            
            logger.info(f"Uploaded {len(uploaded_files)} files for presentation {presentation_id}")
            return uploaded_files
            
        except Exception as e:
            logger.error(f"Failed to upload presentation data for {presentation_id}: {e}")
            return uploaded_files
    
    def create_temp_file(self, data: bytes, suffix: str = '') -> str:
        """
        Create a temporary file with the given data
        
        Args:
            data: File data as bytes
            suffix: File suffix (e.g., '.pptx', '.pdf')
            
        Returns:
            Path to the temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(data)
        temp_file.close()
        return temp_file.name
    
    def cleanup_temp_file(self, file_path: str):
        """
        Clean up a temporary file
        
        Args:
            file_path: Path to the temporary file
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")

# Global S3 service instance
s3_service = S3Service() 