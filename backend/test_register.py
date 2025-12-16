import asyncio

import httpx


async def main() -> None:
  """Simple script to verify /auth/register works with correct JSON body.

  Run this while your FastAPI app is running (uvicorn / backend server).
  """
  async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
    resp = await client.post(
      "/api/auth/register",
      json={
        "user_data": {
          "email": "user@example.com",
          "password": "strongpassword",
          "full_name": "User Name",
        },
      },
    )
    print("Status:", resp.status_code)
    try:
      print("Response JSON:", resp.json())
    except Exception:
      print("Raw response:", resp.text)


if __name__ == "__main__":
  asyncio.run(main())


