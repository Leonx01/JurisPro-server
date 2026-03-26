from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, JSON, UniqueConstraint, Float
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func, text

Base = declarative_base()
metadata = Base.metadata


# ========== 用户表 ==========
class User(Base):
    __tablename__ = 'users'

    uid = Column(BIGINT, primary_key=True, autoincrement=True)

    # Necessary fields
    uname = Column(String(45), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(45), nullable=True)
    gender = Column(String(1), server_default='0')

    # Optional fields
    avatar = Column(String(128), nullable=False, server_default='/static/avatar/common.png')
    status = Column(String(1), nullable=False, server_default='1')
    del_flag = Column(String(1), nullable=False, server_default='0')

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')

    login_ip = Column(String(45), nullable=True)
    login_at = Column(TIMESTAMP, nullable=True)

    rid = Column(BIGINT, server_default=text("2"))


# ========== 角色表 ==========
class Role(Base):
    __tablename__ = 'roles'

    id = Column(BIGINT, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)

    status = Column(String(1), nullable=False, server_default='1')
    del_flag = Column(String(1), nullable=False, server_default='0')

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')


class RoleMenus(Base):
    __tablename__ = 'role_menus'
    rid = Column(BIGINT, primary_key=True)
    mid = Column(BIGINT, primary_key=True)


# ========== 菜单表 ==========
class Menu(Base):
    __tablename__ = 'menus'

    mid = Column(BIGINT, primary_key=True, autoincrement=True)
    parent_id = Column(BIGINT, nullable=True)
    name = Column(String(255), nullable=False)
    order_num = Column(Integer, nullable=False)
    path = Column(String(255), nullable=False)
    type = Column(String(1), nullable=False, server_default='M', comment='R:导航 M:目录 C:菜单 F:功能')
    component = Column(String(255), nullable=True)
    redirect = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    del_flag = Column(String(1), nullable=False, server_default='0')
    # meta
    icon = Column(String(255), nullable=True, server_default='octicon:question-16')
    menu = Column(String(1), nullable=False, server_default='1')
    breadcrumb = Column(String(1), nullable=False, server_default='1')
    active_menu = Column(String(255), nullable=True)
    # 权限标识 sys:user:list
    auth = Column(String(255), nullable=True)

    status = Column(String(1), nullable=False, server_default='1')

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')

    description = Column(Text)


class MessageSection(Base):
    __tablename__ = 'message_sections'

    sid = Column(BIGINT, primary_key=True, nullable=False)
    mid = Column(BIGINT, primary_key=True, nullable=False)


class DictType(Base):
    __tablename__ = 'dict_types'

    id = Column(BIGINT, primary_key=True, index=True)
    dict_type = Column(String(100), unique=True, nullable=False)
    # sys_user_sex
    dict_name = Column(String(100), nullable=False)
    # 用户性别
    description = Column(Text)

    status = Column(String(1), nullable=False, server_default='1')

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')


class DictData(Base):
    __tablename__ = 'dict_datas'

    id = Column(BIGINT, primary_key=True, index=True)
    dict_type = Column(String(100), nullable=False)
    dict_value = Column(String(100), nullable=False)
    dict_label = Column(String(100), nullable=False)

    description = Column(Text)

    is_default = Column(String(1), nullable=False, server_default='0')
    status = Column(String(1), nullable=False, server_default='1')

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')


