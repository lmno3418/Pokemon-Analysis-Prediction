---
title: PokéDex
emoji: 👾
colorFrom: purple
colorTo: cyan
sdk: docker
app_port: 7860
pinned: false
---

# 🎮 PokéDex - Interactive Pokémon Analytics & Battle Simulator

A comprehensive Pokémon web application with user authentication, interactive dashboard analytics, and AI-powered battle prediction using Machine Learning, backed by MongoDB Atlas.

## 🚀 Features

### 🔐 Authentication & Users
- ✅ User registration with email & username validation
- ✅ Secure login (email OR username)
- ✅ Password hashing with werkzeug
- ✅ MongoDB integration for persistent storage
- ✅ Unique email & username constraints

### 📊 Interactive Dashboard
- ✅ **11 Advanced Visualizations**:
  - Attack vs Defense scatter plot (bubble size = HP)
  - Top N Pokémon rankings by Attack
  - Box plots by Type (shows outliers)
  - Violin plots for distribution analysis
  - Type distribution bar charts
  - Stats trend area charts (by Generation)
  - Correlation heatmap (all stats relationships)
  - PCA clustering with K-means analysis
  - Multi-stat distribution histograms
  - Interactive data table (50 rows)

- ✅ **Real-time Filtering**:
  - Filter by Type 1 (18 types)
  - Filter by Generation (1-9)
  - Legendary/Non-Legendary toggle
  - Adjustable Top N (5-25)
  - All charts update instantly

### 🎮 Pokémon Pokedex
- ✅ Browse 697 Pokémon
- ✅ Advanced search & filtering
- ✅ Animated sprites & images
- ✅ Complete stats display
- ✅ Type information

### ⚔️ Battle System
- ✅ AI-powered battle predictions
- ✅ Random Forest classifier (ML model)
- ✅ Win probability estimation
- ✅ Head-to-head Pokémon battles
- ✅ Model trained on stat differences

---

## 📸 Project Screenshots

