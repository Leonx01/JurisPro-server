import logging
from datetime import datetime
from typing import List

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from models import Messages, Chat, MessageSection, Section
from schemas.message_schema import MessageVO, MessagePage, MessageCreate, ChatHistory
from schemas.section_schema import SectionRetrieval


class MessageRepository:

    @staticmethod
    def retrieve_history(db: Session, uuid: str, top_k=4) -> List[ChatHistory]:
        try:
            msgs = (
                db.query(Messages)
                .filter(Messages.chat_uuid == uuid)
                .order_by(desc(Messages.created_at))
                .limit(top_k)
                .all()
            )
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED)
        result = []
        for msg in reversed(msgs):
            history = ChatHistory(
                role=msg.type,
                content=msg.content
            )
            result.append(history)
        return result

    @staticmethod
    def fetch_messages(db: Session, uid: int, uuid: str, offset: int, page_size: int = 10) -> MessagePage:
        # Log the input for debugging purposes
        logging.debug(f"Fetching messages for user {uid} in chat {uuid} with offset {offset} and page_size {page_size}")

        # Fetch the chat from the database
        chat = db.query(Chat).filter(Chat.uuid == uuid, Chat.del_flag == 0).first()

        # Check if the chat exists
        if chat is None:
            logging.error(f"Chat with uuid {uuid} not found.")
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND, "Chat not found")

        # Check if the user is authorized to access this chat
        if chat.uid != uid:
            logging.error(f"User {uid} is not authorized to access chat {uuid}")
            raise AppException(ErrorCode.UNAUTHORIZED, "User not authorized to access this chat")

        # Fetch the messages for the chat
        msgs = (
            db.query(Messages)
            .filter(Messages.chat_uuid == uuid)
            .order_by(desc(Messages.created_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # If no messages are found, return an empty list
        if not msgs:
            logging.info(f"No messages found for chat {uuid} with offset {offset}.")

        # Return the messages as a MessagePage object
        messages = []
        for msg in msgs:
            if msg.type == "ai":
                # If the message is of type "AI", we need to fetch the related sections
                sections = MessageRepository.get_related_sections(db, msg.id)
                print(f"Related sections for message {msg.id}: {sections}")
                # Convert the sections to a list of SectionRetrieval objects
                msg = MessageVO.model_validate(msg)
                msg.related_laws = sections
                messages.append(msg)
            else:
                messages.append(MessageVO.model_validate(msg))
        return MessagePage(
            offset=offset + len(msgs),
            messages=messages,
        )

    @staticmethod
    def add_message(db: Session, uid: int, msg: MessageCreate) -> MessageVO:
        chat = db.query(Chat).filter(Chat.uuid == msg.chat_uuid).first()
        if not chat or chat.uid != uid:
            raise AppException(ErrorCode.UNAUTHORIZED)
        chat.updated_at = datetime.now()
        db_msg = Messages(
            content=msg.content,
            type=msg.type,
            mid=msg.model_id,
            chat_uuid=msg.chat_uuid,
            token_counts=msg.token_counts,
            response_time=msg.response_time,
            created_at=msg.created_at,
        )
        try:
            db.add(db_msg)
            db.flush()
            db.commit()
            db.refresh(db_msg)
            # Update the chat's updated_at field
            db.refresh(chat)
            return MessageVO.model_validate(db_msg)
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED)

    @staticmethod
    def bind_related_sections(db: Session, mid: int, sections: List[SectionRetrieval]) -> None:
        try:
            for section in sections:
                db_msg_section = MessageSection(
                    mid=mid,
                    sid=section.id
                )
                db.add(db_msg_section)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to bind sections: {str(e)}")

    @staticmethod
    def get_related_sections(db: Session, mid: int) -> List[SectionRetrieval]:
        try:
            sections = db.query(MessageSection).filter(MessageSection.mid == mid).all()
            if not sections:
                return []
            section_ids = [section.sid for section in sections]
            db_sections = db.query(Section).filter(Section.id.in_(section_ids)).all()
            if not db_sections:
                return []
            return [SectionRetrieval(
                id=section.id,
                law=section.law,
                no=section.no,
                content=section.content,
            ) for section in db_sections]
        except SQLAlchemyError as e:
            raise AppException(ErrorCode.DB_OPERATION_FAILED, f"Failed to retrieve sections: {str(e)}")
