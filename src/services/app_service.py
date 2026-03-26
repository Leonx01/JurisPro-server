from sqlalchemy.orm import Session

from src.repositories.menu_repository import MenuRepository


class AppService:
    @staticmethod
    def get_routes(db: Session):
        routes = MenuRepository.get_routes(db)
        return routes
