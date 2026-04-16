# 劳务狗狗幻灯片

劳务狗狗产品介绍幻灯片，基于 HTML-PPT 构建系统生成。

## 项目结构

```
labourdog-slideshow/
├── .github/workflows/deploy.yml  # GitHub Actions 自动构建部署
├── build.py                      # 构建脚本
├── _config.yaml                  # 全局配置
├── slides/                       # 18个幻灯片 YAML
├── logo.png                      # 品牌标识
└── index.html                    # 由 CI 自动构建生成
```

## 本地构建

```bash
# 安装依赖
pip install pyyaml jinja2

# 构建幻灯片
python3 build.py --slides slides --output index.html --theme clean

# 输出文件: index.html
```

## 幻灯片列表

| 文件 | 布局 | 描述 |
|------|------|------|
| s01-hero.yaml | hero | 主标题 |
| s02-problem.yaml | problem | 问题陈述 |
| s03-pain.yaml | pain | 痛点分析 |
| s04-debut.yaml | debut | 产品定位 |
| s05-definition.yaml | definition | 核心概念 |
| s06-model.yaml | model | 输入模型 |
| s07-spage.yaml | spage | S页面 |
| s08-import.yaml | import | 导入功能 |
| s09-d1.yaml | d1 | 钉钉录入D1 |
| s10-d2.yaml | d2 | 任务下达D2 |
| s11-tax.yaml | tax | 税务计算 |
| s12-dq.yaml | dq | 劳务确认DQ |
| s13-sq.yaml | sq | 财务确认SQ |
| s14-y.yaml | y | 用友导出Y |
| s15-change.yaml | change | 变更对比 |
| s16-local.yaml | local | 本地运行 |
| s17-summary.yaml | summary | 总结 |
| s18-closing.yaml | closing | 结束页 |

## CI/CD

推送到 main 分支后，GitHub Actions 自动:
1. 检出代码
2. 运行 build.py 生成 index.html
3. 部署到 GitHub Pages
