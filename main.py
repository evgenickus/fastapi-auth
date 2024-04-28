from fastapi import Depends, FastAPI, Query, HTTPException, Security, status
from models import User, UserBase, SalarySheet, UserLogin, SalarySheetBase
from sqlmodel import Session, select
from typing import Annotated, Union
from db import get_session
from datetime import date
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
import uvicorn


app = FastAPI()


access_security = JwtAccessBearer(secret_key='very_long_secret_key')

async def get_current_user(
  credentials: JwtAuthorizationCredentials = Security(access_security)
):
  return credentials['username']

async def login_required(
    user: UserLogin = Depends(get_current_user)
) -> UserLogin:
  if user is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail='Not authenticated',
      headers={"WWW-Authenticate": "Bearer"}
    )
  return user

@app.post('/login')
async def loqin_user(
  user: UserLogin,
  session: Session = Depends(get_session)
) -> str:
  users_list = session.exec(select(User)).all()

  if not [u for u in users_list if u.username == user.username and u.password == user.password]:
    raise HTTPException(status_code=409, detail='username or password is incorrect')

  return access_security.create_access_token(subject=user.model_dump())
  # user_id = [u for u in users_list if u.username == user.username][0].id
  # # id = user_id[0].id
  # # user_id = session.exec(select(User).where(User.username == user.username))
  # amount = session.exec(select(SalarySheet.amount).where(SalarySheet.user_id == user_id))
  # update_date = session.exec(select(SalarySheet.update_date).where(SalarySheet.user_id == user_id))

  # return {
  #   "зарплата после повешения": amount, 
  #   "дата повешения": update_date, 
  #   }


  # return user_id





@app.post('/login')
async def login(
  token: str = Depends(loqin_user)
) -> str:
  return token


@app.get('/salary')
async def get_user_salary(
  # user_id: int,
  user: str  = Depends(login_required),
  session: Session = Depends(get_session)
) -> dict:
  
  # user = get_current_user()
  users_list = session.exec(select(User)).all()
  user_id = [u for u in users_list if u.username == user][0].id

  # user_id = session.exec(select(User).where(User.username == user))


  amount = session.exec(select(SalarySheet.amount).where(SalarySheet.user_id == user_id))

  if amount == []:
    raise HTTPException(status_code=409, detail='User not found')
  
  update_date = session.exec(select(SalarySheet.update_date).where(SalarySheet.user_id == user_id))

  return {
    "сотрудник": user,
    "зарплата после повышения": amount, 
    "дата повышения": update_date, 
    }


@app.post('/salary')
async def add_salary_item(
  row_data: SalarySheetBase,
  session: Session = Depends(get_session)
) -> SalarySheet:
  
  add_row = SalarySheet(user_id=row_data.user_id, amount=row_data.amount, update_date=row_data.update_date)

  session.add(add_row)
  session.commit()
  session.refresh(add_row)
  return add_row   

@app.post('/users')
async def create_new_user(
  user_data: UserBase,
  session: Session = Depends(get_session)
  ) -> User:

  users_list = session.exec(select(User)).all()
  
  new_user = User(username=user_data.username, email=user_data.email, password=user_data.password)

  if [u for u in users_list if u.username == user_data.username]:
    raise HTTPException(status_code=409, detail='User already exists')
  
  session.add(new_user)
  session.commit()
  session.refresh(new_user)

  return new_user


@app.get('/users')
async def get_user(
  username: Annotated[str | None, Query(max_length=10)] = None,
  email: str | None = None,
  session: Session = Depends(get_session)
 ) -> list[User]:
 
  users_list = session.exec(select(User)).all()
  if username:
    users_list = [
      b for b in users_list if username in b.username.lower()
    ]
  if email:
    users_list = [
      b for b in users_list if email == b.email.lower()
    ]
  return users_list

# @app.get('/salary')
# async def get_user_salary(
#   user_id: int | None,
#   session: Session = Depends(get_session)
# ) -> dict:

#   amount = session.exec(select(SalarySheet.amount).where(SalarySheet.user_id == user_id))

#   if amount == []:
#     raise HTTPException(status_code=409, detail='User not found')
  
#   update_date = session.exec(select(SalarySheet.update_date).where(SalarySheet.user_id == user_id))

#   return {
#     "зарплата после повешения": amount, 
#     "дата повешения": update_date, 
#     }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


#alembic init migrations
#alembic revision --autogenerate -m "initial migration"
#alembic upgrade head