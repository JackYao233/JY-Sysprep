# JY Sysprep

## Windows Sysprep Automation and Image Deployment Framework

## Windows 系统封装与镜像部署自动化框架


------------------------------------------------------------------------

# 📖 Introduction \| 项目介绍

## English

JY Sysprep is an open-source Windows system preparation and deployment
framework.

The project aims to provide a flexible, modular, and extensible solution
for Windows image customization, system preparation, and automated
deployment.

Inspired by Easy Sysprep, SC and Microsoft Deployment Toolkit (MDT), JY
Sysprep is designed to evolve from a simple Sysprep automation tool into
a complete Windows image management platform.

## 中文

JY Sysprep 是一个开源的 Windows 系统封装与部署自动化框架。

项目旨在提供一个灵活、模块化、可扩展的 Windows
镜像制作、系统配置以及自动化部署解决方案。

项目参考 Easy Sysprep、SC 封装工具以及 Microsoft Deployment Toolkit
(MDT) 等工具理念，计划从基础 Sysprep 自动化工具逐步发展为完整的 Windows
镜像管理平台。

------------------------------------------------------------------------

# ✨ Features \| 功能特性

# Current Features \| 当前已实现功能

## ✅ Sysprep Automation \| Sysprep 自动化

### English

-   Automatically generate unattend.xml
-   Execute Sysprep workflow
-   Support Windows Audit Mode environment
-   Provide automated system preparation workflow

### 中文

-   自动生成 unattend.xml
-   自动执行 Sysprep 封装流程
-   支持 Windows 审核模式环境
-   提供自动化系统准备流程

------------------------------------------------------------------------

## ✅ Unattend Template System \| 无人值守模板系统

### English

A template-based unattended configuration system.

Features:

-   Windows version templates
-   XML template management
-   Automatic configuration generation
-   Extensible architecture

### 中文

基于模板的无人值守配置系统。

功能：

-   Windows版本模板管理
-   XML模板管理
-   自动配置生成
-   可扩展架构设计

------------------------------------------------------------------------

# 🚧 Planned Features \| 未来规划功能

# Environment Validator \| 环境验证系统

## English

A system environment verification module used to ensure that the
operating environment meets the requirements before execution.

Planned features:

-   Audit Mode detection
-   Administrator privilege verification
-   Sysprep status checking
-   System compatibility checking

## 中文

用于在执行封装流程前检测系统环境是否满足要求。

计划功能：

-   审核模式检测
-   管理员权限验证
-   Sysprep状态检测
-   系统兼容性检查

------------------------------------------------------------------------

# Personalization Engine \| 个性化配置引擎

## English

A customizable Windows personalization module.

Planned features:

-   Desktop customization
-   Wallpaper management
-   Theme configuration
-   Start Menu customization
-   Default user profile customization
-   Deployment branding

## 中文

用于实现 Windows 系统个性化配置的模块。

计划功能：

-   桌面个性化
-   壁纸管理
-   主题配置
-   开始菜单配置
-   默认用户配置
-   部署品牌化设置

------------------------------------------------------------------------

# Deployment Experience \| 部署体验系统

## English

A deployment interface customization system designed to improve user
experience during Windows installation and deployment.

Planned features:

-   Custom deployment background
-   Custom logo
-   Progress interface
-   Deployment animation
-   Brand customization

## 中文

用于提升 Windows 部署过程体验的界面定制系统。

计划功能：

-   自定义部署背景
-   自定义Logo
-   部署进度界面
-   部署动画
-   品牌化展示

------------------------------------------------------------------------

# Image Management \| 镜像管理系统

## English

A complete Windows image management solution based on DISM and WIM
technologies.

Planned features:

-   DISM integration
-   WIM capture
-   Image apply
-   Driver injection
-   Package management
-   Image optimization

## 中文

基于 DISM 与 WIM 技术的完整 Windows 镜像管理方案。

计划功能：

-   DISM集成
-   WIM捕获
-   镜像部署
-   驱动注入
-   软件包管理
-   镜像优化

------------------------------------------------------------------------

# 🏗 Architecture \| 项目架构

    JY Sysprep

    ├── Environment Layer
    │
    ├── Validator Layer
    │
    ├── Sysprep Core
    │
    ├── Unattend Generator
    │
    ├── Personalization Engine
    │
    ├── Deployment Experience
    │
    └── Image Management

## English

JY Sysprep adopts a modular architecture.

Each module is independent and designed for future expansion.

## 中文

JY Sysprep采用模块化架构设计。

每个模块保持独立，便于后续功能扩展。

Module Description \| 模块说明：

  -----------------------------------------------------------------------
  Module                  English                 中文
  ----------------------- ----------------------- -----------------------
  Environment             Environment detection   环境检测

  Validator               System validation       状态验证

  Sysprep Core            Core packaging workflow 封装核心流程

  Unattend Generator      Automated XML           自动生成无人值守配置
                          generation              

  Personalization Engine  System customization    系统个性化

  Deployment Experience   Deployment interface    部署体验优化
                          customization           

  Image Management        Windows image           Windows镜像管理
                          management              
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 📌 Roadmap \| 开发路线

  ---------------------------------------------------------------------------
  Version           Status            Description       中文说明
  ----------------- ----------------- ----------------- ---------------------
  Alpha 0.1         ✅ Completed      Basic Sysprep     基础Sysprep自动化
                                      automation        

  Alpha 0.2         ✅ Completed     Validator and     验证器与执行框架
                                      execution         
                                      framework         

  Alpha 0.3         🚧 Developing     TUI Wizard        文本化向导

  Alpha 0.4         Planned           Personalization   个性化配置引擎
                                      Engine            

  Alpha 0.5         Planned           Deployment        部署体验系统
                                      Experience        

  Beta              Planned           Complete image    完整镜像管理系统
                                      management        

  1.0               Future            Full Windows      完整Windows部署平台
                                      deployment        
                                      platform          
  ---------------------------------------------------------------------------

------------------------------------------------------------------------

# 💻 Requirements \| 环境要求

## English

Current requirements:

-   Windows 8.x / Windows 10 / Windows 11
-   Python 3.8+
-   Administrator privilege
-   To run this software, the system must in audit mode

## 中文

当前环境要求：

-   Windows 8.x / Windows 10 / Windows 11
-   Python 3.8+
-   管理员权限
-   需保证系统处于审核模式

------------------------------------------------------------------------

# 🚀 Development \| 开发

## English

Clone repository:

``` bash
git clone https://github.com/JackYao233/JY-Sysprep.git
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

Run:

``` bash
python main.py
```

## 中文

克隆仓库：

``` bash
git clone https://github.com/JackYao233/JY-Sysprep.git
```

安装依赖：

``` bash
pip install -r requirements.txt
```

运行：

``` bash
python main.py
```

------------------------------------------------------------------------

# 📂 Project Structure \| 项目结构

    JY-Sysprep

    ├── src
    ├── templates
    ├── config
    ├── docs
    ├── requirements.txt
    └── README.md

## English

The project structure will continue to evolve with new modules.

## 中文

随着功能增加，项目结构将持续扩展。

------------------------------------------------------------------------

# 🤝 Contribution \| 贡献

## English

Contributions, suggestions, and issue reports are welcome.

## 中文

欢迎提交 Issue、功能建议以及代码贡献。

------------------------------------------------------------------------

# 📄 License \| 开源协议

MIT License

MIT 开源协议

