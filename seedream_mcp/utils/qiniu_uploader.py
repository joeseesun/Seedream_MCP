#!/usr/bin/env python3
"""
七牛云上传工具

提供图片上传到七牛云存储的功能。
"""

import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)


class QiniuUploader:
    """七牛云上传器
    
    负责将本地图片上传到七牛云存储。
    """
    
    def __init__(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        domain: Optional[str] = None
    ):
        """初始化七牛云上传器
        
        Args:
            access_key: 七牛云 Access Key，默认从环境变量 QINIU_ACCESS_KEY 读取
            secret_key: 七牛云 Secret Key，默认从环境变量 QINIU_SECRET_KEY 读取
            bucket_name: 存储空间名称，默认从环境变量 QINIU_BUCKET_NAME 读取
            domain: CDN 域名，默认从环境变量 QINIU_DOMAIN 读取
        """
        self.access_key = access_key or os.getenv("QINIU_ACCESS_KEY")
        self.secret_key = secret_key or os.getenv("QINIU_SECRET_KEY")
        self.bucket_name = bucket_name or os.getenv("QINIU_BUCKET_NAME")
        self.domain = domain or os.getenv("QINIU_DOMAIN")
        
        # 检查是否配置了七牛云
        self.enabled = bool(self.access_key and self.secret_key and self.bucket_name and self.domain)
        
        if self.enabled:
            try:
                # 延迟导入 qiniu SDK
                from qiniu import Auth, put_file
                self.auth = Auth(self.access_key, self.secret_key)
                self.put_file = put_file
                logger.info(f"七牛云上传器初始化成功: bucket={self.bucket_name}, domain={self.domain}")
            except ImportError:
                logger.warning("未安装 qiniu SDK，七牛云上传功能将被禁用。请运行: pip install qiniu")
                self.enabled = False
        else:
            logger.info("七牛云配置未完整，上传功能已禁用")
    
    def upload_file(self, local_path: str, key: Optional[str] = None) -> Optional[str]:
        """上传文件到七牛云
        
        Args:
            local_path: 本地文件路径
            key: 七牛云存储的文件名，如果不指定则自动生成
            
        Returns:
            上传成功返回文件的公开访问 URL，失败返回 None
        """
        if not self.enabled:
            logger.debug("七牛云上传未启用")
            return None
        
        try:
            # 检查文件是否存在
            if not Path(local_path).exists():
                logger.error(f"文件不存在: {local_path}")
                return None
            
            # 生成文件名
            if not key:
                # 使用时间戳 + 原文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = Path(local_path).name
                key = f"seedream/{timestamp}_{filename}"
            
            # 生成上传凭证
            token = self.auth.upload_token(self.bucket_name, key, 3600)
            
            # 上传文件
            logger.info(f"开始上传文件到七牛云: {local_path} -> {key}")
            ret, info = self.put_file(token, key, local_path)
            
            if info.status_code == 200:
                # 生成公开访问 URL
                url = f"{self.domain.rstrip('/')}/{key}"
                logger.info(f"文件上传成功: {url}")
                return url
            else:
                logger.error(f"文件上传失败: status={info.status_code}, error={info.error}")
                return None
                
        except Exception as e:
            logger.error(f"上传文件到七牛云时出错: {e}", exc_info=True)
            return None
    
    def upload_multiple(self, local_paths: list[str]) -> list[Optional[str]]:
        """批量上传文件
        
        Args:
            local_paths: 本地文件路径列表
            
        Returns:
            URL 列表，失败的项为 None
        """
        urls = []
        for path in local_paths:
            url = self.upload_file(path)
            urls.append(url)
        return urls


# 全局单例
_uploader: Optional[QiniuUploader] = None


def get_qiniu_uploader() -> QiniuUploader:
    """获取七牛云上传器单例
    
    Returns:
        QiniuUploader 实例
    """
    global _uploader
    if _uploader is None:
        _uploader = QiniuUploader()
    return _uploader

