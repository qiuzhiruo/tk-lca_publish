# -*- coding: utf-8 -*-
"""
# Author: tanghaojia
# Time: 2026-01-23 13:38:18
# Desc: 在原wav的基础上增加采样点，让rv识别得到正确的帧数
        已经给OpenRv PR 已经给OpenRv内部计算帧数的bug，官方同意了merge,内部暂时用不上，只能采取修改wav长度绕开
        src/lib/image/MovieFFMpeg/MovieFFMpeg.cpp
"""

import struct
import os
import wave
import contextlib
import subprocess
import json

FFPROBE_PATH = '/mnt/utility/dev/linux/ffmpeg-linux64-static/ffprobe'
FFMPEG_PATH = '/mnt/utility/dev/linux/ffmpeg-linux64-static/ffmpeg'


def get_audio_info(file_path):
    """使用 ffprobe 获取音频时长和采样信息"""
    cmd = [
        FFPROBE_PATH, '-v', 'quiet', '-print_format', 'json',
        '-show_entries', 'stream=duration,sample_rate,nb_samples,codec_name,sample_fmt',
        file_path
    ]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()

        if process.returncode != 0:
            return None

        data = json.loads(out)
        # 有些wav可能没有streams信息，做个简单防护
        if 'streams' in data and len(data['streams']) > 0:
            return data['streams'][0]
        return None
    except Exception as e:
        print u"读取信息出错: {}".format(e)
        return None


def check_rv_risk(file_path, fps=24.0):
    """检测是否存在 RV 识别丢帧风险，模拟openrv bug逻辑

    返回:
        tuple: (is_risk, msg, expected_frames, rv_frames)
            - is_risk: bool, 是否存在风险
            - msg: unicode, 描述信息
            - expected_frames: int, 理论帧数
            - rv_frames: int, RV 识别的帧数
    """
    info = get_audio_info(file_path)
    if not info:
        return False, u"无法读取文件信息或文件损坏", 0, 0

    try:
        duration = float(info.get('duration', 0))
    except (ValueError, TypeError):
        return False, u"无法获取有效的时长信息", 0, 0

    # 模拟 RV 的逻辑
    calc_frames = duration * fps
    truncated_frames = int(calc_frames)

    # 我们期望的帧数（四舍五入）
    expected_frames = int(calc_frames + 0.5)

    if truncated_frames < expected_frames:
        diff = expected_frames - calc_frames
        msg = u"存在风险：理论 {} 帧，RV 将识别为 {} 帧 (差距: {:.6f})".format(
            expected_frames, truncated_frames, diff
        )
        return True, msg, expected_frames, truncated_frames

    msg = u"安全：RV 识别为 {} 帧".format(truncated_frames)
    return False, msg, expected_frames, truncated_frames


def getDuration(filename, fps=24.0):
    '''
    Get duration/length in frames from an audio file (*.wav)
    '''
    duration = None
    with contextlib.closing(wave.open(filename, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate) * fps

    return int(round(duration))


def path_change_chmod(path):
    """
    解路径权限
    """
    cmd = 'su -'
    root_cmd = '''chmod 777 -R %s''' % path
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.stdin.write('20150312')
    p.stdin.write('\n')
    out, err = p.communicate(root_cmd)
    if err is None:
        # print('change chmod ok')
        return True
    else:
        # print ('change chmod error')
        return False


def add_wave_length(input_file, output_file, extra_samples=1):
    """
    读取 WAV 文件，增加少量采样点以修正时长，并保留所有原始元数据。
    Python 2 兼容版本。
    """

    with open(input_file, 'rb') as f:
        data = bytearray(f.read())

    file_len = len(data)

    # 检查 RIFF/WAVE 头部
    if data[0:4] != b'RIFF' or data[8:12] != b'WAVE':
        raise ValueError("Not a valid WAV file")

    # 提取原始 RIFF 大小
    orig_riff_size = struct.unpack('<I', bytes(data[4:8]))[0]

    # 查找 fmt 和 data 块的位置
    pos = 12
    data_pos = -1
    fmt_pos = -1

    while pos + 8 <= file_len:
        chunk_id = bytes(data[pos:pos + 4])
        chunk_size = struct.unpack('<I', bytes(data[pos + 4:pos + 8]))[0]

        if chunk_id == b'fmt ':
            fmt_pos = pos
        elif chunk_id == b'data':
            data_pos = pos
            break

        pos += 8 + chunk_size
        if chunk_size % 2 != 0:
            pos += 1

    if data_pos == -1 or fmt_pos == -1:
        raise ValueError("Could not find fmt or data chunk")

    # 从 fmt 块获取采样参数
    fmt_block_size = struct.unpack('<I', bytes(data[fmt_pos + 4:fmt_pos + 8]))[0]
    fmt_data = data[fmt_pos + 8: fmt_pos + 8 + fmt_block_size]
    fmt_code, channels, rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH', bytes(fmt_data[:16]))

    # 计算需要增加的字节数
    bytes_per_sample_frame = channels * (bits_per_sample // 8)
    padding_bytes = extra_samples * bytes_per_sample_frame

    # 原始数据大小
    orig_data_size = struct.unpack('<I', bytes(data[data_pos + 4:data_pos + 8]))[0]
    new_data_size = orig_data_size + padding_bytes

    # 1. 更新 RIFF 大小 (文件头部 [4:8])
    new_riff_size = orig_riff_size + padding_bytes
    data[4:8] = struct.pack('<I', new_riff_size)

    # 2. 更新 data 块大小 ([data_pos+4 : data_pos+8])
    data[data_pos + 4: data_pos + 8] = struct.pack('<I', new_data_size)

    # 3. 在数据块末尾插入静音采样
    insertion_point = data_pos + 8 + orig_data_size
    padding = b'\x00' * padding_bytes

    final_data = bytes(data[:insertion_point]) + padding + bytes(data[insertion_point:])

    # 验证时长一致性
    # 先写一个临时文件来检查
    temp_fix = output_file + ".tmp"
    with open(temp_fix, 'wb') as f:
        f.write(final_data)

    dur_orig = getDuration(input_file)
    dur_fixed = getDuration(temp_fix)

    if dur_orig != dur_fixed:
        os.remove(temp_fix)
        raise ValueError("时长匹配不一致性 原始: %d, 修复后: %d，将自动删除修复后的文件" % (dur_orig, dur_fixed))

    if os.path.exists(output_file):
        os.remove(output_file)
    os.rename(temp_fix, output_file)


if __name__ == "__main__":
    add_wave_length("/home/haojia/Work/r/m20480.wav", "/home/haojia/Work/r/m20480_ttttt.wav")

