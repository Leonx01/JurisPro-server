from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from schemas.document_schema import DocTypeCreate, DocTypeUpdate, DocumentCreate, DocumentUpdate
from services.document_service import DocumentService
from src.utils.dependencies import get_db, get_current_user
from utils.response import ResponseModel

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/types/user")
async def get_user_doc_type(db=Depends(get_db)):
    types = DocumentService.get_user_doc_types(db)
    return ResponseModel.success(data=types)


@router.get("/types")
async def get_doc_types(db: Session = Depends(get_db), keyword: str = Query(None), status: str = Query(None)):
    types = DocumentService.get_doc_types(db, keyword, status)
    return ResponseModel.success(data=types)


@router.post("/type")
async def add_doc_type(doc: DocTypeCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc.created_by = user['uname']
    doc.updated_by = user['uname']
    DocumentService.add_doc_type(db, doc)
    return ResponseModel.success()


@router.put("/type")
async def update_doc_type(doc: DocTypeUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc.updated_by = user['uname']
    DocumentService.update_doc_type(db, doc)
    return ResponseModel.success()


@router.delete("/type")
async def delete_doc_type(id: int, db: Session = Depends(get_db)):
    DocumentService.delete_doc_type(db, id)
    return ResponseModel.success()


@router.post("")
async def add_doc(doc: DocumentCreate, db=Depends(get_db), user=Depends(get_current_user)):
    # response = LLMService.llm_invoke(request.query, request.model_id, db)
    # create doc
    # generate content
    doc.updated_by = user['uname']
    doc.created_by = user['uname']
    DocumentService.add_doc(db, doc)
    return ResponseModel.success()


@router.get("/preview")
async def get_doc(uuid: str, db: Session = Depends(get_db)):
    doc = DocumentService.get_document_by_uuid(db, uuid)
    return ResponseModel.success(data=doc)


@router.get("/user")
async def get_user_docs(page: int, page_size: int, keyword: str = Query(None), tid: int = Query(None),
                        db: Session = Depends(get_db),
                        user=Depends(get_current_user)):
    docs = DocumentService.get_user_doc(db, user['uname'], keyword, tid, page, page_size)
    return ResponseModel.success(data=docs)


@router.delete("")
async def delete_doc(id: int, db: Session = Depends(get_db)):
    DocumentService.delete_document(db, id)
    return ResponseModel.success()


@router.put("")
async def update_doc(doc: DocumentUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc.update_by = user["uname"]
    DocumentService.update_document(db, doc)
    return ResponseModel.success()
