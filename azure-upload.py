from __future__ import print_function
import os
import zipfile
from tqdm import tqdm
import glob
import socket
import random
from azure.storage.blob import ContainerClient
from azure.core.exceptions import ResourceExistsError
import sys
import socket
from dotenv import load_dotenv
import argparse

class AzureUploader(object):
    def __init__(self, dir, zip):
        self.service = None
        self.dir = dir
        self.zip = zip
        self.azure_client = None

    def check_prereqs(self):
        if not os.path.exists('.env'):
            print('Please create a .env file and populate local_folder, connection_string and container_name fields.')
            return False

        load_dotenv()
        self.connection_string = os.getenv('connection_string')
        self.container_name = os.getenv('container_name')

        if self.connection_string is None or self.container_name is None:
            print('Please create a .env file and populate connection_string and container_name values.')
            return False

        self.azure_client = ContainerClient.from_connection_string(self.connection_string, self.container_name)
        if self.azure_client is None:
            print('Error creating Azure Container client. Please check the connection_string or container_name stored in .env file')
            return False

        return True

    def zipdir(self, path, ziph):
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

    def upload(self):
        print('Uploading local folder: {} to Azure container {}'.format(self.dir, self.container_name))
        files_to_upload = []

        if self.zip == 'none':
            files_to_upload = list(glob.iglob(os.path.join(self.dir, '**', '*.*')))
            files_to_upload += list(glob.iglob(os.path.join(self.dir, '*.*')))

        elif self.zip == 'root':
            print('Commpressing directory: {}'.format(self.dir))
            zipfile_name = self.dir + '.zip'
            zipf = zipfile.ZipFile(zipfile_name, 'w', zipfile.ZIP_DEFLATED)
            self.zipdir(self.dir, zipf)
            zipf.close()
            files_to_upload = [zipfile_name]

        elif self.zip == 'child':
            folders = glob.glob(os.path.join(self.dir, '*'))
            files_to_upload = []
            print('Compressing individual directories:')
            print('\t\n'.join(folders))
            for folder in tqdm(folders):
                zipfile_name = os.path.dirname(folder) + '-' + os.path.basename(folder) + '.zip'
                zipf = zipfile.ZipFile(zipfile_name, 'w', zipfile.ZIP_DEFLATED)
                self.zipdir(self.dir, zipf)
                zipf.close()
                files_to_upload.append(zipfile_name)

        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        print('Uploading files to container: {}'.format(self.container_name))
        print('\t\n'.join(files_to_upload))

        for file in tqdm(files_to_upload):
            try:
                blob_client = self.azure_client.get_blob_client(file)
                with open(file, 'rb') as data:
                    blob_client.upload_blob(data)
            except ResourceExistsError as ex:
                print('\n... Error: resource already exists in container: {}'.format(file))
            except Exception as ex:
                print('\n... Error: Unknown exception occurred during upload of {}: {}'.format(file, ex))


        print('Upload complete.')
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')

def main():
    print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')

    # Parse arguments
    parser = argparse.ArgumentParser(description='Upload folders to Azure Blob Storage')
    parser.add_argument('-d', '--dir', help='Local folder to be uploaded.', type=str, action='store', required=True)
    parser.add_argument('-z', '--zip', help='Zip folders (root | child | none)', type=str, action='store', default='none')

    args = parser.parse_args()
    dir = args.dir
    zip = args.zip
    if not os.path.exists(dir):
        print('Error: Path {} does not exist'.format(dir))
        return -1

    # Create the Azure Blob Storage Uploader Object
    azureUploader = AzureUploader(dir, zip)

    # Check for pre-requisites.
    if azureUploader.check_prereqs() is False:
        print('Pre-requisites not met. Exiting.')
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        return -1

    # Upload folders
    if azureUploader.upload() is False:
        print('Error occurred during upload. Exiting.')
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')
        return -1

    # Done.
    print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ')

if __name__ == '__main__':
    main()
