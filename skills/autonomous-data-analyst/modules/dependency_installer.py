"""依赖安装模块 - 自动识别并安装 Python 依赖"""

from __future__ import annotations

import importlib
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DependencySpec:
    """依赖规格"""
    package_name: str
    import_name: str | None = None
    min_version: str | None = None
    reason: str = ""


@dataclass
class InstallResult:
    """安装结果"""
    package_name: str
    success: bool
    already_installed: bool = False
    error_message: str | None = None


# 分析方法到依赖的映射
METHOD_DEPENDENCY_MAP: dict[str, list[DependencySpec]] = {
    "descriptive_stats": [
        DependencySpec(
            package_name="numpy",
            import_name="numpy",
            reason="基础数值计算",
        ),
        DependencySpec(
            package_name="pandas",
            import_name="pandas",
            reason="数据处理",
        ),
    ],
    "correlation": [
        DependencySpec(
            package_name="scipy",
            import_name="scipy",
            reason="统计检验",
        ),
        DependencySpec(
            package_name="pandas",
            import_name="pandas",
            reason="数据处理",
        ),
    ],
    "regression": [
        DependencySpec(
            package_name="scikit-learn",
            import_name="sklearn",
            reason="回归模型",
        ),
        DependencySpec(
            package_name="numpy",
            import_name="numpy",
            reason="数值计算",
        ),
    ],
    "clustering": [
        DependencySpec(
            package_name="scikit-learn",
            import_name="sklearn",
            reason="聚类算法",
        ),
    ],
    "classification": [
        DependencySpec(
            package_name="scikit-learn",
            import_name="sklearn",
            reason="分类算法",
        ),
    ],
    "time_series": [
        DependencySpec(
            package_name="statsmodels",
            import_name="statsmodels",
            reason="时间序列分析",
        ),
        DependencySpec(
            package_name="pandas",
            import_name="pandas",
            reason="时间序列处理",
        ),
    ],
    "ab_test": [
        DependencySpec(
            package_name="scipy",
            import_name="scipy",
            reason="统计检验",
        ),
    ],
    "funnel": [
        DependencySpec(
            package_name="pandas",
            import_name="pandas",
            reason="数据处理",
        ),
    ],
    "cohort": [
        DependencySpec(
            package_name="pandas",
            import_name="pandas",
            reason="数据处理",
        ),
    ],
    "segmentation": [
        DependencySpec(
            package_name="scikit-learn",
            import_name="sklearn",
            reason="分群算法",
        ),
    ],
}

# 数据源类型到依赖的映射
SOURCE_DEPENDENCY_MAP: dict[str, list[DependencySpec]] = {
    "database": [
        DependencySpec(
            package_name="sqlalchemy",
            import_name="sqlalchemy",
            reason="数据库连接",
        ),
    ],
    "file": [
        DependencySpec(
            package_name="pandas",
            import_name="pandas",
            reason="文件读写",
        ),
        DependencySpec(
            package_name="openpyxl",
            import_name="openpyxl",
            reason="Excel 文件支持",
        ),
    ],
    "web_page": [
        DependencySpec(
            package_name="requests",
            import_name="requests",
            reason="HTTP 请求",
        ),
        DependencySpec(
            package_name="beautifulsoup4",
            import_name="bs4",
            reason="HTML 解析",
        ),
    ],
}

# 可视化依赖
VISUALIZATION_DEPENDENCIES: list[DependencySpec] = [
    DependencySpec(
        package_name="matplotlib",
        import_name="matplotlib",
        reason="基础绘图",
    ),
    DependencySpec(
        package_name="seaborn",
        import_name="seaborn",
        reason="统计可视化",
    ),
]


