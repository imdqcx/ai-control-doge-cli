# 贡献指南 (Contributing Guide)

## Git 提交规范

本项目遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 提交格式

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### 类型 (type)

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(capture): 添加多显示器截图支持` |
| `fix` | 修复bug | `fix(input): 修复鼠标拖拽坐标偏移问题` |
| `docs` | 文档更新 | `docs(readme): 更新API接口说明` |
| `style` | 代码格式（不影响功能） | `style: 格式化代码缩进` |
| `refactor` | 重构（非新功能非修复） | `refactor(server): 重构路由注册逻辑` |
| `perf` | 性能优化 | `perf(capture): 优化截图压缩算法` |
| `test` | 测试相关 | `test(api): 添加健康检查单元测试` |
| `build` | 构建系统或外部依赖 | `build: 更新pyinstaller配置` |
| `ci` | CI配置 | `ci: 添加GitHub Actions工作流` |
| `chore` | 其他杂项 | `chore: 更新.gitignore` |
| `revert` | 回滚 | `revert: 回滚feat(capture)提交` |

### 范围 (scope)

可选，用于说明影响范围：

| 范围 | 说明 |
|------|------|
| `capture` | 屏幕截图模块 |
| `input` | 输入模拟模块 |
| `clipboard` | 剪贴板模块 |
| `server` | HTTP服务器模块 |
| `tray` | 系统托盘模块 |
| `config` | 配置管理模块 |
| `ui` | 设置界面模块 |
| `api` | API接口 |
| `deps` | 依赖管理 |
| `release` | 版本发布 |

### 主题 (subject)

- 简短描述，不超过50个字符
- 使用中文或英文（建议统一）
- 不以大写字母开头
- 不以句号结尾

### 示例

```bash
# 简单提交
git commit -m "feat: 添加剪贴板读写功能"

# 带范围
git commit -m "fix(input): 修复键盘输入中文乱码问题"

# 带详细说明
git commit -m "feat(capture): 添加区域截图功能

- 支持指定坐标和尺寸
- 支持多显示器选择
- 添加参数验证

Closes #123"

# 重大变更（BREAKING CHANGE）
git commit -m "feat(api)!: 重构截图API响应格式

BREAKING CHANGE: 截图API返回格式变更，不再返回base64，改为二进制流"
```

---

## 分支管理

| 分支 | 用途 |
|------|------|
| `main` | 主分支，稳定版本 |
| `develop` | 开发分支 |
| `feat/*` | 功能分支 |
| `fix/*` | 修复分支 |
| `release/*` | 发布分支 |

### 分支命名

```bash
# 功能分支
git checkout -b feat/clipboard-support

# 修复分支
git checkout -b fix/mouse-offset

# 发布分支
git checkout -b release/v1.1.0
```

---

## 开发流程

1. 从 `develop` 创建功能分支
2. 在功能分支上开发
3. 提交代码（遵循提交规范）
4. 创建 Pull Request
5. 代码审查
6. 合并到 `develop`
7. 测试通过后合并到 `main`

---

## 版本号规范

遵循 [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH

MAJOR: 不兼容的API变更
MINOR: 向后兼容的功能新增
PATCH: 向后兼容的问题修复
```

示例：`1.0.0` → `1.1.0` → `1.1.1` → `2.0.0`

---

## 代码规范

- 使用类型注解
- 遵循 PEP 8 规范
- 编写文档字符串
- 保持函数简洁

---

*文档版本: v1.0*  
*创建日期: 2026-06-19*