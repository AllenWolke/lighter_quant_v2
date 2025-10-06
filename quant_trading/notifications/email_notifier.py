"""
邮件通知器
支持SMTP邮件发送
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from .base_notifier import BaseNotifier, Notification


class EmailNotifier(BaseNotifier):
    """邮件通知器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化邮件通知器
        
        Args:
            config: 邮件配置
        """
        super().__init__(config)
        self.logger = logging.getLogger("EmailNotifier")
        
        # SMTP配置
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.from_email = config.get("from_email", self.username)
        self.to_emails = config.get("to_emails", [])
        
        # 邮件模板配置
        self.template_config = config.get("template", {})
        
    async def send_notification(self, notification: Notification) -> bool:
        """发送单个通知"""
        if not self.should_send(notification):
            return True
            
        try:
            # 创建邮件
            msg = self._create_email(notification)
            
            # 发送邮件
            await self._send_email(msg)
            
            self.logger.info(f"邮件通知发送成功: {notification.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"邮件通知发送失败: {e}")
            return False
            
    async def send_batch_notifications(self, notifications: List[Notification]) -> bool:
        """批量发送通知"""
        if not notifications:
            return True
            
        try:
            # 过滤需要发送的通知
            valid_notifications = [n for n in notifications if self.should_send(n)]
            
            if not valid_notifications:
                return True
                
            # 创建批量邮件
            msg = self._create_batch_email(valid_notifications)
            
            # 发送邮件
            await self._send_email(msg)
            
            self.logger.info(f"批量邮件通知发送成功: {len(valid_notifications)} 条")
            return True
            
        except Exception as e:
            self.logger.error(f"批量邮件通知发送失败: {e}")
            return False
            
    def _create_email(self, notification: Notification) -> MIMEMultipart:
        """创建邮件"""
        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_email
        msg['To'] = ', '.join(self.to_emails)
        msg['Subject'] = f"[量化交易] {notification.title}"
        
        # 创建邮件内容
        html_content = self._create_html_content(notification)
        text_content = self._create_text_content(notification)
        
        # 添加文本版本
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # 添加HTML版本
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        return msg
        
    def _create_batch_email(self, notifications: List[Notification]) -> MIMEMultipart:
        """创建批量邮件"""
        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_email
        msg['To'] = ', '.join(self.to_emails)
        msg['Subject'] = f"[量化交易] 批量通知 - {len(notifications)} 条消息"
        
        # 创建批量邮件内容
        html_content = self._create_batch_html_content(notifications)
        text_content = self._create_batch_text_content(notifications)
        
        # 添加文本版本
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # 添加HTML版本
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        return msg
        
    def _create_html_content(self, notification: Notification) -> str:
        """创建HTML邮件内容"""
        level_colors = {
            "info": "#007bff",
            "warning": "#ffc107", 
            "error": "#dc3545",
            "critical": "#6f42c1"
        }
        
        color = level_colors.get(notification.level.value, "#007bff")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>量化交易通知</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; border-radius: 0 0 8px 8px; font-size: 12px; color: #6c757d; }}
                .level {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
                .level-info {{ background-color: #d1ecf1; color: #0c5460; }}
                .level-warning {{ background-color: #fff3cd; color: #856404; }}
                .level-error {{ background-color: #f8d7da; color: #721c24; }}
                .level-critical {{ background-color: #e2e3e5; color: #383d41; }}
                .data-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                .data-table th, .data-table td {{ border: 1px solid #dee2e6; padding: 8px; text-align: left; }}
                .data-table th {{ background-color: #f8f9fa; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚀 量化交易通知</h2>
                    <span class="level level-{notification.level.value}">{notification.level.value.upper()}</span>
                </div>
                <div class="content">
                    <h3>{notification.title}</h3>
                    <p>{notification.message}</p>
                    <p><strong>时间:</strong> {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>类型:</strong> {notification.notification_type.value}</p>
        """
        
        # 添加附加数据
        if notification.data:
            html += """
                    <h4>详细信息:</h4>
                    <table class="data-table">
            """
            for key, value in notification.data.items():
                html += f"""
                        <tr>
                            <th>{key}</th>
                            <td>{value}</td>
                        </tr>
                """
            html += """
                    </table>
            """
        
        html += """
                </div>
                <div class="footer">
                    <p>此邮件由量化交易系统自动发送，请勿回复。</p>
                    <p>如有问题，请联系系统管理员。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    def _create_text_content(self, notification: Notification) -> str:
        """创建文本邮件内容"""
        text = f"""
