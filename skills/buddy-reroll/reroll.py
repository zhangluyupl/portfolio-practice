#!/usr/bin/env python3
"""Buddy Reroll Skill - 清理 Claude Code companion"""

import json
import os
import sys
import webbrowser

CLAUDE_JSON = os.path.expanduser("~/.claude.json")

def get_current():
    """读取当前状态"""
    if not os.path.exists(CLAUDE_JSON):
        return None
    with open(CLAUDE_JSON) as f:
        data = json.load(f)
    return data.get("companion"), data.get("userID")

def clear_companion():
    """清除 companion"""
    if not os.path.exists(CLAUDE_JSON):
        print("~/.claude.json 不存在")
        return False
    with open(CLAUDE_JSON) as f:
        data = json.load(f)
    if "companion" in data:
        del data["companion"]
        with open(CLAUDE_JSON, "w") as f:
            json.dump(data, f, indent=2)
        print("✅ companion 已清除")
        return True
    else:
        print("ℹ️ 没有 companion")
        return True

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "clear":
        companion, userID = get_current()
        if companion:
            print(f"当前: {companion.get('name', 'unknown')}")
        clear_companion()

    elif cmd == "status":
        companion, userID = get_current()
        if companion:
            print(f"当前 buddy: {companion.get('name', 'unknown')}")
            print(f"稀有度: {companion.get('rarity', 'unknown')}")
            print(f"物种: {companion.get('species', 'unknown')}")
        else:
            print("还没有 buddy")
        if userID:
            print(f"userID: {userID[:16]}...")

    elif cmd == "open":
        print(f"打开 {CLAUDE_JSON} ...")
        #  macOS
        os.system(f"open -t {CLAUDE_JSON}")

    else:
        print("用法: buddy-reroll clear|status|open")

if __name__ == "__main__":
    main()
