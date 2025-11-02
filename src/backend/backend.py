from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import random
import ctypes
from ctypes import wintypes
from pynput.keyboard import Controller, Key
import win32api
import win32gui
import win32con
import win32process

app = Flask(__name__)
CORS(app)

# 全局状态
typing_thread = None
stop_event = threading.Event()
status = {
    'is_typing': False,
    'progress': 0,
    'total_chars': 0,
    'current_status': 'IDLE',
    'last_event': 'SYSTEM_READY'
}

# 输入法控制相关
WM_INPUTLANGCHANGEREQUEST = 0x0050
ENGLISH_LAYOUT = 0x04090409
original_input_method = None
layout_handles = {}
english_layout_hkl = None
chinese_layout_hkl = None
current_active_layout = None
target_window_handle = None
target_thread_id = None
input_switch_lock = threading.Lock()
special_key_delay = 0.30

# 键盘控制器
keyboard_controller = Controller()

# Windows API 常量
user32 = ctypes.windll.user32
VK_SHIFT = 0x10
VK_TAB = 0x09
VK_SPACE = 0x20
VK_ESCAPE = 0x1B
VK_RETURN = 0x0D
SCANCODE_TAB = 0x0F
SCANCODE_SPACE = 0x39
SCANCODE_ESCAPE = 0x01
SCANCODE_ENTER = 0x1C
SCANCODE_HOME = 0x47
SCANCODE_DELETE = 0x53


def send_unicode_character(character: str):
    """发送Unicode字符"""
    try:
        keyboard_controller.type(character)
        return True
    except Exception as e:
        print(f"Unicode 字符输入失败: {e}")
        return False


def prepare_input_layout_handles():
    """准备输入法句柄"""
    global layout_handles, english_layout_hkl, chinese_layout_hkl
    try:
        layout_handles.clear()
        layouts = win32api.GetKeyboardLayoutList()
        if layouts:
            for hkl in layouts:
                lang_id = hkl & 0xFFFF
                layout_handles.setdefault(lang_id, []).append(hkl)
                if lang_id == 0x0409 and english_layout_hkl is None:
                    english_layout_hkl = hkl
                elif lang_id == 0x0804 and chinese_layout_hkl is None:
                    chinese_layout_hkl = hkl
        if english_layout_hkl is None:
            try:
                loaded = win32api.LoadKeyboardLayout("00000409", 0)
                if loaded:
                    english_layout_hkl = loaded
                    layout_handles.setdefault(0x0409, []).append(loaded)
            except Exception as error:
                print(f"加载英文输入法失败: {error}")
        print(f"初始化输入法句柄 -> 英文: {hex(english_layout_hkl) if english_layout_hkl else 'None'}")
    except Exception as error:
        print(f"初始化输入法句柄失败: {error}")


def set_target_window_context(window_handle: int):
    """设置目标窗口上下文"""
    global target_window_handle, target_thread_id, original_input_method, current_active_layout
    try:
        target_window_handle = window_handle
        if window_handle:
            thread_id, _ = win32process.GetWindowThreadProcessId(window_handle)
            target_thread_id = thread_id
            original_input_method = win32api.GetKeyboardLayout(thread_id)
            current_active_layout = original_input_method
            prepare_input_layout_handles()
        else:
            target_thread_id = None
    except Exception as error:
        print(f"获取目标窗口线程信息失败: {error}")
        target_thread_id = None


def activate_layout_for_target(layout_handle: int) -> bool:
    """为目标窗口激活输入法"""
    if not layout_handle or not target_thread_id or not target_window_handle:
        return False
    current_thread_id = win32api.GetCurrentThreadId()
    attached = False
    try:
        if current_thread_id != target_thread_id:
            ctypes.set_last_error(0)
            attach_result = user32.AttachThreadInput(current_thread_id, target_thread_id, True)
            if attach_result:
                attached = True
        ctypes.set_last_error(0)
        user32.ActivateKeyboardLayout(ctypes.c_void_p(layout_handle & 0xFFFFFFFFFFFFFFFF), 0)
        win32gui.PostMessage(
            target_window_handle,
            WM_INPUTLANGCHANGEREQUEST,
            0,
            layout_handle
        )
        time.sleep(0.05)
        return True
    except Exception as error:
        print(f"激活输入法时发生异常: {error}")
        if attached:
            user32.AttachThreadInput(current_thread_id, target_thread_id, False)
    return False


