"""模拟 AI 服务，用于分析电器操作并给出建议。"""

import random


def analyze_appliance_action(appliance_name: str, action: str, power: float) -> str:
    """模拟 AI 分析用户的操作并给出建议。

    Args:
        appliance_name: 电器名称
        action: 操作类型 ("ON" 或 "OFF")
        power: 电器功率 (kW)

    Returns:
        AI 给出的建议消息
    """
    if action == "OFF":
        return f"已关闭 {appliance_name}。做得好！这将为您每小时节省 {power:.2f} 度电。"

    # 如果是开启操作，随机给出一些建议
    tips = [
        f"检测到当前处于用电高峰期，{appliance_name} 功率较大 ({power}kW)，建议适当缩短使用时间哦。",
        f"{appliance_name} 已开启。今天天气凉爽，或许开窗通风也是个不错的选择？",
        f"已为您开启 {appliance_name}。记得出门前检查是否关闭以避免浪费。",
        "AI 提示：当前家庭总负荷正常，请放心使用。",
        f"{appliance_name} 已启动。建议设置合适的温度/亮度以平衡舒适度和节能。",
    ]

    return random.choice(tips)

