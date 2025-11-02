"""
全局快捷键管理模块
支持注册和监听全局快捷键，用于快速启动键盘输入功能
"""

import threading
import time
from typing import Dict, Callable, Optional, Tuple
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GlobalHotkeyManager:
    """全局快捷键管理器"""
    
    def __init__(self):
        self.hotkey_combinations: Dict[str, Dict] = {}
        self.listener: Optional[keyboard.GlobalHotKeys] = None
        self.is_running = False
        self.lock = threading.Lock()
        
        # 默认快捷键配置
        self.default_hotkeys = {
            'start_typing': {
                'combination': '<ctrl>+<shift>+t',
                'description': '开始/停止键盘输入',
                'enabled': True
            },
            'emergency_stop': {
                'combination': '<ctrl>+<shift>+s',
                'description': '紧急停止输入',
                'enabled': True
            }
        }
        
        # 回调函数映射
        self.callbacks: Dict[str, Callable] = {}
    
    def register_callback(self, hotkey_name: str, callback: Callable) -> bool:
        """
        注册快捷键回调函数
        
        Args:
            hotkey_name: 快捷键名称
            callback: 回调函数
            
        Returns:
            bool: 注册是否成功
        """
        try:
            with self.lock:
                self.callbacks[hotkey_name] = callback
                logger.info(f"已注册快捷键回调: {hotkey_name}")
                return True
        except Exception as e:
            logger.error(f"注册快捷键回调失败: {hotkey_name}, 错误: {e}")
            return False
    
    def update_hotkey_combination(self, hotkey_name: str, combination: str) -> bool:
        """
        更新快捷键组合
        
        Args:
            hotkey_name: 快捷键名称
            combination: 新的快捷键组合
            
        Returns:
            bool: 更新是否成功
        """
        try:
            if hotkey_name in self.default_hotkeys:
                self.default_hotkeys[hotkey_name]['combination'] = combination
                logger.info(f"已更新快捷键组合: {hotkey_name} -> {combination}")
                
                # 如果监听器正在运行，需要重启
                if self.is_running:
                    self.stop_listener()
                    time.sleep(0.1)  # 短暂延迟确保停止完成
                    self.start_listener()
                
                return True
            else:
                logger.warning(f"未找到快捷键: {hotkey_name}")
                return False
        except Exception as e:
            logger.error(f"更新快捷键组合失败: {hotkey_name}, 错误: {e}")
            return False
    
    def enable_hotkey(self, hotkey_name: str, enabled: bool = True) -> bool:
        """
        启用或禁用快捷键
        
        Args:
            hotkey_name: 快捷键名称
            enabled: 是否启用
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if hotkey_name in self.default_hotkeys:
                self.default_hotkeys[hotkey_name]['enabled'] = enabled
                logger.info(f"快捷键 {hotkey_name} {'启用' if enabled else '禁用'}")
                
                # 重启监听器以应用更改
                if self.is_running:
                    self.stop_listener()
                    time.sleep(0.1)
                    self.start_listener()
                
                return True
            else:
                logger.warning(f"未找到快捷键: {hotkey_name}")
                return False
        except Exception as e:
            logger.error(f"设置快捷键状态失败: {hotkey_name}, 错误: {e}")
            return False
    
    def _create_hotkey_handler(self, hotkey_name: str) -> Callable:
        """
        创建快捷键处理函数
        
        Args:
            hotkey_name: 快捷键名称
            
        Returns:
            Callable: 处理函数
        """
        def handler():
            try:
                if hotkey_name in self.callbacks:
                    logger.info(f"触发快捷键: {hotkey_name}")
                    self.callbacks[hotkey_name]()
                else:
                    logger.warning(f"未找到快捷键回调: {hotkey_name}")
            except Exception as e:
                logger.error(f"执行快捷键回调失败: {hotkey_name}, 错误: {e}")
        
        return handler
    
    def start_listener(self) -> bool:
        """
        启动全局快捷键监听器
        
        Returns:
            bool: 启动是否成功
        """
        try:
            with self.lock:
                if self.is_running:
                    logger.warning("快捷键监听器已在运行")
                    return True
                
                # 构建启用的快捷键映射
                active_hotkeys = {}
                for hotkey_name, config in self.default_hotkeys.items():
                    if config['enabled']:
                        combination = config['combination']
                        handler = self._create_hotkey_handler(hotkey_name)
                        active_hotkeys[combination] = handler
                        logger.info(f"注册快捷键: {combination} -> {hotkey_name}")
                
                if not active_hotkeys:
                    logger.warning("没有启用的快捷键")
                    return False
                
                # 创建并启动监听器
                self.listener = keyboard.GlobalHotKeys(active_hotkeys)
                self.listener.start()
                self.is_running = True
                
                logger.info(f"全局快捷键监听器已启动，共注册 {len(active_hotkeys)} 个快捷键")
                return True
                
        except Exception as e:
            logger.error(f"启动快捷键监听器失败: {e}")
            return False
    
    def stop_listener(self) -> bool:
        """
        停止全局快捷键监听器
        
        Returns:
            bool: 停止是否成功
        """
        try:
            with self.lock:
                if not self.is_running:
                    logger.warning("快捷键监听器未在运行")
                    return True
                
                if self.listener:
                    self.listener.stop()
                    self.listener = None
                
                self.is_running = False
                logger.info("全局快捷键监听器已停止")
                return True
                
        except Exception as e:
            logger.error(f"停止快捷键监听器失败: {e}")
            return False
    
    def get_hotkey_status(self) -> Dict:
        """
        获取快捷键状态信息
        
        Returns:
            Dict: 状态信息
        """
        return {
            'is_running': self.is_running,
            'hotkeys': self.default_hotkeys.copy(),
            'registered_callbacks': list(self.callbacks.keys())
        }
    
    def parse_hotkey_combination(self, combination: str) -> Tuple[bool, str]:
        """
        解析并验证快捷键组合格式
        
        Args:
            combination: 快捷键组合字符串
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息或格式化后的组合)
        """
        try:
            # 尝试解析快捷键组合
            # 这里使用pynput的内部解析来验证格式
            from pynput.keyboard import HotKey
            
            # 简单的格式验证
            if not combination or not isinstance(combination, str):
                return False, "快捷键组合不能为空"
            
            # 检查是否包含修饰键
            modifiers = ['<ctrl>', '<shift>', '<alt>', '<cmd>']
            has_modifier = any(mod in combination.lower() for mod in modifiers)
            
            if not has_modifier:
                return False, "快捷键组合必须包含至少一个修饰键 (Ctrl, Shift, Alt)"
            
            # 格式化组合键（统一小写）
            formatted = combination.lower().strip()
            
            return True, formatted
            
        except Exception as e:
            return False, f"快捷键组合格式错误: {e}"


# 全局快捷键管理器实例
hotkey_manager = GlobalHotkeyManager()


def initialize_hotkey_manager() -> GlobalHotkeyManager:
    """
    初始化全局快捷键管理器
    
    Returns:
        GlobalHotkeyManager: 管理器实例
    """
    return hotkey_manager


def cleanup_hotkey_manager():
    """清理快捷键管理器资源"""
    if hotkey_manager.is_running:
        hotkey_manager.stop_listener()
        logger.info("快捷键管理器已清理")