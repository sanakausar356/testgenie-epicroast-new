# 🧪 Deployment Testing Checklist

## Your Deployment URLs

**Backend (Railway):** https://web-production-8415f.up.railway.app
**Frontend (Vercel):** [Waiting for your Vercel URL]

---

## ✅ Test 1: Backend Health Check

### Test URL:
```
https://web-production-8415f.up.railway.app/api/health
```

### Expected Response:
```json
{
  "status": "healthy",
  "services": {
    "testgenie": true,
    "epicroast": true,
    "groomroom": true,
    "jira": true
  }
}
```

### Result:
- [ ] Backend returns "healthy" status
- [ ] All services show as `true`
- [ ] No errors in response

**Status:** ⏳ Testing now...

---

## ✅ Test 2: Vercel Deployment Status

### Check Vercel Dashboard:
1. Go to: https://vercel.com/dashboard
2. Find your project: `testgenie-epicroast-new`
3. Check deployment status

### Expected:
- [ ] Build completed successfully
- [ ] Deployment shows "Ready"
- [ ] No build errors

### Your Vercel URL:
```
https://testgenie-epicroast-new-[random-id].vercel.app
```

**Status:** ❓ What's your Vercel URL?

---

## ✅ Test 3: Frontend Loads

### Test:
Open your Vercel URL in browser

### Expected:
- [ ] Page loads without errors
- [ ] See three tabs: TestGenie, EpicRoast, GroomRoom
- [ ] UI is responsive
- [ ] No 404 or 500 errors

**Status:** ⏳ Pending Vercel URL

---

## ✅ Test 4: Backend Connectivity

### Test:
1. Open your Vercel URL
2. Press F12 (open Developer Tools)
3. Go to Console tab
4. Look for any errors

### Expected:
- [ ] No "Network Error" messages
- [ ] No CORS errors
- [ ] No "Failed to fetch" errors

**Status:** ⏳ Pending

---

## ✅ Test 5: GroomRoom Functionality

### Test Steps:
1. Open your Vercel URL
2. Click **"GroomRoom"** tab
3. Enter ticket ID: `ODCD-34544`
4. Select mode: **"Actionable"**
5. Click **"Analyze"**
6. Wait 5-10 seconds

### Expected Results:
- [ ] Loading indicator appears
- [ ] Analysis completes without errors
- [ ] Full report displays
- [ ] Markdown renders correctly
- [ ] No console errors

**Status:** ⏳ Pending

---

## ✅ Test 6: EpicRoast Functionality

### Test Steps:
1. Click **"EpicRoast"** tab
2. Paste ticket content or enter ticket ID
3. Select theme: **"Medium"**
4. Click **"Roast It!"**

### Expected Results:
- [ ] Loading indicator appears
- [ ] Roast generates successfully
- [ ] Content displays properly
- [ ] No errors

**Status:** ⏳ Pending

---

## ✅ Test 7: TestGenie Functionality

### Test Steps:
1. Click **"TestGenie"** tab
2. Paste acceptance criteria or enter ticket ID
3. Click **"Generate Test Scenarios"**

### Expected Results:
- [ ] Loading indicator appears
- [ ] Test scenarios generate
- [ ] Positive, negative, edge cases shown
- [ ] No errors

**Status:** ⏳ Pending

---

## ✅ Test 8: API Calls Verification

### Test:
1. Open Vercel URL
2. Press F12 → Network tab
3. Try analyzing a ticket in GroomRoom
4. Watch the network requests

### Expected:
- [ ] API call to: `https://web-production-8415f.up.railway.app/api/groomroom/generate`
- [ ] Status: 200 OK
- [ ] Response contains analysis data
- [ ] No 500, 404, or CORS errors

**Status:** ⏳ Pending

---

## ✅ Test 9: Jira Integration

### Test:
1. In GroomRoom, enter a real Jira ticket ID from your system
2. Click "Analyze"

### Expected:
- [ ] Ticket fetches from Jira
- [ ] Analysis includes Jira ticket data
- [ ] No authentication errors

**Status:** ⏳ Pending

---

## ✅ Test 10: Error Handling

### Test:
1. Enter invalid ticket ID: `INVALID-123`
2. Click Analyze

### Expected:
- [ ] Shows user-friendly error message
- [ ] Doesn't crash the app
- [ ] Console shows helpful error info

**Status:** ⏳ Pending

---

## 🐛 Troubleshooting Guide

### Issue: Backend Health Check Fails

**Symptoms:**
- Can't reach backend URL
- Timeout errors
- 503 Service Unavailable

**Solutions:**
1. Check Railway deployment status
2. Verify environment variables in Railway
3. Check Railway logs for errors
4. Verify Azure OpenAI credentials

---

### Issue: Frontend Can't Connect to Backend

**Symptoms:**
- "Network Error" in browser
- CORS errors in console
- "Failed to fetch" messages

**Solutions:**
1. Verify VITE_API_URL in Vercel settings:
   - Should be: `https://web-production-8415f.up.railway.app/api`
   - Must end with `/api`
2. Test backend health directly
3. Check for typos in URL
4. Redeploy Vercel after fixing env var

---

### Issue: API Returns 500 Error

**Symptoms:**
- Analysis starts but fails
- 500 Internal Server Error
- Backend logs show errors

**Solutions:**
1. Check Railway logs for specific error
2. Verify Azure OpenAI credentials are correct
3. Check Azure OpenAI quota/rate limits
4. Verify Jira credentials if using Jira

---

### Issue: Build Failed on Vercel

**Symptoms:**
- Deployment shows "Failed"
- Build errors in logs

**Solutions:**
1. Verify Root Directory is set to `frontend`
2. Check Node.js version is 18.x+
3. Review build logs for specific errors
4. Check for TypeScript errors

---

## 📊 Test Results Summary

| Test | Status | Notes |
|------|--------|-------|
| Backend Health | ⏳ | Testing... |
| Vercel Deployed | ❓ | Need URL |
| Frontend Loads | ⏳ | Pending |
| Backend Connection | ⏳ | Pending |
| GroomRoom Works | ⏳ | Pending |
| EpicRoast Works | ⏳ | Pending |
| TestGenie Works | ⏳ | Pending |
| API Calls | ⏳ | Pending |
| Jira Integration | ⏳ | Pending |
| Error Handling | ⏳ | Pending |

---

## 🎯 What To Report

After testing, tell me:

1. ✅ **Did backend health check pass?**
   - What did you see at: https://web-production-8415f.up.railway.app/api/health

2. ✅ **What's your Vercel URL?**
   - Should look like: https://testgenie-epicroast-new-xxx.vercel.app

3. ✅ **Did Vercel deployment succeed?**
   - Check Vercel dashboard

4. ✅ **Can you open your Vercel URL?**
   - Does it load?

5. ✅ **Any errors in browser console?**
   - Press F12 and check

6. ✅ **Can you analyze a ticket?**
   - Try ODCD-34544 in GroomRoom

---

## ✅ Success Criteria

All deployments are successful when:

- ✅ Backend health returns "healthy"
- ✅ Frontend loads without errors
- ✅ All three tabs are visible
- ✅ Can analyze Jira tickets
- ✅ No console errors
- ✅ API calls return 200 status
- ✅ Analysis results display correctly

---

**Railway Backend:** https://web-production-8415f.up.railway.app
**Health Endpoint:** https://web-production-8415f.up.railway.app/api/health

**Next:** Share your Vercel URL and test results!

