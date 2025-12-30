# 🚀 HuggingFace Spaces Deployment Guide

Complete step-by-step guide to deploy PokéDex on Hugging Face Spaces.

---

## 📋 Pre-Deployment Checklist

Before you start, ensure you have:

- [ ] GitHub account (for pushing code)
- [ ] Hugging Face account (free at huggingface.co)
- [ ] MongoDB Atlas account (free tier works)
- [ ] MongoDB database user credentials
- [ ] MongoDB connection string copied

---

## Step 1️⃣: Setup MongoDB Atlas

### 1.1 Create MongoDB Cluster
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up or login
3. Create a free M0 cluster
4. Wait for cluster to be ready (~5 minutes)

### 1.2 Create Database User
1. In MongoDB Atlas, go to **Database Access**
2. Click **"+ Add New Database User"**
3. Enter username and generate a strong password
4. Save the password somewhere safe
5. Click **"Add User"**

### 1.3 Get Connection String
1. Go to **Database** → **Connect**
2. Click **"Drivers"**
3. Select **Python** and version **3.11+**
4. Copy the connection string
5. Replace `<password>` and `<dbname>`

**Format:**
```
mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

---

## Step 2️⃣: Create Hugging Face Space

### 2.1 Create New Space
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in details:
   - **Space name**: `pokedex` (or your choice)
   - **License**: MIT
   - **Space SDK**: Docker ✅
   - **Visibility**: Public (recommended)

### 2.2 Wait for Creation
- HF creates the repository
- You'll get a Git URL like: `https://huggingface.co/spaces/YOUR_USERNAME/pokedex`

---

## Step 3️⃣: Setup Local Git & Push Code

### 3.1 Clone Your HF Space
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/pokedex
cd pokedex
```

### 3.2 Copy PokéDex Files
Copy these files from your local PokéDex to the cloned space:

```bash
# Copy all essential files
cp ~/path/to/local/PokeDex/app.py .
cp ~/path/to/local/PokeDex/dashboard.py .
cp ~/path/to/local/PokeDex/requirements.txt .
cp ~/path/to/local/PokeDex/Dockerfile .
cp ~/path/to/local/PokeDex/.dockerignore .
cp ~/path/to/local/PokeDex/.env.example .

# Copy directories
cp -r ~/path/to/local/PokeDex/static .
cp -r ~/path/to/local/PokeDex/templates .
```

**Your space should now contain:**
```
pokedex/
├── .git/
├── .gitattributes
├── app.py                    ✅
├── dashboard.py              ✅
├── requirements.txt          ✅
├── Dockerfile                ✅
├── .dockerignore             ✅
├── .env.example              ✅
├── README.md (from HF, keep it)
├── static/                   ✅
│   ├── css/
│   ├── js/
│   └── data/
└── templates/                ✅
    └── *.html files
```

### 3.3 Update README
Replace the HF-generated README with our comprehensive one, or merge both.

### 3.4 Commit & Push
```bash
cd pokedex

# Add all files
git add .

# Commit
git commit -m "Deploy PokéDex - Interactive Pokemon Analytics Dashboard"

# Push to HF
git push
```

---

## Step 4️⃣: Add MongoDB Secret

### 4.1 Navigate to Space Settings
1. Go to your Space: `huggingface.co/spaces/YOUR_USERNAME/pokedex`
2. Click the **⚙️ Settings** button (top right)

### 4.2 Add Repository Secret
1. In Settings, find **"Repository secrets"** section
2. Click **"Add new secret"**
3. Fill in:
   - **Name**: `MONGO_URI`
   - **Value**: Paste your MongoDB connection string
   ```
   mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```
4. Click **"Add secret"**

**Important**: The secret is automatically provided to the Docker container as an environment variable.

---

## Step 5️⃣: Deploy & Launch

### 5.1 Automatic Deployment
Once you push to HF, deployment starts automatically:

1. HF reads your Dockerfile
2. Builds Docker image (~3-5 minutes)
3. Starts container on port 7860
4. App becomes live

### 5.2 Monitor Deployment
1. Go to your Space page
2. Watch the **"Building"** → **"Running"** status
3. Check **"Logs"** if it fails (Settings → Logs)

### 5.3 Access Your App
Once **"Running"**, your app is live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/pokedex
```

Or the direct link HF provides on the space page.

---

## ✅ Verify Deployment

### Test the App
1. **Home page loads** - Visit the URL
2. **Register new user** - Create an account
3. **Login** - Use email or username to login
4. **View Pokémon** - Browse the Pokédex
5. **View Dashboard** - Check analytics
6. **Battle Pokémon** - Test the ML model

### Check Logs
If something fails:
1. Go to Space Settings
2. Click **"Logs"**
3. Look for error messages
4. Common issues:
   - `MONGO_URI` not set → Add secret again
   - Port mismatch → Check Dockerfile (should be 7860)
   - Missing packages → Check requirements.txt

---

## 🔄 Update Your App

### Push Updates
```bash
# Make changes locally, then:
cd pokedex
git add .
git commit -m "Update message"
git push
```

HF automatically rebuilds & redeploys!

---

## 🛠️ Troubleshooting

### App won't start
**Error**: "Connection refused" or "Cannot connect to MongoDB"
- **Fix**: Check MONGO_URI secret is added correctly
- **Verify**: MongoDB cluster is active & accessible

### Dashboard not loading
**Error**: "Graph error" or blank dashboard
- **Fix**: Check scikit-learn is in requirements.txt
- **Verify**: ML model file exists in static/data/

### Authentication fails
**Error**: "Login unsuccessful" or "Registration failed"
- **Fix**: Ensure MongoDB user credentials are correct
- **Check**: Database exists in MongoDB Atlas

### Port error
**Error**: "Port 5000 already in use"
- **Fix**: Dockerfile must expose port 7860, not 5000
- **Verify**: `EXPOSE 7860` is in Dockerfile

### Rebuild manually
If stuck in "Building" state:
1. Go to Space Settings
2. Click **"Restart space"**
3. Wait for rebuild

---

## 📊 Production Checklist

- [ ] MongoDB Atlas cluster is active
- [ ] Database user has correct password
- [ ] MONGO_URI secret is added to Space
- [ ] All files pushed to HF repository
- [ ] Dockerfile uses port 7860
- [ ] requirements.txt includes all packages
- [ ] .env file is NOT in git (use .env.example)
- [ ] README.md has deployment instructions
- [ ] App loads at HF Spaces URL
- [ ] Can register & login successfully
- [ ] Can view Pokédex
- [ ] Dashboard displays charts
- [ ] Battle prediction works

---

## 🎉 Success!

Your PokéDex is now live on Hugging Face Spaces! 

**Next steps:**
- Share the URL with friends
- Monitor app performance
- Collect user feedback
- Add more features

---

## 📚 Useful Links

- [HF Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Docker Docs](https://docs.docker.com/)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
- [Flask Docs](https://flask.palletsprojects.com/)

---

**Questions?** Check the main README.md or visit the Hugging Face forums.