量化交易通知
{'=' * 50}

级别: {notification.level.value.upper()}
类型: {notification.notification_type.value}
时间: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

标题: {notification.title}

内容: {notification.message}
"""
        
        # 添加附加数据
        if notification.data:
            text += "\n详细信息:\n"
            text += "-" * 30 + "\n"
            for key, value in notification.data.items():
                text += f"{key}: {value}\n"
        
        text += f"""
{'=' * 50}
此邮件由量化交易系统自动发送，请勿回复。
如有问题，请联系系统管理员。
"""
        
        return text
        
    def _create_batch_html_content(self, notifications: List[Notification]) -> str:
        """创建批量HTML邮件内容"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>量化交易批量通知</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #007bff; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; border-radius: 0 0 8px 8px; font-size: 12px; color: #6c757d; }}
                .notification {{ border: 1px solid #dee2e6; border-radius: 4px; margin-bottom: 15px; padding: 15px; }}
                .notification-header {{ font-weight: bold; margin-bottom: 10px; }}
                .notification-time {{ font-size: 12px; color: #6c757d; }}
                .level {{ display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold; margin-left: 10px; }}
                .level-info {{ background-color: #d1ecf1; color: #0c5460; }}
                .level-warning {{ background-color: #fff3cd; color: #856404; }}
                .level-error {{ background-color: #f8d7da; color: #721c24; }}
                .level-critical {{ background-color: #e2e3e5; color: #383d41; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🚀 量化交易批量通知</h2>
                    <p>共 {len(notifications)} 条消息</p>
                </div>
                <div class="content">
        """
        
        for i, notification in enumerate(notifications, 1):
            html += f"""
                    <div class="notification">
                        <div class="notification-header">
                            #{i} {notification.title}
                            <span class="level level-{notification.level.value}">{notification.level.value.upper()}</span>
                        </div>
                        <div class="notification-time">{notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
                        <p>{notification.message}</p>
            """
            
            if notification.data:
                html += "<ul>"
                for key, value in notification.data.items():
                    html += f"<li><strong>{key}:</strong> {value}</li>"
                html += "</ul>"
            
            html += "</div>"
        
        html += """
                </div>
                <div class="footer">
                    <p>此邮件由量化交易系统自动发送，请勿回复。</p>
                    <p>如有问题，请联系系统管理员。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    def _create_batch_text_content(self, notifications: List[Notification]) -> str:
        """创建批量文本邮件内容"""
        text = f"""
量化交易批量通知
{'=' * 50}

共 {len(notifications)} 条消息

"""
        
        for i, notification in enumerate(notifications, 1):
            text += f"""
消息 #{i}
{'-' * 30}
级别: {notification.level.value.upper()}
类型: {notification.notification_type.value}
时间: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
标题: {notification.title}
内容: {notification.message}
"""
            
            if notification.data:
                text += "详细信息:\n"
                for key, value in notification.data.items():
                    text += f"  {key}: {value}\n"
            
            text += "\n"
        
        text += f"""
{'=' * 50}
此邮件由量化交易系统自动发送，请勿回复。
如有问题，请联系系统管理员。
"""
        
        return text
        
    async def _send_email(self, msg: MIMEMultipart):
        """发送邮件"""
        try:
            # 创建SSL上下文
            context = ssl.create_default_context()
            
            # 连接SMTP服务器
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                
                # 发送邮件
                server.send_message(msg)
                
        except Exception as e:
            self.logger.error(f"SMTP发送失败: {e}")
            raise
