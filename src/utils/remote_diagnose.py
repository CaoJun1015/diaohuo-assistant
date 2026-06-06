"""
远程诊断助手 (Remote Diagnose Assistant)

结构化的故障排查决策树，帮助经销商远程引导客户解决问题。

设计原则：
- 不是 AI 自由发挥，而是结构化的排查流程
- 每一步有明确的操作指引和分支
- 记录排查过程，可作为售后凭证
"""

DIAGNOSE_TREE = {
    "蓝屏": {
        "title": "蓝屏（Blue Screen）排查",
        "steps": [
            {
                "q": "蓝屏上有没有显示错误代码？（如 IRQL_NOT_LESS_OR_EQUAL、KERNEL_SECURITY_CHECK_FAILURE 等）",
                "options": {
                    "有错误代码": {
                        "action": "记录错误代码，搜索对应解决方案。常见代码：\n"
                                 "• IRQL_NOT_LESS_OR_EQUAL → 驱动冲突，进安全模式卸载最近安装的驱动\n"
                                 "• KERNEL_SECURITY_CHECK_FAILURE → 系统文件损坏，运行 sfc /scannow\n"
                                 "• CRITICAL_PROCESS_DIED → 关键进程崩溃，尝试系统还原\n"
                                 "• PAGE_FAULT_IN_NONPAGED_AREA → 内存问题，检查内存条",
                        "resolved": True,
                    },
                    "没有/看不清": {"next": 1},
                },
            },
            {
                "q": "蓝屏是在什么情况下出现的？",
                "options": {
                    "开机就蓝屏": {
                        "action": "系统引导文件可能损坏。\n"
                                 "1. 重启电脑，反复按 F8（Win10/11 按住 Shift 点重启）\n"
                                 "2. 选择「安全模式」\n"
                                 "3. 能进安全模式 → 运行 sfc /scannow，或使用系统还原\n"
                                 "4. 安全模式也蓝屏 → 硬件问题概率大，建议送修",
                        "resolved": True,
                    },
                    "使用中突然蓝屏": {
                        "action": "可能是驱动或软件冲突。\n"
                                 "1. 想一下蓝屏前在做什么操作\n"
                                 "2. 最近是否安装了新软件或更新驱动\n"
                                 "3. 进安全模式，卸载最近安装的软件/驱动\n"
                                 "4. 运行 Windows 更新，确保系统补丁最新",
                        "resolved": True,
                    },
                    "玩游戏/高负载时蓝屏": {
                        "action": "可能是显卡驱动或散热问题。\n"
                                 "1. 更新显卡驱动到最新版本\n"
                                 "2. 检查散热：清理风扇灰尘，确保出风口畅通\n"
                                 "3. 用鲁大师/AIDA64 跑温度监控，CPU/GPU 超过 90°C 需要处理散热\n"
                                 "4. 如果是新买的机器，可能是显卡硬件问题，建议送修",
                        "resolved": True,
                    },
                    "不确定": {
                        "action": "建议先观察复现条件。\n"
                                 "1. 记录蓝屏错误代码（拍照）\n"
                                 "2. 尝试进入安全模式排查\n"
                                 "3. 如果反复蓝屏，建议送修",
                        "resolved": True,
                    },
                },
            },
        ],
    },
    "开不了机": {
        "title": "开不了机排查",
        "steps": [
            {
                "q": "按电源键后，机器有什么反应？",
                "options": {
                    "完全没反应（指示灯不亮、风扇不转）": {
                        "action": "电源问题。\n"
                                 "1. 检查电源适配器是否插好，换一个插座试试\n"
                                 "2. 如果是笔记本，长按电源键 15 秒放电，再重新开机\n"
                                 "3. 检查电源适配器指示灯是否亮\n"
                                 "4. 以上都不行 → 可能是电源适配器或主板问题，建议送修",
                        "resolved": True,
                    },
                    "指示灯亮但屏幕不亮": {
                        "action": "可能是屏幕或显卡问题。\n"
                                 "1. 外接一台显示器试试（笔记本用 HDMI 接口）\n"
                                 "2. 外接显示器有画面 → 笔记本屏幕或排线问题\n"
                                 "3. 外接也没画面 → 显卡或内存问题\n"
                                 "4. 尝试拔掉电源，长按电源键 15 秒，重新开机",
                        "resolved": True,
                    },
                    "卡在品牌 Logo 界面": {
                        "action": "系统引导问题。\n"
                                 "1. 等待 5 分钟，看是否能自行进入系统\n"
                                 "2. 不行的话，强制关机（长按电源键），再开机\n"
                                 "3. 反复按 F2/Del 进 BIOS，检查硬盘是否被识别\n"
                                 "4. BIOS 里能看到硬盘 → 系统引导损坏，需要 PE 修复\n"
                                 "5. BIOS 里看不到硬盘 → 硬盘可能坏了",
                        "resolved": True,
                    },
                    "反复重启": {
                        "action": "系统或硬件不稳定。\n"
                                 "1. 开机时按 F8 进安全模式\n"
                                 "2. 安全模式不重启 → 驱动或软件问题，卸载最近安装的东西\n"
                                 "3. 安全模式也重启 → 硬件问题（内存/硬盘）\n"
                                 "4. 建议送修检测",
                        "resolved": True,
                    },
                },
            },
        ],
    },
    "WiFi断连": {
        "title": "WiFi 断连/连不上排查",
        "steps": [
            {
                "q": "WiFi 是连不上，还是连上了但经常断？",
                "options": {
                    "连不上WiFi": {
                        "action": "1. 确认 WiFi 开关是否打开（Fn+F5 或侧边物理开关）\n"
                                 "2. 重启路由器和电脑\n"
                                 "3. 进设备管理器 → 网络适配器，看无线网卡是否正常\n"
                                 "4. 无线网卡有黄色感叹号 → 右键卸载驱动，重启自动重装\n"
                                 "5. 设备管理器里看不到无线网卡 → 硬件故障",
                        "resolved": True,
                    },
                    "连上了但经常断": {
                        "action": "1. 更新无线网卡驱动（去品牌官网下载）\n"
                                 "2. WiFi 设置 → 电源管理 → 取消「允许计算机关闭此设备以节省电源」\n"
                                 "3. 尝试切换 2.4G/5G 频段\n"
                                 "4. 如果只在家里断 → 路由器问题，重启路由器\n"
                                 "5. 哪里都断 → 网卡硬件问题",
                        "resolved": True,
                    },
                    "网速很慢": {
                        "action": "1. 测速（speedtest.cn），对比其他设备\n"
                                 "2. 只有这台慢 → 更新网卡驱动\n"
                                 "3. 所有设备都慢 → 路由器或宽带问题\n"
                                 "4. 连 5G WiFi 测试，2.4G 容易受干扰",
                        "resolved": True,
                    },
                },
            },
        ],
    },
    "风扇噪音大": {
        "title": "风扇噪音大排查",
        "steps": [
            {
                "q": "风扇是一直响还是特定情况下才响？",
                "options": {
                    "一直很响": {
                        "action": "1. 检查 CPU 占用率（任务管理器），是否有程序占用过高\n"
                                 "2. 清理风扇灰尘（用吹风机冷风吹出风口）\n"
                                 "3. 检查散热模式：Lenovo Vantage 里切换到安静模式\n"
                                 "4. 如果是新机器就很响 → 可能风扇硬件问题",
                        "resolved": True,
                    },
                    "玩游戏/高负载时响": {
                        "action": "正常现象。高负载时风扇加速是正常的。\n"
                                 "如果觉得太响：\n"
                                 "1. 在 Lenovo Vantage 里切换到安静模式\n"
                                 "2. 降低游戏画质设置\n"
                                 "3. 使用散热底座",
                        "resolved": True,
                    },
                    "开机没多久就响": {
                        "action": "可能是后台程序占用 CPU。\n"
                                 "1. 打开任务管理器，看 CPU 占用率\n"
                                 "2. 结束不需要的后台程序\n"
                                 "3. 检查是否有 Windows 更新在后台运行",
                        "resolved": True,
                    },
                },
            },
        ],
    },
}


