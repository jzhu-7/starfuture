# 销售数据监控系统 

**简介**

这是一个用于抓取、处理并可视化房地产销售与面积数据的轻量化 Python 项目。项目包含数据抓取（scrapers）、数据处理（processors）、核心运行脚本（core）和基于 Streamlit 的可视化大屏（`app.py`）。

---

## ⚙️ 系统功能（详细说明）

- 自动抓取
  - 抓取期房签约统计（`core/processors` 从 `DATA_URL` 解析期房签约表）。
  - 抓取楼栋状态（`core/scrapers/status_scraper.py`）：并行抓取各楼栋房源状态，保存到 `data/sales/YYYY-MM-DD.json`。
  - 抓取房源面积（`core/scrapers/area_scraper.py`）：解析房源详情页并生成 `data/areas/areas.json`。

- 数据处理与合成
  - 解析期房统计表并计算累计、当日与增量（`core/processors/data_processor.py`）。
  - 将状态变化（由 `status_scraper` 比对前后数据得到的变动）与面积数据关联，生成成交户号列表并写入 `data/total.json`。
  - 支持按日期写入和覆盖（同日自动覆盖）。

- 可视化与交互（Streamlit）
  - `app.py` 提供可视化大屏：顶部KPI卡、价格趋势图、当日成交明细卡片与房号卡片展示。
  - 侧边栏支持手动更新（点击“更新数据”会调用 `core.main` 执行抓取与处理流程）、日期选择器与跳转至最新成交按钮。
  - 可视化对数据缺失有良好容错：显示空状态提示并支持选择最近可用数据。

### 🖥️ 可视化界面使用指南（UI 使用教程）

以下为用户打开 `streamlit run app.py` 后在页面中常见交互的说明：

- 启动与刷新
  - 启动：运行 `streamlit run app.py`，浏览器打开后即可看到仪表盘。
  - 手动更新数据：点击左侧栏的 **更新数据** 按钮，会触发后端脚本（等同于 `python -m core.main`），页面会显示加载 Spinner，完成后给出成功或失败提示；成功后页面会自动刷新并清除缓存。

- 侧边栏（控制面板）
  - **更新数据**：触发抓取与处理流程（请耐心等待，脚本运行会输出日志信息）。
  - **日期选择器**：选择要查看的日期（默认显示最新日期）。选择后，页面会显示该日期的数据（若该日期无部分数据，会使用最近可用数据替代相关指标）。
  - **当前显示提示**：侧边栏会展示“当前显示: YYYY-MM-DD”，便于确认当前上下文。

- 顶部 KPI 卡（指标含义）
  - **累计签约套数**：截至当前日期累计签约的套数（来自 `data/total.json`）。
  - **累计签约面积 (㎡)**：累计已签约的建筑面积，单位平方米。
  - **累计成交均价**：按累计数据计算的平均单价（￥/㎡）。
  - **当日均价 / 最新均价**：显示选中日期或最近有数据日期的当日均价，并展示与上一个有记录日期的环比变化。

- 成交明细卡（左侧大卡）
  - 当天无成交：卡片中显示“当天暂无成交记录”，并提供“跳转至最新成交”按钮快速查看最近有成交数据的日期。
  - 有成交记录：卡片列出每个成交的房号、建筑面积与总价（总价为 建筑面积 × 当日均价，当数据缺失时显示 N/A）。
  - 房号格式：通常以 “楼盘名#房号” 展示，面积以平方米显示。

- 价格趋势图（右侧）
  - 两条曲线：**累计均价**（主曲线）与**当日均价**（辅助曲线）。
  - 悬停提示：将鼠标悬停到图上可以精确看到某日的两条价格数据。
  - 选中日期高亮：当前选中日期在曲线上会有高亮点和垂直参考线，便于与成交明细关联查看。

- 常见问题与排查（Troubleshooting）
  - 页面提示“暂无数据”：确认是否已执行一次 `更新数据`；可查看 `data/total.json` 是否存在且非空。
  - 更新失败或脚本异常：侧边栏会显示错误信息，更多日志可查看终端输出或 `logs/house_data.log`（若启用日志文件）。
  - 当日有均价但无成交户号：说明该日统计有均价数据但没有通过状态比对得到可售→签约的具体房号，属于正常情况。

- 使用小贴士
  - 若频繁刷新导致页面缓存问题，可在更新成功后手动清除浏览器缓存或重启 Streamlit 服务。
  - 想要定时抓取数据，可以将 `python -m core.main data` 加入系统计划任务（cron / Windows Task Scheduler）。


- 并发、健壮性与配置
  - 抓取使用多线程（ThreadPoolExecutor）并有超时与延迟控制（`core/config` 中配置 `MAX_WORKERS`、`REQUEST_TIMEOUT`、`REQUEST_DELAY`）。
  - 集中配置管理：`core/config/__init__.py`（URL、路径、状态颜色映射等）。
  - 日志系统：使用 Python logging，默认输出到控制台（可配置追加到文件 `logs/house_data.log`）。

- 输出与兼容性
  - 主要输出文件：`data/areas/areas.json`、`data/sales/YYYY-MM-DD.json`、`data/total.json`。
  - 提供 CLI 入口：`python core/main.py [areas|data]`，便于定时任务或手动触发。
  - 易扩展：新增抓取器或处理逻辑可放到 `core/scrapers` / `core/processors` 中，配置集中管理降低耦合。

---

## 🚀 快速开始

1. 克隆仓库并进入目录：

```bash
git clone <repo-url>
cd house
```

2. 创建并激活虚拟环境，安装依赖：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. 常用命令：

- 更新销售数据：

```bash
python core/main.py data
```

- 更新面积数据：

```bash
python core/main.py areas
```

- 默认更新（等同于销售数据）：

```bash
python core/main.py
```

- 启动可视化大屏（Streamlit）：

```bash
streamlit run app.py
```

- 或使用运行脚本：
  - Linux/macOS: `./run.sh`
  - Windows: `run.bat`

---

## 📁 项目结构（简要）

```
.
├── app.py                 # Streamlit 可视化入口
├── core/
│   ├── main.py            # 项目主脚本（CLI）
│   ├── config/            # 配置（可在此调整日志/抓取选项）
│   ├── scrapers/          # 抓取器（area, status 等）
│   ├── processors/        # 数据处理逻辑
│   └── utils/             # 工具函数
├── data/                  # 输出的数据（total.json, sales/, areas/）
├── logs/                  # 日志（house_data.log）
└── requirements.txt
```

---

## 🗂️ 数据说明

- `data/total.json`：汇总后的总数据
- `data/areas/areas.json`：面积相关数据
- `data/sales/YYYY-MM-DD.json`：按日期保存的每日销售数据

---

## 📝 日志与配置

- 日志路径：`logs/house_data.log`
- 日志级别：`DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL`
- 配置文件位置：`core/config/config.py`（可修改抓取间隔、日志级别等）

> ⚠️ 出错排查提示：若抓取或请求失败，请检查日志文件 `logs/house_data.log` 获取详细错误信息。
