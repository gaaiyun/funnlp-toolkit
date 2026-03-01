# funNLP-toolkit

中文 NLP 资源工具包 - OpenClaw Skill

## 简介

funNLP-toolkit 是基于 [funNLP](https://github.com/fighting41love/funNLP) 项目的 OpenClaw Skill，提供中文 NLP 常用资源的快速加载和使用。

## 功能特性

### 1. 资源搜索
搜索 funNLP 60+ 类别的 NLP 资源，支持关键词查询。

### 2. 词库加载
一键加载常用中文词库：
- 停用词
- 人名库（中英文）
- 公司名、地名
- 成语、动物、医学、法律、财经等专业词库

### 3. 统计预览
查看词库统计信息和内容预览。

## 快速开始

### 搜索资源
```bash
python scripts/search.py --query "中文分词"
python scripts/search.py --query "知识图谱" --limit 5
```

### 加载词库
```bash
# 查看可用词库类型
python scripts/load_dict.py --type stopwords --stats

# 加载停用词
python scripts/load_dict.py --type stopwords --preview

# 加载人名库
python scripts/load_dict.py --type person_names_cn --stats

# JSON 输出
python scripts/load_dict.py --type idioms --output json
```

## 可用词库类型

| 类型 | 说明 | 数据源 |
|------|------|--------|
| `stopwords` | 停用词 | 停用词/stopwords.txt |
| `person_names_cn` | 中文人名 | 中英日本人名字库/ |
| `person_names_en` | 英文人名 | 中英日本人名字库/ |
| `company_names` | 公司名 | 公司名字词库/ |
| `place_names` | 地名 | 地名词库/THUOCL_diming.txt |
| `idioms` | 成语 | 成语词库/idiom.txt |
| `animals` | 动物 | 动物词库/THUOCL_animal.txt |
| `medical` | 医学 | 医学词库/THUOCL_medical.txt |
| `law` | 法律 | 法律词库/THUOCL_law.txt |
| `finance` | 财经 | 财经词库/THUOCL_caijing.txt |
| `food` | 食品 | 食品词库/THUOCL_food.txt |
| `car` | 汽车品牌 | 汽车品牌词库/THUOCL_car.txt |
| `it` | IT 词汇 | IT词库/THUOCL_it.txt |

## 配置

编辑 `config/settings.yaml` 自定义配置：
```yaml
data_dir: "../../funNLP/data"
dictionaries:
  encoding: "utf-8"
  cache_enabled: true
```

## 依赖

- Python 3.8+
- PyYAML (可选)

## 数据源

本 Skill 使用 funNLP 项目的数据资源：
- 项目: https://github.com/fighting41love/funNLP
- Stars: 79.1k+
- 数据位置: `workspace/funNLP/data/`

## 许可证

Apache 2.0

---

基于 funNLP 项目二次开发
