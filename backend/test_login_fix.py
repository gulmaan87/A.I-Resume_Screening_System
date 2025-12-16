"""
Test script to verify login works after bcrypt fix.
"""
import asyncio
import httpx

async def test_login():
    """Test login with the test user."""
    print("=" * 60)
    print("Testing Login After Bcrypt Fix")
    print("=" * 60)
    print()
    
    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=10.0) as client:
        print("1. Testing login with user@example.com...")
        print()
        
        try:
            response = await client.post(
                "/api/auth/login",
                json={
                    "credentials": {
                        "email": "user@example.com",
                        "password": "strongpassword"
                    }
                }
            )
            
            print(f"Status Code: {response.status_code}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                print("✅ LOGIN SUCCESSFUL!")
                print(f"Access Token: {data.get('access_token', '')[:50]}...")
                print(f"Token Type: {data.get('token_type')}")
                print(f"Expires In: {data.get('expires_in')} seconds")
            else:
                print("❌ LOGIN FAILED")
                print(f"Response: {response.text}")
                print()
                print("Possible reasons:")
                print("- User doesn't exist (need to register first)")
                print("- Password is incorrect")
                print("- Bcrypt still has issues")
                
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_login())




