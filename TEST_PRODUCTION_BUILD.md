# 🧪 Test Production Build Locally

Before deploying, test the production build locally to ensure everything works.

---

## Backend Production Test

### 1. Install Gunicorn (if not already)
```bash
cd TestGenie
pip install gunicorn
```

### 2. Test with Gunicorn
```bash
# Start backend with Gunicorn (production server)
gunicorn app:app --bind 0.0.0.0:5000 --workers 1

# Should see:
# [INFO] Starting gunicorn 21.2.0
# [INFO] Listening at: http://0.0.0.0:5000
```

### 3. Test Health Endpoint
Open browser: `http://localhost:5000/api/health`

Should see:
```json
{
  "status": "healthy",
  "service": "TestGenie & EpicRoast with GroomRoom",
  "version": "1.0"
}
```

**✅ Backend production build works!**

---

## Frontend Production Test

### 1. Build Production Bundle
```bash
cd TestGenie/frontend
npm run build

# Should see:
# ✓ built in XXXms
# dist/index.html                X.XX kB
# dist/assets/index-XXXXX.js     XXX.XX kB
```

### 2. Preview Production Build
```bash
npm run preview

# Should see:
# Local:   http://localhost:4173/
# Network: http://xxx.xxx.xxx.xxx:4173/
```

### 3. Test in Browser
Open: `http://localhost:4173`

**Make sure backend is also running!**

Test features:
- ✅ GroomRoom analysis
- ✅ EpicRoast
- ✅ Figma integration

**✅ Frontend production build works!**

---

## Full Stack Production Test

### Terminal 1 (Backend):
```bash
cd TestGenie
gunicorn app:app --bind 0.0.0.0:5000
```

### Terminal 2 (Frontend):
```bash
cd TestGenie/frontend
npm run preview
```

### Browser:
Open: `http://localhost:4173`

**Test all features - should work exactly like development mode!**

---

## Clean Up

Stop both servers:
- Press `Ctrl+C` in each terminal

**Ready for deployment!** 🚀

