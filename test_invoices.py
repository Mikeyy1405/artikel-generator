import os
import sys

# Test script to debug invoice loading issue

print("=== Testing Invoice API ===\n")

# Check if stripe is installed
try:
    import stripe
    print("✅ Stripe library installed")
    print(f"   Version: {stripe.__version__}")
except ImportError:
    print("❌ Stripe library NOT installed")
    sys.exit(1)

# Check environment variables
stripe_key = os.environ.get('STRIPE_SECRET_KEY', '')
if stripe_key:
    print(f"✅ STRIPE_SECRET_KEY is set (starts with: {stripe_key[:7]}...)")
    stripe.api_key = stripe_key
else:
    print("❌ STRIPE_SECRET_KEY is NOT set")
    print("   This is likely the problem!")

# Check if we can connect to Stripe
if stripe_key:
    try:
        # Try to list invoices (will fail if no customer, but tests connection)
        test = stripe.Invoice.list(limit=1)
        print("✅ Stripe API connection successful")
    except stripe.error.AuthenticationError as e:
        print(f"❌ Stripe authentication failed: {e}")
        print("   Check if STRIPE_SECRET_KEY is correct")
    except Exception as e:
        print(f"⚠️  Stripe API test: {e}")
        print("   (This might be normal if no customers exist)")

print("\n=== Checking Database ===\n")

# Check database
import sqlite3
DB_PATH = os.environ.get('DB_PATH', 'writgo.db')

try:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone():
        print("✅ Users table exists")
        
        # Check for stripe columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'stripe_customer_id' in columns:
            print("✅ stripe_customer_id column exists")
        else:
            print("❌ stripe_customer_id column MISSING")
        
        if 'remember_token' in columns:
            print("✅ remember_token column exists")
        else:
            print("⚠️  remember_token column missing (run migration)")
        
        # Check if any users have stripe_customer_id
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE stripe_customer_id IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"   Users with Stripe customer ID: {count}")
        
    else:
        print("❌ Users table does NOT exist")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")

print("\n=== Summary ===")
print("If you see errors above, that's likely causing the invoice loading issue.")
print("Most common issues:")
print("1. STRIPE_SECRET_KEY not set in Render environment")
print("2. Database migration not run yet")
print("3. User doesn't have stripe_customer_id (normal for new users)")

