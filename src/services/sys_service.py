import os
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from exceptions.error_codes import ErrorCode
from exceptions.exception import AppException
from src.repositories.menu_repository import MenuRepository
from src.schemas.upload_schema import UploadResponse


class SysService:
    BASE_UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"

    @staticmethod
    def get_menus(db: Session):
        menus = MenuRepository.get_menus(db)
        return menus

    @staticmethod
    async def save_file(file: UploadFile, target_dir: str) -> UploadResponse:
        # 拼接目标目录路径
        target_dir_path = os.path.join(SysService.BASE_UPLOAD_DIR, target_dir)

        # 确保目标目录存在
        os.makedirs(target_dir_path, exist_ok=True)

        try:
            # 获取文件扩展名
            file_ext = os.path.splitext(file.filename)[1]

            # 生成一个唯一的文件名
            file_name = f"{uuid4().hex}{file_ext}"

            # 拼接完整文件路径
            file_path = os.path.join(target_dir_path, file_name)

            # 异步保存文件
            with open(file_path, "wb") as buffer:
                while chunk := await file.read(1024):  # 每次读取 1KB
                    buffer.write(chunk)

            # 生成文件的公开访问 URL
            file_url = f"/static/{target_dir}/{file_name}"

            return UploadResponse(url=file_url)

        except Exception as e:
            # 处理上传过程中的错误并返回自定义错误
            raise AppException(ErrorCode.FILE_UPLOAD_FAIL, f"File upload failed: {str(e)}") from e
