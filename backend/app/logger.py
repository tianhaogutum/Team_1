"""
统一日志配置模块

为整个应用提供结构化的日志系统，支持：
- 不同日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 文件和控制台输出
- 结构化日志格式
- 请求追踪
- 性能监控

使用方式：
    from app.logger import get_logger
    
    logger = get_logger(__name__)
    logger.debug("调试信息")
    logger.info("一般信息")
    logger.warning("警告信息")
    logger.error("错误信息", exc_info=True)
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime

from app.settings import get_settings


# 日志格式
DETAILED_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
)
SIMPLE_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"

# 日志文件路径
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件
APP_LOG_FILE = LOG_DIR / "app.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"
DEBUG_LOG_FILE = LOG_DIR / "debug.log"


def setup_logging(
    log_level: str = "INFO",
    enable_file_logging: bool = True,
    enable_console_logging: bool = True,
    detailed_format: bool = True
) -> None:
    """
    配置应用的日志系统。
    
    Parameters
    ----------
    log_level : str
        日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
    enable_file_logging : bool
        是否启用文件日志
    enable_console_logging : bool
        是否启用控制台日志
    detailed_format : bool
        是否使用详细格式（包含函数名和行号）
    """
    # 转换日志级别
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 选择格式
    log_format = DETAILED_FORMAT if detailed_format else SIMPLE_FORMAT
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_formatter = logging.Formatter(log_format, date_format)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # 文件处理器
    if enable_file_logging:
        # 应用日志（所有级别）
        app_handler = RotatingFileHandler(
            APP_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        app_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
        app_formatter = logging.Formatter(log_format, date_format)
        app_handler.setFormatter(app_formatter)
        root_logger.addHandler(app_handler)
        
        # 错误日志（只记录 WARNING 及以上）
        error_handler = RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.WARNING)
        error_formatter = logging.Formatter(log_format, date_format)
        error_handler.setFormatter(error_formatter)
        root_logger.addHandler(error_handler)
        
        # 调试日志（只记录 DEBUG）
        debug_handler = RotatingFileHandler(
            DEBUG_LOG_FILE,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding="utf-8"
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_formatter = logging.Formatter(log_format, date_format)
        debug_handler.setFormatter(debug_formatter)
        root_logger.addHandler(debug_handler)
    
    # 配置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # 记录日志系统初始化
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("日志系统已初始化")
    logger.info(f"日志级别: {log_level}")
    logger.info(f"文件日志: {'启用' if enable_file_logging else '禁用'}")
    logger.info(f"控制台日志: {'启用' if enable_console_logging else '禁用'}")
    logger.info(f"日志目录: {LOG_DIR}")
    logger.info("=" * 80)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器。
    
    Parameters
    ----------
    name : Optional[str]
        日志记录器名称，通常使用 __name__
    
    Returns
    -------
    logging.Logger
        配置好的日志记录器
    """
    return logging.getLogger(name or __name__)


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: Optional[int] = None,
    duration_ms: Optional[float] = None,
    user_id: Optional[int] = None,
    **kwargs
) -> None:
    """
    记录 HTTP 请求的详细信息。
    
    Parameters
    ----------
    logger : logging.Logger
        日志记录器
    method : str
        HTTP 方法
    path : str
        请求路径
    status_code : Optional[int]
        响应状态码
    duration_ms : Optional[float]
        请求处理时间（毫秒）
    user_id : Optional[int]
        用户 ID
    **kwargs
        其他要记录的信息
    """
    parts = [f"{method} {path}"]
    
    if status_code:
        parts.append(f"status={status_code}")
    
    if duration_ms is not None:
        parts.append(f"duration={duration_ms:.2f}ms")
    
    if user_id:
        parts.append(f"user_id={user_id}")
    
    if kwargs:
        extra_info = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        parts.append(extra_info)
    
    message = " | ".join(parts)
    logger.info(f"🌐 {message}")


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table: str,
    record_id: Optional[int] = None,
    duration_ms: Optional[float] = None,
    **kwargs
) -> None:
    """
    记录数据库操作的详细信息。
    
    Parameters
    ----------
    logger : logging.Logger
        日志记录器
    operation : str
        操作类型（SELECT, INSERT, UPDATE, DELETE）
    table : str
        表名
    record_id : Optional[int]
        记录 ID
    duration_ms : Optional[float]
        操作耗时（毫秒）
    **kwargs
        其他要记录的信息
    """
    parts = [f"{operation} {table}"]
    
    if record_id:
        parts.append(f"id={record_id}")
    
    if duration_ms is not None:
        parts.append(f"duration={duration_ms:.2f}ms")
    
    if kwargs:
        extra_info = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        parts.append(extra_info)
    
    message = " | ".join(parts)
    logger.debug(f"💾 {message}")


def log_api_call(
    logger: logging.Logger,
    service: str,
    endpoint: str,
    method: str = "POST",
    duration_ms: Optional[float] = None,
    success: bool = True,
    **kwargs
) -> None:
    """
    记录外部 API 调用的详细信息。
    
    Parameters
    ----------
    logger : logging.Logger
        日志记录器
    service : str
        服务名称（如 "Ollama", "OutdoorActive"）
    endpoint : str
        API 端点
    method : str
        HTTP 方法
    duration_ms : Optional[float]
        调用耗时（毫秒）
    success : bool
        是否成功
    **kwargs
        其他要记录的信息
    """
    status = "✅" if success else "❌"
    parts = [f"{status} {service} {method} {endpoint}"]
    
    if duration_ms is not None:
        parts.append(f"duration={duration_ms:.2f}ms")
    
    if kwargs:
        extra_info = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        parts.append(extra_info)
    
    message = " | ".join(parts)
    level = logging.INFO if success else logging.ERROR
    logger.log(level, f"🔌 {message}")


def log_business_logic(
    logger: logging.Logger,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    **kwargs
) -> None:
    """
    记录业务逻辑操作的详细信息。
    
    Parameters
    ----------
    logger : logging.Logger
        日志记录器
    action : str
        操作描述（如 "created", "updated", "calculated"）
    entity_type : str
        实体类型（如 "Profile", "Route", "Souvenir"）
    entity_id : Optional[int]
        实体 ID
    **kwargs
        其他要记录的信息
    """
    parts = [f"{action} {entity_type}"]
    
    if entity_id:
        parts.append(f"id={entity_id}")
    
    if kwargs:
        extra_info = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        parts.append(extra_info)
    
    message = " | ".join(parts)
    logger.info(f"📋 {message}")


# 自动从设置初始化日志系统
def init_logging_from_settings() -> None:
    """从应用设置初始化日志系统。"""
    settings = get_settings()
    
    # 从环境变量或设置中读取日志配置
    log_level = getattr(settings, "log_level", "INFO")
    enable_file = getattr(settings, "log_enable_file", True)
    enable_console = getattr(settings, "log_enable_console", True)
    detailed_format = getattr(settings, "log_detailed_format", True)
    
    setup_logging(
        log_level=log_level,
        enable_file_logging=enable_file,
        enable_console_logging=enable_console,
        detailed_format=detailed_format
    )