class DependencyInstaller:
    """依赖安装器"""

    def __init__(self, auto_install: bool = True) -> None:
        self.auto_install = auto_install
        self._installed_packages: set[str] = set()
        self._failed_packages: set[str] = set()

    def identify_dependencies(
        self,
        analysis_methods: list[str] | None = None,
        source_types: list[str] | None = None,
        need_visualization: bool = True,
    ) -> list[DependencySpec]:
        """
        识别所需依赖

        Args:
            analysis_methods: 使用的分析方法
            source_types: 数据源类型
            need_visualization: 是否需要可视化

        Returns:
            依赖规格列表
        """
        deps: list[DependencySpec] = []
        seen: set[str] = set()

        for method in (analysis_methods or []):
            for dep in METHOD_DEPENDENCY_MAP.get(method, []):
                if dep.package_name not in seen:
                    deps.append(dep)
                    seen.add(dep.package_name)

        for src_type in (source_types or []):
            for dep in SOURCE_DEPENDENCY_MAP.get(src_type, []):
                if dep.package_name not in seen:
                    deps.append(dep)
                    seen.add(dep.package_name)

        if need_visualization:
            for dep in VISUALIZATION_DEPENDENCIES:
                if dep.package_name not in seen:
                    deps.append(dep)
                    seen.add(dep.package_name)

        return deps

    def check_installation_status(
        self, dependencies: list[DependencySpec]
    ) -> dict[str, bool]:
        """
        检查依赖安装状态

        Args:
            dependencies: 依赖规格列表

        Returns:
            {包名: 是否已安装}
        """
        status: dict[str, bool] = {}

        for dep in dependencies:
            import_name = dep.import_name or dep.package_name.replace("-", "_")
            is_installed = self._is_package_available(import_name)
            status[dep.package_name] = is_installed

        return status

    def install_dependencies(
        self,
        dependencies: list[DependencySpec],
        upgrade: bool = False,
    ) -> list[InstallResult]:
        """
        安装依赖

        Args:
            dependencies: 依赖规格列表
            upgrade: 是否升级到最新版本

        Returns:
            安装结果列表
        """
        results: list[InstallResult] = []

        for dep in dependencies:
            import_name = dep.import_name or dep.package_name.replace("-", "_")

            if self._is_package_available(import_name):
                results.append(
                    InstallResult(
                        package_name=dep.package_name,
                        success=True,
                        already_installed=True,
                    )
                )
                self._installed_packages.add(dep.package_name)
                continue

            if not self.auto_install:
                results.append(
                    InstallResult(
                        package_name=dep.package_name,
                        success=False,
                        error_message="自动安装已禁用",
                    )
                )
                continue

            result = self._install_package(dep.package_name, upgrade)
            results.append(result)

            if result.success:
                self._installed_packages.add(dep.package_name)
            else:
                self._failed_packages.add(dep.package_name)

        return results

    def get_summary(self) -> dict[str, Any]:
        """获取安装摘要"""
        return {
            "installed": list(self._installed_packages),
            "failed": list(self._failed_packages),
            "total_installed": len(self._installed_packages),
            "total_failed": len(self._failed_packages),
        }

    @staticmethod
    def _is_package_available(import_name: str) -> bool:
        """检查包是否可用"""
        try:
            importlib.import_module(import_name)
            return True
        except ImportError:
            return False

    def _install_package(
        self, package_name: str, upgrade: bool
    ) -> InstallResult:
        """安装单个包"""
        cmd = [sys.executable, "-m", "pip", "install"]

        if upgrade:
            cmd.append("--upgrade")

        cmd.append(package_name)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                logger.info("包 %s 安装成功", package_name)
                return InstallResult(package_name=package_name, success=True)

            logger.error("包 %s 安装失败: %s", package_name, result.stderr)
            return InstallResult(
                package_name=package_name,
                success=False,
                error_message=result.stderr[:200],
            )

        except subprocess.TimeoutExpired:
            return InstallResult(
                package_name=package_name,
                success=False,
                error_message="安装超时",
            )
        except Exception as exc:
            return InstallResult(
                package_name=package_name,
                success=False,
                error_message=str(exc),
            )
