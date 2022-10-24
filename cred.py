import boto3
import conf
import os

INPUT_BUCKET_NAME = conf.S3_BUCKET_INPUT
ARCHIVE_BUCKET_NAME = conf.S3_BUCKET_ARCHIVE
s3 = boto3.resource('s3', aws_access_key_id = conf.ACCESS_KEY, 
                              aws_secret_access_key= conf.SECRET_KEY)
							  
def s3_access():
    # enter authentication credentials
    
    os.makedirs(conf.INPUT_FILE_FOLDER, exist_ok=True)
    my_bucket = s3.Bucket(INPUT_BUCKET_NAME)
    for s3_object in my_bucket.objects.all():
        path, filename = os.path.split(s3_object.key)
        my_bucket.download_file(s3_object.key, conf.INPUT_FILE_FOLDER + '/' + filename)
		
def archive_input_files():
	src = s3.Bucket(INPUT_BUCKET_NAME)
	for object in src.objects.all():
		copy_source = {
			'Bucket': INPUT_BUCKET_NAME,
			'Key': object.key
			}
		s3.meta.client.copy(copy_source, ARCHIVE_BUCKET_NAME, object.key)
		response = s3.meta.client.delete_object(
			Bucket=INPUT_BUCKET_NAME,
			Key=object.key,
			)
	