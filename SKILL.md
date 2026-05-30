# funNLP-toolkit

中文 NLP 资源工具包 - 基于 funNLP 项目

## 描述

funNLP-toolkit 是基于 [funNLP](https://github.com/fighting41love/funNLP) 项目的中文 NLP 工具包，提供中文 NLP 常用资源的快速加载和使用。

## 功能

### 1. 资源搜索
- 搜索 funNLP 60+ 类别的 NLP 资源
- 支持关键词和自然语言查询
- 返回相关资源链接和描述

### 2. 词库加载
- 一键加载常用中文词库
- 支持：停用词、人名库、公司名、地名、成语等
- 提供统计信息和预览

### 3. 文本处理工具
- 信息抽取（人名、地址、邮箱、手机号）
- 时间表达式识别
- 繁简体转换
- 敏感词过滤

## 使用方法

### 搜索资源
```bash
python scripts/search.py --query "中文分词"
python scripts/search.py --query "知识图谱"
```

### 加载词库
```bash
python scripts/load_dict.py --type stopwords
python scripts/load_dict.py --type person_names --preview
```

### 文本处理
```bash
python scripts/extract.py --text "联系方式：张三，电话13800138000"
python scripts/extract.py --file input.txt --output json
```

## 配置

编辑 `config/settings.yaml` 配置：
- 词库路径
- 缓存设置
- 输出格式

## 依赖

- Python 3.8+
- PyYAML
- jieba (可选)

## 数据源

本 Skill 使用 funNLP 项目的数据资源：
- 项目地址: https://github.com/fighting41love/funNLP
- 数据位置: `../../funNLP/data/`

## 许可证

Apache 2.0

---

基于 funNLP 项目二次开发
