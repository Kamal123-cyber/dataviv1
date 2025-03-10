for this project to run 

1. clone this project using ssh or https
2. create a venv for this project
3. install dependencies of the project
4. run the project using uvicorn main:app --host 0.0.0.0 --port 8001 --reload
5. There are some api endpoints 
    1. for creating user or register 8001/auth/register POST
   2. for loging in user 8001/auth/login POST
   3. for getting user details 8000/auth/user-details GET