### Battle System & Prediction
![PokéDex Dashboard](https://github.com/lmno3418/Pokemon-Analysis-Prediction/blob/main/static/imgs/ss01.png?raw=true)
*ML-powered battle prediction with win probability estimation*

### Pokémon Browser
![Pokémon Browser](https://github.com/lmno3418/Pokemon-Analysis-Prediction/blob/main/static/imgs/ss02.png?raw=true)
*Browse and search 697 Pokémon with detailed stats and information*

### Dashboard Analytics
![Battle Prediction](https://github.com/lmno3418/Pokemon-Analysis-Prediction/blob/main/static/imgs/ss03.png?raw=true)
*Interactive dashboard with 11 advanced visualizations and real-time filtering*

---

## 🛠️ Tech Stack

- **Backend**: Flask 3.1.1 + Gunicorn
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: MongoDB Atlas (free tier compatible)
- **Authentication**: Flask-Login + werkzeug
- **Dashboard**: Dash 2.14.2 + Plotly
- **Data Science**: Pandas, NumPy, Scikit-learn
- **Deployment**: Docker + Gunicorn

---

## 📋 Deployment Guide

### 🤗 Deploy to Hugging Face Spaces (Recommended)

### Step 1: Prepare Your Environment

Get your MongoDB Atlas connection string:
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster (free tier available)
3. Create a database user
4. Copy the connection string

### Step 2: Create HF Spaces Secret

In your Hugging Face Spaces repository, add this secret in **Settings → Repository secrets**:

```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### Step 3: Deploy

1. Create a new Space on [huggingface.co/spaces](https://huggingface.co/spaces)
2. Select **Docker** as the SDK
3. Push this repository to your HF Space
4. The app will automatically deploy!

---
#### Step 1: Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free account & cluster
3. Create database user with password
4. Get connection string (copy it!)

#### Step 2: Create HF Space
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `pokedex`
   - **License**: MIT
   - **Space SDK**: Docker
4. Click **"Create Space"**

#### Step 3: Clone & Push Code
```bash
# Clone your HF Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/pokedex
cd pokedex

# Copy all files from this repo
cp /path/to/PokeDex/* .

# Push to HF
git add .
git commit -m "Deploy PokéDex"
git push
```

#### Step 4: Add MongoDB Secret
1. In your Space, go to **Settings** ⚙️
2. Click **"Repository secrets"**
3. Add new secret:
   - **Name**: `MONGO_URI`
   - **Value**: `mongodb+srv://username:password@cluster...`
4. Save

#### Step 5: Wait & Launch
- HF builds automatically (5-10 minutes)
- Watch status: **Building** → **Running** ✅
- App opens at: `https://huggingface.co/spaces/YOUR_USERNAME/pokedex`

---

## 💻 Local Development

### Prerequisites
- Python 3.11+
- MongoDB Atlas account (free)
- Git

### Quick Start

```bash
# 1. Clone repo
git clone <repo-url>
cd PokeDex

# 2. Virtual environment
python3 -m venv myvenv
source myvenv/bin/activate

# 3. Install packages
pip install -r requirements.txt

# 4. Create .env file
cat > .env << EOF
mongo_uri=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
SECRET_KEY=your-super-secret-key-here
EOF

# 5. Run app
python3 app.py

# 6. Visit http://127.0.0.1:7860
```

---

## 🐳 Docker (Local Testing)

```bash
# Build image
docker build -t pokedex .

# Run container
docker run -p 7860:7860 --env-file .env pokedex

# Visit http://localhost:7860
```

---

## 📊 API Endpoints

| Endpoint | Method | Protected | Description |
|----------|--------|-----------|-------------|
| `/` | GET | No | Home page |
| `/register` | GET/POST | No | User registration |
| `/login` | GET/POST | No | User login |
| `/logout` | GET | Yes | Logout user |
| `/pokedex` | GET | Yes | Pokémon browser |
| `/dashboard/` | GET | Yes | Analytics dashboard |
| `/api/pokemon` | GET | Yes | Search Pokémon (filtered) |
| `/api/pokemon/<id>` | GET | Yes | Get Pokémon by ID |
| `/api/battle` | POST | Yes | Battle prediction |

---

## 🔑 Key Features Explained

### Dashboard Analytics
- **11 interactive charts** with Plotly
- **Real-time filtering** updates all visualizations
- **Responsive grid layout** adapts to screen size
- **Modern UI** with gradients and shadows
- **PCA clustering** shows Pokémon stat patterns

### Battle System
- Uses **Random Forest classifier** ML model
- Trained on 697 Pokémon stat differences
- Predicts winner based on:
  - Type matchups
  - HP, Attack, Defense, Speed
  - Height, Weight, Experience
  - Generation & Legendary status
- Returns win probability percentage

### Authentication
- **Dual login** (email OR username)
- **Password hashing** for security
- **Session persistence** with Flask-Login
- **Unique constraints** on email & username

---

## 🧹 Maintenance

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Retrain ML Model (if needed)
```bash
python3 retrain_model.py
```

### Clear Cache
```bash
rm -rf __pycache__ myvenv/lib/python3.14/site-packages/__pycache__
```

---

## 📖 Database Schema

### MongoDB Collections

**users**
```json
{
  "_id": ObjectId,
  "username": "unique_username",
  "email": "user@example.com",
  "password": "hashed_password"
}
```

---

## 🎯 Roadmap

- [ ] Pokémon favoriting system
- [ ] User profiles & statistics
- [ ] Multiplayer battles
- [ ] Pokédex completion tracker
- [ ] Advanced filtering with ranges
- [ ] Export battle history as CSV
- [ ] Dark mode toggle

---

## 📝 License

MIT License - Free to use and modify

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

## ❓ Troubleshooting

### App won't start
- Check MongoDB connection string
- Verify `.env` file exists
- Check Python version (need 3.11+)

### Battle system not working
- Ensure scikit-learn is installed: `pip install scikit-learn`
- Check ML model file exists at `static/data/pokemon_RandomForest_model.pkl`

### HF Spaces won't deploy
- Check logs in Space settings
- Verify MONGO_URI secret is added
- Ensure Dockerfile is valid

---

**Created with ❤️ for Pokémon fans**
- [ ] Repository pushed to HF Space
- [ ] `MONGO_URI` secret added to HF Space
- [ ] Deployment triggered

---

## 🧪 Testing

### Local Testing
```bash
# Register a new account
# Login with credentials
# Browse Pokémon
# Test battle prediction
# Verify data in MongoDB Atlas
```

### Production Testing (HF Spaces)
Same steps after deployment to HF Spaces

---

## 📊 Technologies

- **Backend**: Python Flask with Gunicorn
- **Database**: MongoDB Atlas
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Flask-Login
- **Machine Learning**: Scikit-learn Random Forest
- **Deployment**: Docker, Hugging Face Spaces

---

## 🐛 Troubleshooting

### MongoDB Connection Error
Check `mongo_uri` in HF Spaces secrets or `.env` file
Verify IP whitelist on MongoDB Atlas
Ensure cluster is running

### Build Fails
Check Docker build logs
Verify all dependencies in `requirements.txt`
Ensure `.dockerignore` excludes unnecessary files

### 404 Errors on Static Files
Verify `static/` folder structure
Check file paths in HTML templates

---

## 🔗 Useful Links

- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [Hugging Face Spaces](https://huggingface.co/spaces)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)

---

## 📝 License

This project is for educational purposes only.

---

**Optimized for Hugging Face Spaces Deployment**  
Last Updated: December 30, 2025
