from pymongo import MongoClient

from config import settings

client = MongoClient(settings.DATABASE_URL, serverSelectionTimeoutMS=5000)

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:
    print("Unable to connect MongoDB Server.")

db = client[settings.MONGO_INITDB_DATABASE]

PropertyDetail = db.property_detail
Users = db.users
UserSubscriptionPlan = db.subscription_plans
UserSubscription = db.user_subscription
Tenants = db.tenants
Owners = db.owners
PropertyAccessLog = db.property_access_log
UserSubscriptionHistory = db.user_subscription_history
UsersProfile = db.users_profile
UsersFeedback = db.users_feedback
ServiceRequest = db.service_request
UsersAddress = db.users_address
UsersFavorites = db.users_favorites_properties
PropertyReports = db.property_reports