def search_diagnose(keyword):
    """
    根据关键词搜索匹配的诊断流程。

    参数:
        keyword: str — 症状关键词

    返回:
        list[dict] — 匹配的诊断项 [{key, title, match_type}]
    """
    keyword = keyword.strip().lower()
    results = []

    for key, tree in DIAGNOSE_TREE.items():
        title = tree["title"].lower()
        if keyword in key.lower() or keyword in title:
            results.append({"key": key, "title": tree["title"], "match_type": "标题匹配"})
        elif any(keyword in opt.lower() for step in tree["steps"] for opt in step["options"]):
            results.append({"key": key, "title": tree["title"], "match_type": "选项匹配"})

    return results


def get_diagnose_tree(key):
    """
    获取指定诊断流程。

    参数:
        key: str — 诊断项的 key（如 "蓝屏"）

    返回:
        dict — 诊断树，或 None
    """
    return DIAGNOSE_TREE.get(key)


def get_all_diagnose_keys():
    """返回所有可用的诊断项。"""
    return [{"key": k, "title": v["title"]} for k, v in DIAGNOSE_TREE.items()]


def generate_diagnose_report(key, selected_options, custom_notes=""):
    """
    生成诊断报告文本。

    参数:
        key: str — 诊断项 key
        selected_options: list[str] — 用户选择的路径
        custom_notes: str — 自定义备注

    返回:
        str — 格式化的诊断报告
    """
    tree = DIAGNOSE_TREE.get(key)
    if not tree:
        return "未知诊断项"

    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    parts = []
    parts.append("=" * 36)
    parts.append("        远程诊断报告")
    parts.append("=" * 36)
    parts.append(f"日期: {now}")
    parts.append(f"故障类型: {tree['title']}")
    parts.append("")
    parts.append("排查路径:")
    for i, opt in enumerate(selected_options, 1):
        parts.append(f"  {i}. {opt}")

    # 找到对应的解决方案
    for step in tree["steps"]:
        for opt_name, opt_data in step["options"].items():
            if opt_name in selected_options:
                if "action" in opt_data:
                    parts.append("")
                    parts.append("处理方案:")
                    parts.append(opt_data["action"])

    if custom_notes:
        parts.append("")
        parts.append(f"备注: {custom_notes}")

    parts.append("")
    parts.append("=" * 36)
    return "\n".join(parts)
