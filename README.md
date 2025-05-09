# IdeaForge: Research Collaboration Platform

IdeaForge is a web application that enables users to collaborate on research projects and receive intelligent paper recommendations based on project descriptions. The platform helps connect researchers and collaborators with similar interests, fostering innovation and knowledge sharing.

![IdeaForge Logo](logo.png)

## 🚀 Features

- **User Authentication**: Secure sign-up, login, and profile management
- **Project Management**: Create, browse, and collaborate on research projects
- **Collaboration System**: Send and respond to collaboration requests
- **Research Paper Recommendations**: Get relevant paper recommendations based on project content
- **Real-time Search & Filtering**: Find projects matching specific criteria
- **Responsive Design**: Works seamlessly across devices

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based (JSON Web Tokens)
- **Recommendation Engine**: TF-IDF model with cosine similarity

### Frontend
- **Framework**: React with TypeScript
- **UI Components**: Shadcn UI and Tailwind CSS
- **State Management**: React Context API
- **Routing**: React Router
- **HTTP Client**: Axios

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+
- Git

## 🔧 Installation

### Clone the Repository

```bash
git clone <repository-url>
cd ideaforge
```

## 🛠️ Step 1: Database Setup

1. Install PostgreSQL if not already installed
   - Windows: Download from [PostgreSQL website](https://www.postgresql.org/download/windows/)
   - macOS: `brew install postgresql`
   - Linux: `sudo apt install postgresql`

2. Create a database for IdeaForge:
   ```sql
   CREATE DATABASE ideaforge;
   ```

3. Update database credentials in `backend/.env` file:
   ```
   DB_USER=your_postgres_username
   DB_PASSWORD=your_postgres_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=ideaforge
   ```

### Backend Setup

1. **Create a virtual environment and activate it**:

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:

Create a `.env` file in the `backend` directory with the following variables (or modify the existing one):

```
# Database configuration
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ideaforge

# JWT Authentication
JWT_SECRET=yoursecretkey
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api

# Recommendation model settings
RECOMMENDATION_MODEL_PATH=../initialrecomendmodel.py
MAX_RECOMMENDATIONS=5
```

4. **Initialize the database**:

```bash
# Create tables and initial data
python -m app.database.init_db --with-testdata
```

5. **Run the backend server**:

```bash
python run.py
```

The backend will be available at `http://localhost:8000`.

### Frontend Setup

1. **Install dependencies**:

```bash
# Navigate to frontend directory
cd ideaforge

# Install dependencies
npm install
```

2. **Set up environment variables**:

Create or modify the `.env` file in the `ideaforge` directory:

```
VITE_API_URL=http://localhost:8000/api
VITE_NODE_ENV=development
```

3. **Run the frontend development server**:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## 🚀 Running the Application

1. Start the PostgreSQL database service
2. Start the backend server: `python run.py` (from the `backend` directory)
3. Start the frontend development server: `npm run dev` (from the `ideaforge` directory)
4. Open your browser and navigate to `http://localhost:5173`

## 📦 Project Structure

```
ideaforge/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── database/     # Database configuration and models
│   │   ├── models/       # SQLAlchemy models
│   │   ├── routers/      # API route handlers
│   │   ├── schemas/      # Pydantic models for request/response
│   │   ├── services/     # Business logic and services
│   │   └── main.py       # Application entry point
│   ├── requirements.txt  # Python dependencies
│   └── run.py            # Script to run the backend
├── ideaforge/            # React frontend
│   ├── public/           # Static assets
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── contexts/     # React context providers
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── App.tsx       # Main application component
│   ├── package.json      # Node.js dependencies
│   └── vite.config.ts    # Vite configuration
└── initialrecomendmodel.py  # Recommendation model
```

## 📝 Usage

1. Register a new account or log in with existing credentials
2. Browse existing projects from the "Projects" page
3. Create a new project with the "Create Project" button
4. View project recommendations after creating a project
5. Send collaboration requests to join interesting projects
6. Accept or reject collaboration requests from your dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Shadcn UI](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

