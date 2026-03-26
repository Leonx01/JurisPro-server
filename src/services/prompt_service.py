from typing import List

from sqlalchemy.orm import Session

from repositories.prompt_repository import PromptRepository
from schemas.prompt_schema import PromptCreate, PromptVO, PromptUpdate, PromptPage


class PromptService:
    @staticmethod
    def get_prompt_page(
            db: Session,
            keyword: str = None,
            fid: int = None,
            page: int = 1,
            page_size: int = 10
    ) -> PromptPage:
        """ 分页查询 Prompt """
        return PromptRepository.query_prompt_page(db, keyword, fid, page, page_size)

    @staticmethod
    def get_prompt_by_id(db: Session, pid: int) -> PromptVO:
        """ 根据 ID 获取 Prompt """
        prompt = PromptRepository.get_prompt_by_id(db, pid)
        return PromptVO.model_validate(prompt)

    @staticmethod
    def add_prompt(db: Session, prompt: PromptCreate):
        PromptRepository.add_prompt(db, prompt)

    @staticmethod
    def get_all_prompts(db: Session) -> List[PromptVO]:
        return PromptRepository.get_all_prompt(db)

    @staticmethod
    def get_prompts(db: Session, keyword: str, fid: int) -> List[PromptVO]:
        return PromptRepository.query_prompt(db, keyword, fid)

    @staticmethod
    def update_prompt(db: Session, prompt: PromptUpdate):
        PromptRepository.update_prompt(db, prompt)

    @staticmethod
    def delete_prompt(db: Session, pid: int):
        PromptRepository.delete_prompt(db, pid)
