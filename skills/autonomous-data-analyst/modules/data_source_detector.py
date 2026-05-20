"""数据源检测模块 - 自动识别数据源类型并提取连接信息"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """数据源类型"""
    FINANCIAL = "financial"
    ECOMMERCE = "ecommerce"
    CRM = "crm"
    ERP = "erp"
    LOG = "log"
    PUBLIC_STATS = "public_stats"
    DATABASE = "database"
    API = "api"
    FILE = "file"
    WEB_PAGE = "web_page"


class AccessProtocol(Enum):
    """访问协议"""
    LOCAL_FILE = "local"
    S3 = "s3"
    HDFS = "hdfs"
    HTTP = "http"
    HTTPS = "https"
    FTP = "ftp"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    SQLITE = "sqlite"


@dataclass
class DataSourceInfo:
    """数据源信息"""
    source_type: DataSourceType
    access_protocol: AccessProtocol | None = None
    location: str = ""
    connection_params: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    estimated_size: str | None = None
    is_accessible: bool = False


@dataclass
class DetectionResult:
    """检测结果"""
    primary_source: DataSourceInfo | None = None
    alternative_sources: list[DataSourceInfo] = field(default_factory=list)
    confidence: float = 0.0
    detection_notes: str = ""


# 文件扩展名到数据源类型的映射
FILE_TYPE_MAP: dict[str, DataSourceType] = {
    ".csv": DataSourceType.FILE,
    ".xlsx": DataSourceType.FILE,
    ".xls": DataSourceType.FILE,
    ".parquet": DataSourceType.FILE,
    ".json": DataSourceType.FILE,
    ".jsonl": DataSourceType.FILE,
    ".feather": DataSourceType.FILE,
    ".hdf5": DataSourceType.FILE,
    ".sqlite": DataSourceType.FILE,
    ".db": DataSourceType.FILE,
}

# URL 模式到数据源类型的映射
URL_PATTERN_MAP: list[tuple[str, DataSourceType, AccessProtocol]] = [
    ("s3://", DataSourceType.FILE, AccessProtocol.S3),
    ("hdfs://", DataSourceType.FILE, AccessProtocol.HDFS),
    ("mysql://", DataSourceType.DATABASE, AccessProtocol.MYSQL),
    ("postgresql://", DataSourceType.DATABASE, AccessProtocol.POSTGRESQL),
    ("postgres://", DataSourceType.DATABASE, AccessProtocol.POSTGRESQL),
    ("mongodb://", DataSourceType.DATABASE, AccessProtocol.MONGODB),
    ("redis://", DataSourceType.DATABASE, AccessProtocol.REDIS),
    ("sqlite://", DataSourceType.DATABASE, AccessProtocol.SQLITE),
    ("ftp://", DataSourceType.WEB_PAGE, AccessProtocol.FTP),
    ("http://", DataSourceType.WEB_PAGE, AccessProtocol.HTTP),
    ("https://", DataSourceType.WEB_PAGE, AccessProtocol.HTTPS),
]

# 业务领域关键词
BUSINESS_KEYWORDS: dict[DataSourceType, list[str]] = {
    DataSourceType.FINANCIAL: ["财务", "营收", "利润", "成本", "预算", "审计", "finance"],
    DataSourceType.ECOMMERCE: ["电商", "交易", "订单", "商品", "店铺", "ecommerce"],
    DataSourceType.CRM: ["客户", "CRM", "联系", "客户管理"],
    DataSourceType.ERP: ["ERP", "企业资源", "生产", "物料", "BOM"],
    DataSourceType.LOG: ["日志", "log", "访问日志", "server log"],
    DataSourceType.PUBLIC_STATS: ["统计", "公开", "public", "政府", " census"],
}


class DataSourceDetector:
    """数据源检测器"""

    def detect(self, source_hint: str) -> DetectionResult:
        """
        检测数据源类型

        Args:
            source_hint: 数据源提示（路径、URL、描述等）

        Returns:
            DetectionResult: 检测结果
        """
        if not source_hint or not source_hint.strip():
            return DetectionResult(detection_notes="未提供数据源信息")

        hint = source_hint.strip()
        source_info = self._classify_source(hint)

        if source_info is None:
            return DetectionResult(detection_notes=f"无法识别的数据源: {hint}")

        source_info.is_accessible = self._check_accessibility(source_info)

        return DetectionResult(
            primary_source=source_info,
            confidence=self._calculate_confidence(source_info),
        )

    def detect_from_context(
        self, context: dict[str, Any]
    ) -> DetectionResult:
        """
        从上下文推断数据源

        Args:
            context: 包含领域、目标等信息的上下文

        Returns:
            DetectionResult: 检测结果
        """
        domain = context.get("domain", "")
        objective = context.get("objective", "")
        combined = f"{domain} {objective}"

        sources: list[DataSourceInfo] = []

        for src_type, keywords in BUSINESS_KEYWORDS.items():
            if any(kw.lower() in combined.lower() for kw in keywords):
                sources.append(
                    DataSourceInfo(
                        source_type=src_type,
                        metadata={"inferred_from": "context"},
                    )
                )

        if not sources:
            return DetectionResult(detection_notes="无法从上下文推断数据源")

        return DetectionResult(
            primary_source=sources[0],
            alternative_sources=sources[1:],
            confidence=0.6,
            detection_notes="基于上下文推断",
        )

    def _classify_source(self, hint: str) -> DataSourceInfo | None:
        """分类数据源"""
        # 检查是否为 URL
        url_info = self._parse_url(hint)
        if url_info is not None:
            return url_info

        # 检查是否为本地文件
        file_info = self._parse_file_path(hint)
        if file_info is not None:
            return file_info

        # 检查是否为数据库连接字符串
        db_info = self._parse_connection_string(hint)
        if db_info is not None:
            return db_info

        return None

    def _parse_url(self, hint: str) -> DataSourceInfo | None:
        """解析 URL 类型数据源"""
        for prefix, src_type, protocol in URL_PATTERN_MAP:
            if hint.lower().startswith(prefix):
                params: dict[str, Any] = {}
                if protocol in (AccessProtocol.MYSQL, AccessProtocol.POSTGRESQL):
                    params = self._extract_db_params(hint)

                return DataSourceInfo(
                    source_type=src_type,
                    access_protocol=protocol,
                    location=hint,
                    connection_params=params,
                )
        return None

    def _parse_file_path(self, hint: str) -> DataSourceInfo | None:
        """解析本地文件路径"""
        path = Path(hint)
        if not path.exists() and not hint.startswith("/"):
            return None

        ext = path.suffix.lower()
        src_type = FILE_TYPE_MAP.get(ext)
        if src_type is None:
            return None

        size = self._get_file_size(path)

        return DataSourceInfo(
            source_type=src_type,
            access_protocol=AccessProtocol.LOCAL_FILE,
            location=str(path),
            estimated_size=size,
        )

    def _parse_connection_string(self, hint: str) -> DataSourceInfo | None:
        """解析数据库连接字符串"""
        patterns = {
            "mysql": (DataSourceType.DATABASE, AccessProtocol.MYSQL),
            "postgresql": (DataSourceType.DATABASE, AccessProtocol.POSTGRESQL),
            "mongo": (DataSourceType.DATABASE, AccessProtocol.MONGODB),
            "redis": (DataSourceType.DATABASE, AccessProtocol.REDIS),
        }

        for keyword, (src_type, protocol) in patterns.items():
            if keyword in hint.lower():
                return DataSourceInfo(
                    source_type=src_type,
                    access_protocol=protocol,
                    location=hint,
                    connection_params=self._extract_db_params(hint),
                )
        return None

    def _extract_db_params(self, connection_string: str) -> dict[str, Any]:
        """从连接字符串提取参数"""
        try:
            parsed = urlparse(connection_string)
            return {
                "host": parsed.hostname,
                "port": parsed.port,
                "database": parsed.path.lstrip("/") if parsed.path else None,
                "username": parsed.username,
            }
        except Exception:
            return {}

    def _check_accessibility(self, source: DataSourceInfo) -> bool:
        """检查数据源是否可访问"""
        if source.access_protocol == AccessProtocol.LOCAL_FILE:
            return Path(source.location).exists()

        if source.access_protocol in (
            AccessProtocol.HTTP, AccessProtocol.HTTPS
        ):
            return True  # 假设 URL 可达

        if source.access_protocol in (
            AccessProtocol.MYSQL,
            AccessProtocol.POSTGRESQL,
            AccessProtocol.MONGODB,
            AccessProtocol.REDIS,
            AccessProtocol.SQLITE,
        ):
            return source.connection_params.get("host") is not None

        return True

    def _calculate_confidence(self, source: DataSourceInfo) -> float:
        """计算检测置信度"""
        base = 0.5

        if source.access_protocol is not None:
            base += 0.2

        if source.location:
            base += 0.1

        if source.is_accessible:
            base += 0.2

        return min(base, 1.0)

    @staticmethod
    def _get_file_size(path: Path) -> str | None:
        """获取文件大小"""
        try:
            if path.exists():
                size_bytes = path.stat().st_size
                if size_bytes < 1024:
                    return f"{size_bytes}B"
                if size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.1f}KB"
                if size_bytes < 1024 * 1024 * 1024:
                    return f"{size_bytes / 1024 / 1024:.1f}MB"
                return f"{size_bytes / 1024 / 1024 / 1024:.1f}GB"
        except OSError:
            pass
        return None
