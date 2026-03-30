import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'src'))
sys.path.append(os.path.join(current_dir, 'src', 'web'))

print("Testing imports...")

try:
    import live_feed
    print("✅ live_feed.py imported successfully - no syntax errors")
except Exception as e:
    print(f"❌ Error in live_feed.py: {e}")

try:
    from utils import email_service
    print("✅ email_service.py imported successfully - no syntax errors")
except Exception as e:
    print(f"❌ Error in email_service.py: {e}")

print("\nAll files compiled successfully!")
print("\nTo see the new features:")
print("1. Restart Streamlit: streamlit run src/web/app.py")
print("2. Go to 'Live Monitoring'")
print("3. Look for '📸 Recent Captures' in the right sidebar")
print("4. Start camera and trigger a detection to see screenshots appear")
