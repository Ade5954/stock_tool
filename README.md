## 程序简介

股票金字塔加仓工具是一款专为股票投资者设计的辅助决策软件，基于金字塔加仓策略（越跌越买）的原理，帮助投资者在下跌行情中系统性地制定分批买入计划。通过该工具，您可以根据当前价格、止损价格和投入资金，自动生成详细的分批买入方案，并获得风险评估和收益分析。

## 功能特点

1. **金字塔加仓计划生成**
   - 根据当前价格和止损价格划分20个价格区间
   - 采用非线性权重分配资金，低价位区间分配更多资金
   - 自动计算每个价格区间的买入股数和投入金额

2. **实时行情获取**
   - 支持输入股票代码自动获取实时行情
   - 显示股票名称、当前价格、涨跌幅、最高价、最低价等信息
   - 每10秒自动刷新行情数据

3. **基本面信息展示**
   - 展示市盈率、市净率、总市值、换手率和股息率等基本面数据
   - 帮助投资者全面了解股票基本情况

4. **平均成本和收益分析**
   - 计算每次买入后的累计平均成本
   - 分析目标价格下的预期收益率
   - 使用红绿色视觉区分正负收益

5. **风险评估系统**
   - 计算最大投入金额、最大回撤比例
   - 分析风险收益比和盈亏平衡价格
   - 预测最大预期收益率

6. **可视化图表分析**
   - 买入价格与股数关系图
   - 平均成本变化曲线图
   - 预期收益率分析柱状图

## 使用指南

### 1. 获取股票行情
- 在"股票代码"输入框中输入股票代码（如：300888）
- 点击"获取行情"按钮，程序将自动获取并显示股票信息
- 行情数据会每10秒自动更新

### 2. 设置策略参数
- **当前价格**：输入股票当前价格（获取行情后会自动填充）
- **止损目标价**：设置您的止损价格，低于此价格将不再买入
- **本金(元)**：设置您计划投入的总资金
- **目标价格**：设置预期的目标价格（用于计算收益率）

### 3. 生成加仓计划
- 完成参数设置后，点击"生成加仓列表"按钮
- 程序将生成20个价格区间的买入计划
- 表格中会显示每个价格区间的详细买入信息
- 风险评估摘要区域会显示核心风险指标

### 4. 查看分析结果
- **加仓列表选项卡**：查看详细的买入计划表格
- **分析图表选项卡**：查看三种可视化分析图表
  - 上图：买入股数和投入金额分析
  - 中图：平均成本变化及关键价格线
  - 下图：预期收益率分析

## 详细功能说明

### 表格数据说明
- **价格区间**：从当前价格到止损价格之间划分的20个区间
- **买入价格**：每个区间的具体买入价格
- **买入比例**：当前区间分配的资金比例
- **买入股数**：当前价格下应买入的股票数量
- **本次投入**：当前区间需要投入的资金
- **累计投入**：到当前区间为止的累计投入资金
- **平均成本**：到当前区间为止的加权平均买入成本
- **盈亏平衡**：需要上涨到什么价格才能实现盈亏平衡
- **收益分析**：目标价格下的预期收益率

### 风险评估指标说明
- **最大投入金额**：执行完整策略需要的总资金
- **最大回撤**：从当前价格到止损价格的最大跌幅
- **风险收益比**：潜在收益与潜在损失的比值
- **盈亏平衡价格**：总体平均成本价格
- **最大预期收益率**：目标价格下的最大潜在收益率

### 图表说明
- **金字塔加仓买点图**：显示买入股数和投入金额随价格变化的关系
- **平均成本图**：显示平均成本随买入价格的变化，以及当前价格、止损价格和目标价格线
- **预期收益率分析图**：显示每个买入点在目标价格下的潜在收益率（红色为正收益，绿色为负收益）

## 注意事项

1. 本工具仅提供决策参考，不构成投资建议
2. 实际交易中可能存在滑点、手续费等因素影响
3. 股票基本面数据为模拟数据，仅供参考
4. 止损价格应根据个人风险承受能力和具体股票波动特性设定
5. 使用金字塔加仓策略需要足够的资金支持，请根据自身资金状况合理规划

## 免责声明

本软件仅作为投资决策辅助工具，不对因使用本软件而导致的任何投资损失负责。投资者应当对自己的投资决策负责，并承担相应的风险。

---

开发者：Ade
版本：1.0
最后更新：2025.3.14
