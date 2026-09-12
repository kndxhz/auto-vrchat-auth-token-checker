#!/usr/bin/env python3
"""
运行 npx vrchat-auth-token-checker -y，
自动从 .env 读取用户名 / 密码 / TOTP 密钥并按提示输入，
最终只输出形如 "Auth token: authcookie_xxx" 的一行。
"""

import os
import re
import sys
from pathlib import Path

import pexpect
import pyotp


def load_env(path: str = ".env") -> dict:
    env = {}
    p = Path(path)
    if not p.exists():
        print(f"[error] .env not found at {p.resolve()}", file=sys.stderr)
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

    missing = [
        n
        for n, v in (
            ("USERNAME", username),
            ("PASSWORD", password),
            ("TOTP/TOTP_SECRET", totp_secret),
        )
        if not v
    ]
    if missing:
        print(f"[error] missing in .env: {', '.join(missing)}", file=sys.stderr)
        return 1

    child = pexpect.spawn(
        "npx",
        ["-y", "vrchat-auth-token-checker"],
        encoding="utf-8",
        timeout=180,
    )
    # 把子进程输出放到 stderr，避免污染 stdout（stdout 只允许输出最终一行）
    child.logfile_read = sys.stderr

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
            else:  # EOF 或 TIMEOUT
                break
    except pexpect.ExceptionPexpect as e:
        print(f"[error] {e}", file=sys.stderr)
    finally:
        try:
            child.close(force=True)
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
