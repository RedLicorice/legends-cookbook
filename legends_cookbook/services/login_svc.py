from ..repositories.login_token import LoginTokenRepository
from ..repositories.user import UserRepository, UserCreate, UserModel
from ..schemas.login_token import LoginTokenCreate, LoginTokenUpdate, LoginTokenModel
from ..db import db_session, Session
from typing import Optional, List, Union
import logging
import json
import base64
from io import StringIO
from datetime import datetime, timedelta, UTC as UTC_TZ
from urllib.parse import quote_plus
from ..config import settings
from .utils import add_human_interval, generate_random_alphanumeric_string
import jwt

class LoginService:
    def __init__(self):
        self.repo = LoginTokenRepository()
        self.users_repo = UserRepository()

    #  Usato dal frontend (nicegui o fastapi), genera una stringa codificata in base64 che sarà passata al comando start del bot,
    #  permette se necessario di passare dati aggiuntivi.
    def generate_bot_login_payload(self, data):
        _tst = datetime.now(UTC_TZ).isoformat()
        _payload = dict(
            request_time=_tst
        )
        if data != None:
            _payload.update(data)
        _dump = json.dumps(_payload)
        _b64_dump = base64.b64encode(_dump.encode('utf-8'), b'-_')
        return _b64_dump.decode('utf-8')

    # Usato dal bot telegram, decodifica la stringa ed estrae le informazioni del payload
    def parse_bot_login_payload(self, payload: str):
        _dump = base64.b64decode(payload, b'-_', True)
        data = json.loads(_dump.decode('utf-8'))
        return data

    # Usato dal frontend, genera un link che invoca il comando "start" del bot, con un payload custom.
    # Il bot invierà all'utente un link con un token, che quando visitato garantirà il token jwt per l'accesso.
    def generate_bot_login_link(self, data: Optional[dict] = None):
        login_link = settings.telegram_bot.bot_link + '?start=' + self.generate_bot_login_payload(data)
        return login_link
    
    # Usato dal bot, genera un link che imposta il token jwt (e quindi autentica l'utente)
    def generate_jwt_token_link(self, telegram_user_id: str, name: Optional[str]):
        _dto = LoginTokenCreate(
            telegram_user_id=telegram_user_id,
            name=name
        )
        _tok = self.generate_login_token(_dto)
        return _tok
    
    # Usato internamente, genera un token che consente all'utente con cui sta chattando
    # di accedere. 
    def generate_login_token(self, dto: LoginTokenCreate):
        if not dto.telegram_user_id:
            raise ValueError(f"Invalid telegram_user_id for login token! {dto}")
        
        # Se il token è nullo o non è almeno di 64 caratteri lo rigenero
        if not dto.token or len(dto.token) != 64:
            dto.token = generate_random_alphanumeric_string(64)
        
        # Se non è impostata una scadenza, adotto quella di default
        #   creazione e modifica sono impostate dal db
        if not dto.expires:
            _tst = datetime.now(UTC_TZ)
            _exp = add_human_interval(_tst, settings.telegram_bot.login_token_lifetime)
            dto.expires = _exp
    
        with db_session() as db:
            # Se non esiste un utente corrispondente all'ID telegram, lo creo
            #   nel dto è incluso opzionalmente il nome utente da creare.
            existing_user = self.users_repo.get_by_telegram_user_id(db, dto.telegram_user_id)
            if not existing_user:
                new_user = UserCreate(
                    telegram_user_id=dto.telegram_user_id,
                    name=generate_random_alphanumeric_string(6) if not dto.name else dto.name
                )
                existing_user = self.users_repo.create(db, new_user)
            # Creo un login token. Mi sono già assicurato che l'utente esista.
            login_token = self.repo.create(db, dto)

        return login_token
    
    # Consuma un "login token"
    def consume_login_token(self, token: str):
        with db_session() as db:
            token = self.repo.get_by_token(db, token)
        
        if not token:
            raise Exception("Login token not found")
        
        if token.used:
            raise Exception("Login token found, but it has been already used")
        
        if not token.active:
            raise Exception("Login token found, but it is not active")
        

        user = self.users_repo.get_by_telegram_user_id(token.telegram_user_id)
        if not user:
            raise Exception("Login token found, but no corresponding user found")
        
        # Login is ok, generate a new jwt
        _tst = datetime.now(UTC_TZ)
        _exp = add_human_interval(_tst, settings.api.jwt_lifetime)
        _jwt_payload = {
            'token_id': token.id,
            'token': token.token,
            'user_id': user.id,
            'telegram_user_id': user.telegram_user_id,
            'user_name': user.name,
            'issued_at': _tst.isoformat(),
            'expires_at': _exp.isoformat()
        }

        # Issue a JWT Payload
        encoded_jwt = jwt.encode(_jwt_payload, settings.api.jwt_secret, algorithm="HS256")
        
        return encoded_jwt
