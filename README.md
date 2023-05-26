# ScrutiniXAI
ScrutiniXAI is an AI Interview Assistant! This tool will help you assess your candidate during their job interview by generating potential interview questions based on your conversation with them and the job description.


#  Seting up the project
## 1. Clone the repository
```
git clone <REPOSITORY_URL>
```
## 2. Install the dependencies
 Backend:
```
cd scrutinixAi-be
pip install -r requirements.txt
```
Frontend:
```
cd scrutinixAi-fe
npm install
```


## 3. Run the project
Backend:
```
uvicorn main:app --reload
```

Frontend:
```
npm run dev
```

## 4. Open the project
Open the frontend project in your browser at http://localhost:3000/

Open the backend project in your browser at http://localhost:8000/


#  Project Structure
## Frontend
The frontend is built using [Next.js](https://nextjs.org/). The main pages are located in the `pages` folder. The `components` folder contains the components used in the pages. The `styles` folder contains the global styles and the styles for the components. The `public` folder contains the images and the favicon.

## Backend
The backend is built using [FastAPI](https://fastapi.tiangolo.com/). The `main.py` file contains the endpoints. The `models` folder contains the models used in the project. The `utils` folder contains the functions used in the project. The `data` folder contains the data used in the project. The `templates` folder contains the templates used in the project. The `static` folder contains the images used in the project.