class Task(Base):
    __tablename__ = "tasks"

    id = Column(BIGINT, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # Ensure uniqueness
    method = Column(String(100), nullable=False)
    params = Column(JSON, nullable=True)
    status = Column(String(1), nullable=False, server_default='1')
    cron_expr = Column(String(128), index=True)  # Specify length for VARCHAR
    description = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')


# class Case(Base):
#     __tablename__ = "cases"
#
#     id = Column(BIGINT, primary_key=True, index=True)
#
#     description = Column(Text)
#     status = Column(String(1), nullable=False, server_default='1')
#     created_at = Column(TIMESTAMP, server_default=func.now())
#     updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
#     created_by = Column(String(45), nullable=False, default='system')  # Ensure default value
#     updated_by = Column(String(45), nullable=False, default='system')  # Ensure default value
#

class GenerativeModel(Base):
    __tablename__ = "llms"

    id = Column(BIGINT, primary_key=True, index=True)
    label = Column(String(100), nullable=False, unique=True, comment="模型标识")
    name = Column(String(50), nullable=False, comment="模型参数名称")
    avatar = Column(String(512), nullable=False,
                    server_default='https://raw.githubusercontent.com/Leonx01/picx-images-hosting/master/model_avatar.8vn2n8jmqr.webp')
    type = Column(String(1), nullable=False, server_default='I', comment='I:inner local,E:external api')

    api_key = Column(String(512))
    base_url = Column(String(512))
    provider = Column(String(20), nullable=False)

    description = Column(Text)
    connection = Column(String(1), nullable=False, server_default='0', comment='0 for pending 1 for ok 2 for error')
    status = Column(String(1), nullable=False, server_default='1')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')
    is_deleted = Column(String(1), nullable=True, server_default='0', comment='0 for not deleted 1 for deleted')


class LLMFunction(Base):
    __tablename__ = "llm_functions"
    id = Column(BIGINT, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(100), nullable=False, unique=True)
    # description = Column(Text, nullable=True)
    status = Column(String(1), nullable=False, server_default='1')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')
    pid = Column(BIGINT, nullable=True, comment='父功能编号')
    need_prompt = Column(String(1), nullable=True, server_default='1', comment='是否需要提示词 0:不需要 1:需要')
    prompt_id = Column(BIGINT, nullable=True, comment='选择的提示词')
    slots = Column(JSON, nullable=True, comment='参数槽位列表')


class LLMFunctionBinding(Base):
    __tablename__ = "llm_function_bindings"
    __table_args__ = (
        UniqueConstraint('llm_id', 'function_id', name='uq_llm_func'),
    )
    id = Column(BIGINT, primary_key=True, index=True)
    llm_id = Column(BIGINT, nullable=False, comment='llm id')
    function_id = Column(BIGINT, nullable=False, comment='function id')
    # status = Column(String(1), nullable=False, server_default='1')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')


class Chat(Base):
    __tablename__ = "chats"
    id = Column(BIGINT, primary_key=True, index=True)
    uuid = Column(String(100), nullable=False, unique=True, comment="业务唯一标识")
    name = Column(String(100), nullable=False, comment="会话名称")
    uid = Column(BIGINT, nullable=False, comment="user id ")  # user id
    del_flag = Column(String(1), nullable=False, server_default='0')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Messages(Base):
    __tablename__ = "messages"

    id = Column(BIGINT, primary_key=True, index=True)
    # cid = Column(BIGINT, nullable=False, comment='chat id')
    chat_uuid = Column(String(100), nullable=False, comment="chat uuid")
    mid = Column(BIGINT, nullable=True, comment='generative model id')
    type = Column(String(8), nullable=False, comment='human,ai')
    status = Column(String(1), nullable=False, server_default='1')
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=True)
    token_counts = Column(Integer, nullable=False, server_default='0')
    response_time = Column(Float, nullable=True, server_default='0')


# class EmbeddingModel(Base):
#     __tablename__ = "embeddings"

# class PromptBluePrint(Base):
#     __tablename__ = "prompt_blueprints"
#
#     id = Column(BIGINT, primary_key=True, index=True)
#     name = Column(String(100), nullable=False, unique=True)
#     label = Column(String(50), nullable=False, index=True, comment="提示词类别")
#     description = Column(Text, nullable=True, comment="用途描述")
#     input_schema = Column(JSON, nullable=True, comment="输入参数定义（JSON格式）")
#     status = Column(String(1), nullable=False, server_default='1')
#     created_at = Column(TIMESTAMP, server_default=func.now())
#     updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
#     created_by = Column(String(45), nullable=True, server_default='system')
#     updated_by = Column(String(45), nullable=True, server_default='system')
#
#
class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(BIGINT, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    fid = Column(BIGINT, nullable=False, comment="功能编号")
    prompt = Column(Text, nullable=False, comment="提示词模板")
    description = Column(String(255), nullable=True, comment="提示词用途描述")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')


# class PromptFunction(Base):
#     __tablename__ = "prompt_functions"
#
#     id = Column(BIGINT, primary_key=True, index=True)
#     prompt_id = Column(BIGINT, nullable=False, comment="提示词编号")
#     function_id = Column(BIGINT, nullable=False, unique=True, comment="功能编号")
#

class Law(Base):
    __tablename__ = "laws"
    id = Column(BIGINT, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=False)
    version = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(1), nullable=False, server_default='1', comment="0 启用 1 废弃")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')


class Section(Base):
    __tablename__ = "sections"
    id = Column(BIGINT, primary_key=True, index=True)
    lid = Column(BIGINT, nullable=False, comment='法律条文编号')
    law = Column(String(100), nullable=False, comment='法律名称')
    no = Column(String(100), nullable=False, comment='章节编号')
    order_num = Column(Integer, nullable=False, comment='章节顺序')
    content = Column(Text, nullable=False, comment='章节内容')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')


class Document(Base):
    __tablename__ = "documents"
    id = Column(BIGINT, primary_key=True, index=True)
    tid = Column(BIGINT, nullable=True, comment='文书类型编号')
    uuid = Column(String(100), nullable=False, unique=True, comment='业务唯一标识')
    uid = Column(BIGINT, nullable=False, comment='用户编号')
    name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False, comment='章节内容')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')


class DocType(Base):
    __tablename__ = "doc_types"
    id = Column(BIGINT, primary_key=True, index=True)
    label = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True, default='', comment='文书类型描述')
    example = Column(Text, nullable=False, comment='文书示例')
    prompt = Column(Text, nullable=False, comment='交互提示')
    status = Column(String(1), nullable=False, server_default='1')
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(45), nullable=True, server_default='system')
    updated_by = Column(String(45), nullable=True, server_default='system')
    fid = Column(BIGINT, nullable=True, comment='生成功能编号')
