import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient

if __name__ == "__main__":
    load_dotenv()

    clientID=os.getenv("AZURE_CLIENT_ID")
    tenantID=os.getenv("AZURE_TENANT_ID")
    clientSecret=os.getenv("AZURE_CLIENT_SECRET")
    storage_account=os.getenv("AZURE_STORAGE_ACCOUNT")
    container_bronze=os.getenv("AZURE_CONTAINER_BRONZE")
    container_silver=os.getenv("AZURE_CONTAINER_SILVER")
    container_gold=os.getenv("AZURE_CONTAINER_GOLD")

    
    print("Testing Azure Connections....")
    container_list=[
        os.getenv("AZURE_CONTAINER_BRONZE"),
        os.getenv("AZURE_CONTAINER_SILVER"),
        os.getenv("AZURE_CONTAINER_GOLD"),
        ]
    results={}
    try:
        print("Checking Credentionals:")
        credentional=ClientSecretCredential(
            tenant_id=tenantID,
            client_id=clientID,
            client_secret=clientSecret
        )
        print("Credentials loaded")

        #creating Blob client
        blob_service_client = BlobServiceClient(account_url=f"https://{storage_account}.blob.core.windows.net/", credential=credentional)

        print("Printing Blobs available ...")

        containers = blob_service_client.list_containers(include_metadata=True)
        for container_name in container_list:
            print(f"Testing {container_name} container:")
            try:
                container = blob_service_client.get_container_client(container_name)

                #writing a file to the container
                container.upload_blob(
                    name=f"connection_test/test_{container_name}.txt",
                    data=f"{container_name} container test".encode(),
                    overwrite=True
                    )
                print(f"Written file and uploaded to {container_name} successfully")

                #reading the contents
                blob = container.download_blob(f"connection_test/test_{container_name}.txt")
                content = blob.readall().decode()
                print(f"Read from {container_name} successful — '{content}'")

                #clean up
                container.delete_blob(f"connection_test/test_{container_name}.txt")
                print(f" Cleanup successful")
                results[container_name] = "PASS"

            except Exception as e:
                print(f"Container Connection failed for {container_name}: {e}")
                print("Check .env creditionals")
                results[container_name]= "Fail"
        print("CONNECTION TEST SUMMARY")
        for container_name, status in results.items():
            print(f"  {status}  {container_name}")

        if all("PASS" in v for v in results.values()):
            print("\nAll containers operational.")
            print("You can go through the ELT pipeline.")
        else:
            print("\nSome containers failed — check errors above.")
        credentional.close()
    except Exception as e:
        print(f"Connection Failed: {e}")
        print("Check your API URL in the .env")
        credentional.close()