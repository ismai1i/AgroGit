from flask import Flask, render_template, request, redirect, url_for
from azure.storage.blob import BlobServiceClient
import pypyodbc as odbc
import os
import uuid

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Azure Storage account information
account_name = 'agrohelperblob'
account_key = 'mss4yIG7ufi3mtbGOZiJyShQGw/lgKsaS2GRcMmg04dXr8ytilfo7Zrg7lfFuEnBWXAFkCH5qcc0+ASt3HiHEA=='

# Create a BlobServiceClient
azure_storage_connection_string = f"DefaultEndpointsProtocol=https;AccountName=agrohelperblob;AccountKey=mss4yIG7ufi3mtbGOZiJyShQGw/lgKsaS2GRcMmg04dXr8ytilfo7Zrg7lfFuEnBWXAFkCH5qcc0+ASt3HiHEA==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(azure_storage_connection_string)

# Database connection information
server = 'agrohelperserver.database.windows.net'
database = 'AgroDB'
username = 'serveradmin'
password = 'agroPWD1234'

# Establish a database connection
conn_string = f'Driver={{ODBC Driver 18 for SQL Server}};Server=agrohelperserver.database.windows.net;Database=AgroDB;Uid=serveradmin;Pwd=agroPWD1234;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
conn = odbc.connect(conn_string)

# Container name in Azure Blob Storage
container_name = 'agrohelpercontainer'

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']

        # Handling file upload (image)
        if 'file' in request.files:
            file = request.files['file']

            # Create a unique name for the blob
            blob_name = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]

            # Get a BlobClient instance
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

            # Upload the file to Azure Blob Storage
            blob_client.upload_blob(file)

            # Get the URL of the uploaded blob
            blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}"

            # Perform the SQL insertion with the blob URL
            cursor = conn.cursor()
            query = "INSERT INTO dbo.AgroSQL ([FirstName], [LastName], [Email], [file]) VALUES (?, ?, ?, ?);"
            cursor.execute(query, (firstName, lastName, email, blob_url))
            conn.commit()

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
