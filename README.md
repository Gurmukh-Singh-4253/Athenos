# Athenos 🧠📚  
**An AI-powered adaptive learning platform** that personalizes content difficulty (Beginner, Intermediate, Advanced) based on learner performance — and dynamically rewrites educational content using Generative AI.  

---

## 🚀 Features

- 📊 **Smart Learner Profiling**  
  Classifies learners using a machine learning model that analyzes speed, accuracy, confidence, and consistency.

- 🤖 **AI-Powered Content Rewriting**  
  Utilizes the FLAN-T5 model to adjust content difficulty to each learner’s level.

- 🧪 **Synthetic Training Data**  
  Uses statistically controlled synthetic datasets for model training and evaluation.

- 🎨 **User-Friendly Web Interface**  
  Built with Flask and Streamlit for an intuitive experience.

- 🤖 **Telegram Bot Integration**  
  Enables learners to interact with Athenos via Telegram for instant learning content.

- 🔗 **GitHub-Integrated Architecture**  
  Easy to clone, run, and extend.

---

## 🧠 Tech Stack

- **Backend**: Flask (Web API), Streamlit (Interactive UI)  
- **ML & AI**: Scikit-learn (Learner Classification), HuggingFace Transformers (FLAN-T5)  
- **Data Processing**: Pandas, NumPy  
- **Database**: SQLite  
- **Bot Integration**: Python Telegram Bot API  

---

## 🔍 Folder Structure  

```
📁 Athenos
├── 📁 Flask                  # Backend API (Flask)
│   ├── 📁 __pycache__
│   ├── 📁 instance           # Database files
│   │   ├── aternos.db
│   │   ├── database.db
│   ├── 📁 static             # Frontend assets
│   │   ├── bootstrap.bundle.min.js
│   │   ├── bootstrap.min.css
│   │   ├── logo.jpg
│   │   ├── style.css
│   │   ├── styles.css
│   ├── 📁 templates          # HTML templates
│   ├── app.py                # Flask app
│   ├── check_db.py           # Database checker
│   ├── database.db           # SQLite database
│   ├── init_db.py            # DB initialization script
│   ├── schema.sql            # Database schema
│   ├── site.db               # Another database file
│
├── 📁 telegram-bot           # Telegram bot integration
│   ├── .gitignore
│   ├── telegram-bot.py
│
├── .gitignore                # Ignore unnecessary files
```

---

## 🛠 Installation  

```bash
git clone https://github.com/Gurmukh-Singh-4253/Athenos.git
cd Athenos/Flask
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate` 
pip install -r requirements.txt
```

---

## 💻 Usage  

### **1. Run the Flask Backend**  
Launch the main backend server to serve API endpoints:
```bash
cd Flask
flask run
```

### **2. Run the Streamlit Frontend**  
Open the interactive web UI to classify learners and rewrite content:
```bash
streamlit run app.py
```
Navigate to the localhost URL provided (typically `http://localhost:8501`).

### **3. Run the Telegram Bot**  
Start the bot to enable AI-powered interactions directly in Telegram.
Make sure you have your Telegram Bot Token configured in the script or using environment variables.
```bash
cd telegram-bot
python -m venv venv
pip install -r requirements.txt
python telegram-bot.py
```

### **4. Upload & Test**  
- Upload a `.csv` of learner performance or use sample data.
- View predicted learner level.
- Watch content adapt in real time based on performance.

---

## 🧩 Real-World Use Cases

- 🏫 **Schools & Universities**  
  Adapt coursework dynamically to individual student levels, ensuring no one is left behind or held back.

- 📚 **EdTech Platforms**  
  Integrate Athenos into digital learning apps to offer tailored lessons and adaptive assessments.

- 👩‍💻 **Self-paced Learning**  
  Independent learners can receive content tailored to their skill level via web or Telegram.

- 🧑‍🏫 **Tutoring Centers**  
  Provide real-time learner insights to tutors, and automatically serve customized practice content.

- 🗣️ **Language Learning Apps**  
  Adjust vocabulary and grammar complexity for beginners vs advanced speakers using the GenAI engine.

- 💼 **Corporate Training**  
  Deliver training modules adapted to employee experience levels, improving retention and engagement.

---

## 🤖 Telegram Bot Features  
- Automatically provides personalized learning content based on user queries.  
- Supports content adaptation for different skill levels (Beginner, Intermediate, Advanced).  
- Enables quick interactions and instant knowledge checks.  
- Uses AI-powered content rewriting for dynamic responses.  

---

## 📝 License  

MIT License — free to use, modify, and distribute with attribution.  

---



