# Azure Blob Storage Upload
Zip local files and upload to Azure Blob Storage.

## Overview
This repo has code for uploading any local files to an Azure Storage Container. You can use it for backing up your data in the cloud. 

You can either upload all the files one-by-one, or you can zip your local data and upload it.   

Please share any suggestions and improvements through the Issues section on github.

## Setup
* Clone this repository
```
git clone https://github.com/visionify/azure-files-upload.git
cd azure-files-upload
```

* Go to [Azure Portal](https://portal.azure.com) and create a storage account. 
* Create a container in this Storage account. Copy over the connection string. 
* Create a `.env` file in the root folder. 
* Add the connection_string and container_name in this `.env` file.
```
connection_string=your_connection_string_without quotes
container_name=your-container-name
```
* Install Python dependencies.
```
pip3 install -r requirements.txt
```
* Run the program
```
python3 azure-upload.py --dir directory-to-upload --zip root
```
* Program options
```
-d (--dir): Directory to upload to the Azure container
-z (--zip): Zip the folder(s) to be uploaded.  
    root  : Zip the entire root folder and upload to Azure Container.
    child : Zip any child folders under this root folder and upload them individually to the cloud.
    none  : Don't zip anything, upload all the files within this folder to Azure storage container. 
```

## Feedback
Please share any feedback and suggestions through the Issues tab on Github. You can learn more about the work we do at www.visionify.ai

