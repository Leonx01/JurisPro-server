import datetime
import time
from datetime import datetime
from pprint import pprint

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from repositories.chat_repository import ChatRepository
from repositories.function_repository import FunctionRepository
from repositories.message_repository import MessageRepository
from repositories.prompt_repository import PromptRepository
from repositories.section_repository import SectionRepository
from schemas.chat_schema import ChatCreate, ChatPage
from schemas.message_schema import MessagePage, UserMessageRaw, MessageCreate, MessageVO
from schemas.prompt_schema import PromptTemplate
from services.llm_service import LLMService
from utils.converters import Converter


class ChatService:
    @staticmethod
    def get_chat_page(db: Session, uid: int, keyword: str, page: int, page_size: int) -> ChatPage:
        """获取会话列表"""
        page = ChatRepository.get_chat_page(db, uid, keyword, page, page_size)
        return page

    @staticmethod
    def start_chat(db: Session, chat: ChatCreate, uid: int):
        """开始会话"""
        chat.uid = uid
        name = LLMService.generate_response_by_code(db, 'summary', chat.query)
        chat.name = Converter.clean_text(name)
        ChatRepository.add_chat(db, chat)

    @staticmethod
    def fetch_messages(db: Session, uid: int, uuid: str, offset: int, page_size: int = 10) -> MessagePage:
        return MessageRepository.fetch_messages(db, uid, uuid, offset, page_size)

    @staticmethod
    def delete_chat(db: Session, uuid: str, uid: int):
        """删除会话"""
        ChatRepository.delete_chat(db, uuid, uid)

    @staticmethod
    def add_message(es_client: Elasticsearch, db: Session, embedding_model: SentenceTransformer, uid: int,
                    msg: UserMessageRaw) -> MessageVO | None:
        user_msg = MessageCreate(
            chat_uuid=msg.chat_uuid,
            content=msg.query,
            type='human',
            created_at=datetime.now()
        )
        function = FunctionRepository.get_function_by_code(db, 'chat')
        if not function:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND)
        prompt = PromptRepository.get_prompt_by_id(db, function.prompt_id)
        if not prompt:
            raise AppException(ErrorCode.RESOURCE_NOT_FOUND)
        template = PromptTemplate(
            content=prompt.prompt,
            slots=function.slots
        )
        history = MessageRepository.retrieve_history(db, msg.chat_uuid, 4)
        laws = SectionRepository.retrieval_in_chat(es_client, embedding_model, msg.query, 3)
        slots_value = {
            "query": msg.query,
            "law": Converter.format_list(laws),
            "history": Converter.format_list(history),
        }
        start = time.time()
        model_msg_raw = LLMService.generate_with_prompt(db, msg.model_id, template, slots_value)
        end = time.time()
        time_cost = end - start
        pprint(model_msg_raw)
        usage = None
        if model_msg_raw.usage_metadata:
            usage = model_msg_raw.usage_metadata
        elif model_msg_raw.response_metadata['token_usage']:
            usage = model_msg_raw.response_metadata['token_usage']
        if not usage:
            raise AppException(ErrorCode.INVALID_DATAFORMAT)
        model_msg = MessageCreate(
            type='ai',
            content=model_msg_raw.content,
            chat_uuid=msg.chat_uuid,
            created_at=datetime.now(),
            response_time=time_cost,
            token_counts=usage['output_tokens']
        )
        user_msg.token_counts = usage['output_tokens']
        MessageRepository.add_message(db, uid, user_msg)
        resp = MessageRepository.add_message(db, uid, model_msg)
        MessageRepository.bind_related_sections(db, resp.id, laws)
        resp.related_laws = laws
        pprint(user_msg)
        pprint(model_msg)
        return resp
