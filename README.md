# VRChat Auth Token 自动获取脚本

通过 `npx vrchat-auth-token-checker -y` 自动完成 VRChat 登录并获取 Auth Token，最终**只在标准输出打印一行**：

```
Auth token: authcookie_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

其余所有日志、提示和错误信息均输出到标准错误（stderr），方便在 shell 脚本或 CI 中直接捕获 stdout 获取 token。

## 环境要求

- Python 3.9+
- [uv](https://github.com/astral-sh/uv)（Python 包管理器）
- Node.js（提供 `npx` 命令）

## 安装

1. 克隆仓库并进入项目目录。
2. 使用 uv 安装依赖：

   ```bash
   uv sync
   ```

   如果尚未初始化项目，可执行：

   ```bash
   uv init
   uv add pexpect pyotp
   ```

## 配置

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

然后编辑 `.env`，填入你的 VRChat 账号信息。`.env.example` 内容如下：

```env
USERNAME=your_vrchat_username
PASSWORD=your_vrchat_password
TOTP=JBSWY3DPEHPK3PXP
```

- `USERNAME`：VRChat 用户名
- `PASSWORD`：VRChat 密码
- `TOTP`：TOTP 密钥（Base32 格式），用于生成动态验证码。如果账号启用了 2FA，必须填写。

> **安全提示**：`.env` 包含敏感信息，请勿提交到版本控制系统。建议将 `.env` 加入 `.gitignore`。

## 运行

```bash
uv run python main.py
```

或者：

```bash
uv run main.py
```

脚本会自动执行以下流程：

1. 启动 `npx vrchat-auth-token-checker -y`
2. 当出现 `VRChat Username:` 时，自动输入 `.env` 中的 `USERNAME`
3. 当出现 `VRChat Password:` 时，自动输入 `.env` 中的 `PASSWORD`
4. 当出现 `TOTP Code:` 时，使用 `pyotp` 根据 `TOTP` 密钥生成当前验证码并输入
5. 捕获 `Auth token: authcookie_...` 并在 stdout 输出该行

## 输出示例

stdout（仅此一行）：

```
Auth token: authcookie_202d7e0f-b159-4a47-a689-2b660482b87f
```

stderr（示例，不会污染 stdout）：

```
npx: installed 1 in 2.3s
VRChat Username: ...
VRChat Password: ...
TOTP Code: ...
Auth token: authcookie_202d7e0f-b159-4a47-a689-2b660482b87f
```

## 项目结构

```
.
├── .env.example
├── .gitignore
├── main.py
├── pyproject.toml
└── README.md
```

## 注意事项

- 本脚本仅用于个人自动化获取 VRChat Auth Token，请妥善保管 `.env` 文件。
- 需要确保本机已安装 Node.js，并且 `npx` 命令可用。
- 脚本使用 `-y` 参数自动确认 npx 安装，无需手动干预。
- 如果 `vrchat-auth-token-checker` 包有更新，脚本会自动使用最新版本。