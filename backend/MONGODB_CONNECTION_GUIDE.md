# MongoDB Connection Troubleshooting Guide

## Permanent DNS Resolution Fix

This guide explains the robust MongoDB connection system that automatically handles DNS failures and provides fallback options.

## Features

✅ **Automatic DNS Fallback** - Tries multiple DNS servers if system DNS fails  
✅ **Connection Retry Logic** - Retries failed connections automatically  
✅ **Local MongoDB Fallback** - Falls back to local MongoDB if Atlas fails  
✅ **Enhanced Connection Options** - Optimized timeouts and pooling  
✅ **Detailed Error Logging** - Clear messages for troubleshooting  

## How It Works

1. **Primary Connection**: Tries to connect to MongoDB Atlas (your configured DB_URI)
2. **DNS Resolution**: Attempts to resolve hostname using:
   - System DNS
   - Google DNS (8.8.8.8, 8.8.4.4)
   - Cloudflare DNS (1.1.1.1, 1.0.0.1)
   - OpenDNS (208.67.222.222)
3. **Connection Retry**: Retries up to 3 times with delays
4. **Fallback**: If Atlas fails, automatically tries local MongoDB (localhost:27017)
5. **Graceful Degradation**: App continues running but database operations will fail

## Configuration Options

### Environment Variables

Add these to your `.env` file:

```bash
# Primary MongoDB Atlas connection
DB_URI=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority

# Optional: Fallback MongoDB URI (if Atlas fails)
MONGO_FALLBACK_URI=mongodb://localhost:27017/?serverSelectionTimeoutMS=5000

# Database name
DB_NAME=Resume_Screening
```

### Using Local MongoDB (Development)

If you have persistent DNS issues, use local MongoDB:

1. **Start MongoDB with Docker**:
   ```bash
   docker run -d -p 27017:27017 --name resume-mongo mongo:6.0
   ```

2. **Update .env**:
   ```bash
   DB_URI=mongodb://localhost:27017
   DB_NAME=Resume_Screening
   ```

3. **Or let it auto-fallback**: The system will automatically try localhost if Atlas fails

## Troubleshooting

### Issue: DNS Resolution Timeout

**Symptoms:**
- Error: "The resolution lifetime expired"
- Cannot resolve `cluster1.jczm3i1.mongodb.net`

**Solutions:**

1. **Check Internet Connection**:
   ```powershell
   ping google.com
   ping 8.8.8.8
   ```

2. **Test DNS Resolution**:
   ```powershell
   nslookup cluster1.jczm3i1.mongodb.net
   Resolve-DnsName cluster1.jczm3i1.mongodb.net
   ```

3. **Change DNS Servers** (Windows):
   - Open Network Settings
   - Change DNS to: `8.8.8.8` and `8.8.4.4` (Google DNS)
   - Or: `1.1.1.1` and `1.0.0.1` (Cloudflare DNS)

4. **Use Local MongoDB**: See "Using Local MongoDB" above

### Issue: MongoDB Atlas Connection Failed

**Symptoms:**
- Error: "Server selection timeout"
- Cannot connect to Atlas cluster

**Solutions:**

1. **Check IP Whitelist**:
   - Go to MongoDB Atlas Dashboard
   - Network Access → IP Access List
   - Add your current IP or `0.0.0.0/0` for testing (less secure)

2. **Check Firewall**:
   - Ensure port 27017 is not blocked
   - Check Windows Firewall settings

3. **Verify Credentials**:
   - Check DB_URI in `.env` file
   - Ensure username/password are correct

4. **Use Fallback**: System will automatically try local MongoDB

### Issue: Connection Works But Slow

**Solutions:**

1. **Check Network Speed**: Test internet connection
2. **Use Local MongoDB**: For development, local is faster
3. **Optimize Connection String**: Already optimized in the code

## Testing Connection

### Test Script

Run the test script to verify connection:

```bash
cd backend
python test_login_fix.py
```

### Manual Test

```python
from app.database_connection import connect_with_fallback
import asyncio

async def test():
    client, db_name, success = await connect_with_fallback(
        primary_uri="your-mongodb-uri",
        db_name="Resume_Screening"
    )
    if success:
        print(f"✅ Connected to {db_name}")
    else:
        print("❌ Connection failed")

asyncio.run(test())
```

## Monitoring

Watch the backend logs for connection status:

- ✅ `MongoDB connection established` - Success
- ⚠️ `DNS resolution failed` - DNS issue (will retry)
- ⚠️ `Primary connection failed, attempting fallback` - Using local MongoDB
- ❌ `All MongoDB connection attempts failed` - All connections failed

## Best Practices

1. **Development**: Use local MongoDB for faster, more reliable connections
2. **Production**: Use MongoDB Atlas with proper IP whitelisting
3. **Testing**: Set `MONGO_FALLBACK_URI` for test environments
4. **Monitoring**: Check logs regularly for connection issues

## Additional Resources

- [MongoDB Connection String Format](https://www.mongodb.com/docs/manual/reference/connection-string/)
- [MongoDB Atlas Network Access](https://www.mongodb.com/docs/atlas/security/ip-access-list/)
- [DNS Troubleshooting](https://www.cloudflare.com/learning/dns/what-is-dns/)




