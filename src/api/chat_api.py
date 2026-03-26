from fastapi import APIRouter, Query
from sentence_transformers import SentenceTransformer

from schemas.chat_schema import ChatCreate
from schemas.message_schema import UserMessageRaw
from services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Application"])

from src.utils.response import ResponseModel
from src.utils.dependencies import get_db, get_current_user, get_elastic, embed
from sqlalchemy.orm import Session
from fastapi import Depends


@router.post("")
def new_chat(chat: ChatCreate, db: Session = Depends(get_db), user=Depends(get_current_user),
             es_client=Depends(get_elastic), embedding_model: SentenceTransformer = Depends(embed)):
    ChatService.start_chat(db, chat, user['uid'])
    user_msg = UserMessageRaw(
        query=chat.query,
        chat_uuid=chat.uuid,
        model_id=chat.model_id,
    )
    ChatService.add_message(es_client, db, embedding_model, user['uid'], user_msg)
    return ResponseModel.success(message="Chat created successfully")


@router.get("/messages")
def fetch_message(db: Session = Depends(get_db), user=Depends(get_current_user), uuid: str = Query(None),
                  offset: int = Query(0), page_size: int = Query(10)):
    msgs = ChatService.fetch_messages(db, user['uid'], uuid, offset, page_size)
    return ResponseModel.success(msgs)


@router.post("/message")
def create_message(msg: UserMessageRaw, db: Session = Depends(get_db), user=Depends(get_current_user),
                   es_client=Depends(get_elastic), embedding_model: SentenceTransformer = Depends(embed), ):
    resp = ChatService.add_message(es_client, db, embedding_model, user['uid'], msg)
    return ResponseModel.success(resp)


@router.get("")
def get_chat_page(db: Session = Depends(get_db), user=Depends(get_current_user), keyword: str = Query(None),
                  page: int = Query(1), page_size: int = Query(10)):
    page = ChatService.get_chat_page(db, user['uid'], keyword, page, page_size)
    return ResponseModel.success(data=page)


@router.delete("")
def delete_chat(db: Session = Depends(get_db), user=Depends(get_current_user), uuid: str = Query(None)):
    ChatService.delete_chat(db, uuid, user['uid'])
    return ResponseModel.success(message="Chat deleted successfully")