def ensure_input_layout(layout_type: str, auto_switch: bool):
    """确保输入法布局"""
    global current_active_layout
    if not auto_switch or not target_thread_id:
        return
    if layout_type == "english":
        desired = english_layout_hkl or original_input_method
    elif layout_type == "chinese":
        desired = chinese_layout_hkl or original_input_method
    else:
        desired = None
    if not desired:
        return
    if current_active_layout and (current_active_layout & 0xFFFFFFFF) == (desired & 0xFFFFFFFF):
        return
    with input_switch_lock:
        activate_layout_for_target(desired)
        current_active_layout = desired


def classify_character_layout(character: str):
    """分类字符布局"""
    if not character:
        return None
    codepoint = ord(character)
    if codepoint < 32:
        return None
    if codepoint < 128:
        return "english"
    return "chinese"


def send_special_key(vk_code: int, pynput_key: Key, post_delay: float = 0.0, hold_time: float = 0.015) -> bool:
    """发送特殊键"""
    try:
        win32api.keybd_event(vk_code, 0, 0, 0)
        if hold_time > 0:
            time.sleep(hold_time)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    except Exception:
        try:
            keyboard_controller.press(pynput_key)
            if hold_time > 0:
                time.sleep(hold_time)
            keyboard_controller.release(pynput_key)
        except Exception as e:
            print(f"发送特殊键失败: {e}")
            return False
    if post_delay > 0:
        time.sleep(post_delay)
    return True


def send_scan_key(scancode: int, extended: bool = False, post_delay: float = 0.12, hold_time: float = 0.015) -> bool:
    """发送扫描码"""
    flags_down = win32con.KEYEVENTF_SCANCODE
    if extended:
        flags_down |= win32con.KEYEVENTF_EXTENDEDKEY
    flags_up = flags_down | win32con.KEYEVENTF_KEYUP
    try:
        win32api.keybd_event(0, scancode, flags_down, 0)
        if hold_time > 0:
            time.sleep(hold_time)
        win32api.keybd_event(0, scancode, flags_up, 0)
    except Exception as error:
        print(f"扫描码发送失败: {error}")
        return False
    if post_delay > 0:
        time.sleep(post_delay)
    return True


