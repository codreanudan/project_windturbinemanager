import pymongo
import certifi

uri = "mongodb+srv://dbUser:dbUserPassword@cluster0.wtnbkwh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tls=true&tlsAllowInvalidCertificates=true"
client = pymongo.MongoClient(uri, tls=True, tlsCAFile=certifi.where())
client.admin.command("ping")
print("✅ Connected to MongoDB!")
