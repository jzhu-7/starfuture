# 房地产销售数据监控系统

## 项目结构

```
house/
├── app.py                 # Streamlit可视化大屏
├── core/                  # 核心业务逻辑
│   ├── __init__.py       # 包初始化
│   ├── main.py           # 主入口脚本
│   ├── config/           # 配置管理
│   │   ├── __init__.py
│   │   └── config.py
│   ├── utils/            # 工具函数
│   │   ├── __init__.py
│   │   └── utils.py
│   ├── models/           # 数据模型
│   │   ├── __init__.py
│   │   └── models.py
│   ├── scrapers/         # 数据抓取
│   │   ├── __init__.py
│   │   ├── area_scraper.py
│   │   └── status_scraper.py
│   └── processors/       # 数据处理
│       ├── __init__.py
│       └── data_processor.py
├── data/                 # 数据存储
│   ├── total.json
│   ├── areas/
│   └── sales/
├── logs/                 # 日志文件
│   └── house_data.log
└── houses_by_building/   # 房屋数据
```

## 使用方法

### 更新销售数据
```bash
python core/main.py data
```

### 更新面积数据
```bash
python core/main.py areas
```

### 默认更新（销售数据）
```bash
python core/main.py
```

## 日志系统

系统使用专业的Python logging模块，支持：

- **结构化输出**：时间戳、模块名、日志级别、消息
- **双重输出**：同时输出到控制台和文件
- **可配置级别**：DEBUG、INFO、WARNING、ERROR、CRITICAL
- **文件位置**：`logs/house_data.log`

### 日志级别说明

- `INFO`: 重要操作信息（如"开始更新数据"）
- `WARNING`: 警告信息（如"跳过某些数据"）
- `ERROR`: 错误信息（如"请求失败"）
- `DEBUG`: 详细调试信息（开发时使用）

## 主要改进

1. **模块化设计**：将功能拆分为独立的模块
2. **配置集中管理**：所有配置项统一管理
3. **代码复用**：消除重复代码
4. **类型安全**：使用数据类定义数据结构
5. **专业日志系统**：结构化日志输出，支持控制台和文件双重输出
6. **向后兼容**：保留原有脚本的兼容性
5. **错误处理**：改进异常处理和日志记录
6. **向后兼容**：保留原有脚本的兼容性