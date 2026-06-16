#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄汁血管年轻 - 配图生成脚本
论文原图（image1首页 + image3折线图）已手动复制，本脚本只生成 AI 概念图
"""
import os
import json
import time
import requests
from pathlib import Path

API_BASE = "https://api.wuyinkeji.com"
SUBMIT_URL = f"{API_BASE}/api/async/image_gpt"
DETAIL_URL = f"{API_BASE}/api/async/detail"
API_KEY = os.environ.get("SUCHUANG_API_KEY", "zgkElfxREIv5SkWZBc5yNZ9YmR")

OUTPUT_DIR = Path(__file__).parent / "blog-images" / "番茄汁血管年轻"

# image_gpt 接口不支持 aspectRatio 参数；用 prompt 描述比例
ASPECT_DESC = {
    "21:9": "超宽横幅 21:9 宽屏",
    "16:9": "16:9 横向构图",
    "1:1": "正方形 1:1",
}

IMAGES = [
    {
        "name": "00-cover.png",
        "prompt": "微信公众号封面图，超宽横幅 21:9 宽屏。画面中央是一杯鲜红透亮的番茄汁，番茄汁从上方缓缓倒入玻璃杯中，溅起优美的水花。背景是深蓝色到暗红色的渐变，隐约可见人体血管和心脏的剪影轮廓。整体风格医学期刊封面感，高级、专业、温暖。底部留白区域用醒目的中文学术风文字写着主题：「每天一杯番茄汁，血管真的会变年轻吗？」，下方副标题「《Food & Function》给出答案」。",
    },
    {
        "name": "01-fmd-concept.png",
        "prompt": "16:9 横向构图。医学概念示意图：展示FMD（血流介导的血管舒张功能）的检测原理。画面左侧是一个手臂截面，上臂绑着血压袖带（蓝色），袖带下方是一段肱动脉的放大示意。画面右侧用箭头分三步展示：第一步袖带充气阻断血流（血管变细），第二步袖带释放血流恢复（血管充血），第三步血管最大扩张（血管变粗）。配色调用医学蓝 #1a5276 主色 + 暖金 #c9a961 强调。插画风格，清晰、专业、易懂。",
    },
    {
        "name": "02-study-design.png",
        "prompt": "16:9 横向构图。临床试验分组流程图：75名健康成年人（FMD 4%-7%）在最顶部，向下分出三条分支箭头，分别指向三个组别。左侧是「安慰剂组」用灰色方块表示，中间是「普通番茄汁组(TJ)」用橙色方块，右侧是「高浓度番茄汁组(HLTJ)」用深红色方块。每个组下方标注「12周」。底部是一条时间轴标注「第0周→第4周→第8周→第12周」四个检测节点。配色医学蓝 #1a5276 主色 + 暖金 #c9a961 强调。扁平化设计，清晰专业。",
    },
    {
        "name": "03-mechanism.png",
        "prompt": "16:9 横向构图。番茄红素保护血管的双通路机制示意图。画面中央是一个红色番茄红素分子（圆形带多个延伸键）。左上方通路标注「通路一：清除自由基」，画面展示番茄红素（红色盾牌）拦截超氧阴离子（蓝色闪电），防止LDL被氧化成氧化型LDL（用油垢黏附血管壁的负面意象）。右下方通路标注「通路二：激活舒张开关」，画面展示番茄红素激活eNOS酶，释放一氧化氮NO（绿色小分子），让血管平滑肌舒张。配色医学蓝 #1a5276 + 番茄红 + 暖金。科学插画风格。",
    },
    {
        "name": "04-daily-guide.png",
        "prompt": "16:9 横向构图。日常摄入番茄红素的四个建议图标四宫格。左上格：5-30mg数字+一个番茄图标，标注「每日摄入量」。右上格：一口锅冒着热气+番茄，标注「加热更吸收」。左下格：一瓶橄榄油+番茄+鸡蛋，标注「搭配油脂」。右下格：日历翻页4周12周标注，标注「长期坚持」。整体配色米白底 #f5f0e6 + 番茄红 + 暖金点缀。扁平化图标风格，温馨生活感。",
    },
    {
        "name": "05-lycopene-food.png",
        "prompt": "16:9 横向构图。富含番茄红素的食物集合展示。画面中央一个大番茄，周围环绕西瓜（红色切片）、番石榴（粉色）、葡萄柚（粉色）、胡萝卜、南瓜等。每种食物下方标注名称。背景米白色 #f5f0e6，食物色彩鲜艳自然，摄影棚打光，高级食物摄影质感。",
    },
]


def submit_with_retry(prompt: str, aspect_ratio: str = "16:9", max_retry: int = 5) -> str:
    aspect = ASPECT_DESC.get(aspect_ratio, aspect_ratio)
    full_prompt = f"{prompt}，{aspect}。"
    payload = {"prompt": full_prompt, "size": "2K"}

    for attempt in range(max_retry):
        try:
            resp = requests.post(
                SUBMIT_URL,
                json=payload,
                headers={"Authorization": API_KEY, "Content-Type": "application/json"},
                timeout=60,
            )
            data = resp.json()
            if data.get("code") == 200 and data.get("data", {}).get("id"):
                return data["data"]["id"]
            print(f"  [提交失败 {attempt+1}] {data.get('msg', data)}")
        except Exception as e:
            print(f"  [提交异常 {attempt+1}] {e}")
        time.sleep(3)
    return ""


def poll_result(task_id: str, timeout: int = 300) -> str:
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(
                DETAIL_URL,
                params={"id": task_id},
                headers={"Authorization": API_KEY},
                timeout=30,
            )
            data = resp.json()
            d = data.get("data", {})
            status = d.get("status", "")
            # API 实际返回：status=2 成功，status=4 失败，status=1 处理中
            if status in (2, "2", "SUCCESS", "success"):
                result = d.get("result", [])
                if result and isinstance(result, list):
                    return result[0]
                url = d.get("resultUrl") or d.get("url", "")
                if url:
                    return url
            elif status in (4, "4", "FAIL", "fail"):
                print(f"  [生成失败] status={status}")
                return ""
        except Exception as e:
            print(f"  [轮询异常] {e}")
        time.sleep(6)
    return ""


def download(url: str, filepath: Path):
    resp = requests.get(url, timeout=120)
    filepath.write_bytes(resp.content)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"待生成: {len(IMAGES)} 张 AI 概念图\n")

    for i, img in enumerate(IMAGES, 1):
        filepath = OUTPUT_DIR / img["name"]
        if filepath.exists():
            print(f"[{i}/{len(IMAGES)}] {img['name']} 已存在，跳过")
            continue

        aspect = "21:9" if "cover" in img["name"] else "16:9"
        print(f"[{i}/{len(IMAGES)}] 提交: {img['name']} ({aspect})")
        task_id = submit_with_retry(img["prompt"], aspect)
        if not task_id:
            print(f"  ❌ 提交失败，跳过")
            continue

        print(f"  轮询中... (task_id={task_id})")
        url = poll_result(task_id)
        if not url:
            print(f"  ❌ 生成超时/失败")
            continue

        download(url, filepath)
        print(f"  ✅ 完成: {filepath.name}")


if __name__ == "__main__":
    main()
