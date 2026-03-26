from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from models import Chat, Messages
from schemas.chat_schema import ChatCreate, ChatPage, ChatVO


class ChatRepository:
    @staticmethod
    def delete_chat(db: Session, uuid: str, uid: int):
        """删除会话"""
        db_chat = db.query(Chat).filter(Chat.uuid == uuid).first()
        if not db_chat:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, f"Chat[ID:{uuid}] Not Found")
        if db_chat.uid != uid:
            raise AppException(ErrorCode.UNAUTHORIZED, f"User[ID:{uid}] Not Authorized to delete this chat")
        db_chat.del_flag = 1
        try:
            db.commit()
            db.refresh(db_chat)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to delete Chat: {str(e)}") from e

    @staticmethod
    def add_chat(db: Session, session: ChatCreate):
        db_chat = Chat(
            uuid=session.uuid,
            uid=session.uid,
            name=session.name,
        )
        try:
            db.add(db_chat)
            db.commit()
            db.refresh(db_chat)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Insert Session Error: {str(e)}") from e

    @staticmethod
    def get_chat_page(db: Session, uid: int, keyword: str = None, page: int = 1, page_size: int = 5) -> ChatPage:
        try:
            query = db.query(Chat).filter(Chat.uid == uid, Chat.del_flag == 0)
            if keyword:
                query = query.filter(Chat.name.like(f"%{keyword}%"))
            total = query.count()  # 不需要排序
            chats = query.order_by(Chat.updated_at.desc()) \
                .offset((page - 1) * page_size) \
                .limit(page_size) \
                .all()

            chat_list = []
            for chat in chats:
                last_human_msg = db.query(Messages).filter(
                    Messages.chat_uuid == chat.uuid,
                    Messages.type == 'human'
                ).order_by(Messages.created_at.desc()).first()

                last_ai_msg = db.query(Messages).filter(
                    Messages.chat_uuid == chat.uuid,
                    Messages.type == 'ai'
                ).order_by(Messages.created_at.desc()).first()

                chat_vo = ChatVO(
                    id=chat.id,
                    uid=chat.uid,
                    uuid=chat.uuid,
                    name=chat.name,
                    updated_at=chat.updated_at,
                    last_human_msg=last_human_msg.content if last_human_msg else "",
                    last_ai_msg=last_ai_msg.content if last_ai_msg else "",

                )
                chat_list.append(chat_vo)
            return ChatPage(
                total=total,
                chats=chat_list
            )
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Database error: {str(e)}") from e
