#!/usr/bin/env python3
"""
运行 npx -y vrchat-auth-token-checker -y，
自动从 .env 读取用户名 / 密码 / TOTP 密钥并按提示输入，
最终只输出形如 "Auth token: authcookie_xxx" 的一行。
所有子进程输出、诊断信息都被丢弃，stdout / stderr 保持干净。
"""

import os
import sys
from pathlib import Path

import pexpect
import pyotp


def load_env(path: str = ".env") -> dict:
    env = {}
    p = Path(path)
    if not p.exists():
        return env
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        env[k] = v
    return env


def main() -> int:
    env = load_env()

    username = env.get("USERNAME")
    password = env.get("PASSWORD")
    totp_secret = env.get("TOTP") or env.get("TOTP_SECRET") or env.get("TOTP_CODE")

    if not (username and password and totp_secret):
        return 1

    # 让 npm / npx 自动确认安装
    npm_env = os.environ.copy()
    npm_env["npm_config_yes"] = "true"

    # 把子进程的所有输出丢到 /dev/null
    devnull = open(os.devnull, "w")

    child = pexpect.spawn(
        "npx",
        ["-y", "vrchat-auth-token-checker"],
        encoding="utf-8",
        timeout=180,
        env=npm_env,
    )
    child.logfile_read = devnull  # 不打印任何子进程输出
    child.logfile_send = devnull  # 也不回显我们发送的内容

    auth_token = None

    patterns = [
        r"VRChat Username:\s*",
        r"VRChat Password:\s*",
        r"TOTP Code:\s*",
        r"Auth token:\s*(authcookie_[A-Za-z0-9\-]+)",
        pexpect.EOF,
        pexpect.TIMEOUT,
    ]

    try:
        while True:
            idx = child.expect(patterns)
            if idx == 0:
                child.sendline(username)
            elif idx == 1:
                child.sendline(password)
            elif idx == 2:
                child.sendline(pyotp.TOTP(totp_secret).now())
            elif idx == 3:
                auth_token = child.match.group(1)
                break
            else:  # EOF / TIMEOUT
                break
    except pexpect.ExceptionPexpect:
        pass
    finally:
        try:
            child.close(force=True)
        except Exception:
            pass
        try:
            devnull.close()
        except Exception:
            pass

    if auth_token:
        # 唯一允许输出的内容
        sys.stdout.write(f"Auth token: {auth_token}\n")
        sys.stdout.flush()
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