def clear_auto_indent(settle_delay: float = 0.04) -> bool:
    """清除自动缩进"""
    success = True
    shift_pressed = False
    try:
        win32api.keybd_event(VK_SHIFT, 0, 0, 0)
        shift_pressed = True
        time.sleep(0.01)
        if not send_scan_key(SCANCODE_HOME, extended=True, post_delay=0.015, hold_time=0.01):
            success = False
    except Exception:
        success = False
        if shift_pressed:
            try:
                win32api.keybd_event(VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            except Exception:
                pass
    if not send_scan_key(SCANCODE_DELETE, extended=True, post_delay=settle_delay, hold_time=0.01):
        success = False
    return success


def preprocess_text_content(text_content: str, ide_mode: bool) -> str:
    """预处理文本内容"""
    processed_text = text_content.replace('\r\n', '\n').replace('\r', '\n')
    if ide_mode:
        processed_text = processed_text.expandtabs(4)
    return processed_text


def execute_typing(text_content: str, speed_cps: int, countdown: int, jitter: int, 
                   send_enter: bool, auto_switch: bool, ide_mode: bool):
    """执行打字"""
    global status, original_input_method, target_window_handle, target_thread_id, current_active_layout
    
    try:
        # 倒计时阶段
        for remaining in range(countdown, 0, -1):
            if stop_event.is_set():
                return
            status['current_status'] = f'COUNTDOWN_{remaining}S'
            status['last_event'] = f'PREP_PHASE'
            time.sleep(1)

        if stop_event.is_set():
            return

        status['current_status'] = 'TYPING'
        status['last_event'] = 'INITIATED'

        # 预处理文本
        processed_text = preprocess_text_content(text_content, ide_mode)
        
        # 计算字符延时 - 直接使用字符/秒
        input_speed = max(1, speed_cps)  # 确保速度至少为1字符/秒
        character_delay = 1.0 / input_speed
        random_jitter = jitter / 100.0  # 将百分比转为小数
        
        total_characters = len(processed_text)
        typed_characters = 0
        status['total_chars'] = total_characters

        auto_switch_enabled = auto_switch
        ide_mode_enabled = ide_mode
        active_layout_type = None
        special_key_delay_val = special_key_delay if ide_mode_enabled else 0.0

        if auto_switch_enabled:
            target_window = win32gui.GetForegroundWindow()
            if target_window:
                set_target_window_context(target_window)

        if ide_mode_enabled:
            lines = processed_text.split('\n')
            total_lines = len(lines)
            trailing_newline = processed_text.endswith('\n')

            for line_index, line in enumerate(lines):
                if stop_event.is_set():
                    break

                if line_index > 0:
                    clear_auto_indent(settle_delay=0.04)

                for character in line:
                    if stop_event.is_set():
                        break

                    if auto_switch_enabled:
                        layout_type = classify_character_layout(character)
                        if layout_type and layout_type != active_layout_type:
                            ensure_input_layout(layout_type, auto_switch_enabled)
                            active_layout_type = layout_type

                    if character == "\t":
                        tab_delay = special_key_delay_val / 2 if special_key_delay_val > 0 else 0.0
                        if not send_scan_key(SCANCODE_TAB, post_delay=tab_delay):
                            send_special_key(VK_TAB, Key.tab, post_delay=tab_delay)
                    elif character == " ":
                        if not send_scan_key(SCANCODE_SPACE, post_delay=0.0, hold_time=0.01):
                            send_special_key(VK_SPACE, Key.space, post_delay=0.0, hold_time=0.01)
                    elif ord(character) < 32:
                        continue
                    else:
                        send_unicode_character(character)

                    typed_characters += 1
                    status['progress'] = typed_characters

                    # 计算实际延时（包含随机抖动）
                    actual_delay = character_delay
                    if random_jitter > 0.0:
                        actual_delay += random.uniform(-random_jitter, random_jitter)
                    actual_delay = max(0.001, actual_delay)
                    time.sleep(actual_delay)

                newline_needed = (
                    (line_index < total_lines - 1) or
                    (line_index == total_lines - 1 and trailing_newline)
                )

                if stop_event.is_set():
                    break

                if newline_needed:
                    if auto_switch_enabled:
                        ensure_input_layout("english", auto_switch_enabled)
                        active_layout_type = "english"
                    time.sleep(0.05)
                    if not send_scan_key(SCANCODE_ESCAPE, post_delay=0.05, hold_time=0.01):
                        send_special_key(VK_ESCAPE, Key.esc, post_delay=0.05, hold_time=0.01)
                    if not send_scan_key(SCANCODE_ENTER, post_delay=max(0.15, special_key_delay_val), hold_time=0.02):
                        send_special_key(VK_RETURN, Key.enter, post_delay=max(0.15, special_key_delay_val), hold_time=0.02)
                    typed_characters += 1
                    status['progress'] = typed_characters
                    
                    # 换行后的延时
                    actual_delay = max(character_delay, 0.01)
                    if random_jitter > 0.0:
                        actual_delay += random.uniform(-random_jitter, random_jitter / 2)
                    actual_delay = max(0.01, actual_delay)
                    time.sleep(actual_delay)
        else:
            for character in processed_text:
                if stop_event.is_set():
                    break

                if character == "\r":
                    continue

                if auto_switch_enabled:
                    layout_type = classify_character_layout(character)
                    if layout_type and layout_type != active_layout_type:
                        ensure_input_layout(layout_type, auto_switch_enabled)
                        active_layout_type = layout_type

                if character == "\n":
                    keyboard_controller.press(Key.enter)
                    keyboard_controller.release(Key.enter)
                elif character == "\t":
                    keyboard_controller.press(Key.tab)
                    keyboard_controller.release(Key.tab)
                elif character == " ":
                    keyboard_controller.press(Key.space)
                    keyboard_controller.release(Key.space)
                elif ord(character) < 32:
                    continue
                else:
                    keyboard_controller.type(character)

                typed_characters += 1
                status['progress'] = typed_characters

                # 计算实际延时（包含随机抖动）
                actual_delay = character_delay
                if random_jitter > 0.0:
                    actual_delay += random.uniform(-random_jitter, random_jitter)
                actual_delay = max(0.001, actual_delay)
                time.sleep(actual_delay)

        # 发送回车键
        if not stop_event.is_set() and send_enter:
            time.sleep(0.2)
            if ide_mode_enabled:
                if not send_scan_key(SCANCODE_ESCAPE, post_delay=0.05, hold_time=0.01):
                    send_special_key(VK_ESCAPE, Key.esc, post_delay=0.05, hold_time=0.01)
                if not send_scan_key(SCANCODE_ENTER, post_delay=max(0.15, special_key_delay), hold_time=0.02):
                    send_special_key(VK_RETURN, Key.enter, post_delay=max(0.15, special_key_delay), hold_time=0.02)
            else:
                keyboard_controller.press(Key.enter)
                keyboard_controller.release(Key.enter)

        if stop_event.is_set():
            status['current_status'] = 'ABORTED'
            status['last_event'] = 'USER_HALT'
        else:
            status['current_status'] = 'COMPLETED'
            status['last_event'] = 'MISSION_SUCCESS'

    except Exception as error:
        print(f"输入过程中发生错误: {error}")
        status['current_status'] = 'ERROR'
        status['last_event'] = f'ERROR_{str(error)[:20]}'
    finally:
        # 恢复原始输入法
        if auto_switch and original_input_method:
            try:
                if target_thread_id:
                    activate_layout_for_target(original_input_method)
                current_active_layout = original_input_method
            except Exception:
                pass
            original_input_method = None
            target_window_handle = None
            target_thread_id = None
            current_active_layout = None
        
        # 重置状态和清理线程引用
        status['is_typing'] = False
        global typing_thread
        typing_thread = None


@app.route('/api/start', methods=['POST'])
def start_typing():
    """开始打字"""
    global typing_thread, stop_event, status
    
    # 检查是否有活跃的输入线程
    if typing_thread and typing_thread.is_alive():
        return jsonify({'success': False, 'message': 'Already typing'}), 400
    
    # 如果上一个线程已完成，清理线程引用
    if typing_thread and not typing_thread.is_alive():
        typing_thread = None
    
    data = request.json
    text_content = data.get('text', '')
    speed_cps = int(data.get('speed', 5))  # 默认5字符/秒
    countdown = int(data.get('countdown', 3))
    jitter = int(data.get('jitter', 5))
    send_enter = data.get('sendEnter', True)
    auto_switch = data.get('autoSwitch', True)
    ide_mode = data.get('ideMode', False)
    
    if not text_content.strip():
        return jsonify({'success': False, 'message': 'No text provided'}), 400
    
    stop_event.clear()
    status = {
        'is_typing': True,
        'progress': 0,
        'total_chars': len(text_content),
        'current_status': 'PREPARING',
        'last_event': 'INIT_SEQ'
    }
    
    typing_thread = threading.Thread(
        target=execute_typing,
        args=(text_content, speed_cps, countdown, jitter, send_enter, auto_switch, ide_mode),
        daemon=True
    )
    typing_thread.start()
    
    return jsonify({'success': True, 'message': 'Typing started'})


@app.route('/api/stop', methods=['POST'])
def stop_typing():
    """停止打字"""
    global stop_event, status, typing_thread
    
    # 设置停止信号
    stop_event.set()
    
    # 等待线程结束（最多等待2秒）
    if typing_thread and typing_thread.is_alive():
        typing_thread.join(timeout=2.0)
        if typing_thread.is_alive():
            # 如果线程仍在运行，强制清理状态
            print("Warning: Typing thread did not stop gracefully")
    
    # 确保状态正确重置
    status.update({
        'is_typing': False,
        'current_status': 'ABORTED',
        'last_event': 'USER_HALT'
    })
    
    # 清理线程引用
    typing_thread = None
    
    return jsonify({'success': True, 'message': 'Stop signal sent and status reset'})


@app.route('/api/reset', methods=['POST'])
def reset_status():
    """重置状态为初始状态"""
    global status
    
    # 只有在非活动状态时才允许重置
    if status['current_status'] in ['COMPLETED', 'ABORTED', 'ERROR', 'IDLE']:
        status.update({
            'is_typing': False,
            'progress': 0,
            'total_chars': 0,
            'current_status': 'IDLE',
            'last_event': 'SYSTEM_READY'
        })
        return jsonify({'success': True, 'message': '状态已重置'})
    else:
        return jsonify({'success': False, 'message': '无法重置活动状态'}), 400


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取状态"""
    progress_percent = 0
    if status['total_chars'] > 0:
        progress_percent = int((status['progress'] / status['total_chars']) * 100)
    
    return jsonify({
        'is_typing': status['is_typing'],
        'progress': status['progress'],
        'total_chars': status['total_chars'],
        'progress_percent': progress_percent,
        'current_status': status['current_status'],
        'last_event': status['last_event']
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})


if __name__ == '__main__':
    print("Starting Keyboard Typer Backend Server...")
    print("Server running on http://localhost:5000")
    
    # 初始化输入法处理
    prepare_input_layout_handles()
    
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)