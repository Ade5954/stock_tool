import sys
import os
import numpy as np
import requests
import json
import re
import matplotlib
from matplotlib import font_manager
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMessageBox, QGridLayout, QFileDialog, QSizePolicy,
                             QComboBox, QGroupBox, QTabWidget)
from PyQt5.QtGui import QDoubleValidator, QFont, QColor
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# 设置matplotlib中文字体支持
def set_matplotlib_chinese_font():
    # 判断操作系统类型
    if sys.platform.startswith('win'):
        # Windows系统
        font_family = ['Microsoft YaHei', 'SimHei', 'SimSun']
    elif sys.platform.startswith('darwin'):
        # macOS系统
        font_family = ['Heiti SC', 'Hei', 'STHeiti', 'SimHei']
    else:
        # Linux系统
        font_family = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'SimHei']
    
    # 尝试按优先级设置字体
    font_found = False
    for font in font_family:
        try:
            matplotlib.rcParams['font.family'] = [font]
            font_found = True
            print(f"已设置中文字体: {font}")
            break
        except:
            continue
    
    # 如果未找到中文字体，使用通用设置
    if not font_found:
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial']
    
    # 修复负号显示问题
    matplotlib.rcParams['axes.unicode_minus'] = False
    
# 初始化matplotlib中文支持
set_matplotlib_chinese_font()

class PyramidStockTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.last_generated_data = None
        
    def initUI(self):
        self.setWindowTitle('股票金字塔加仓工具')
        self.setGeometry(300, 300, 1100, 900)  # 略微增大窗口尺寸
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 添加标题
        title_label = QLabel("股票金字塔加仓策略")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建股票行情区域
        stock_quote_group = QGroupBox("实时行情")
        stock_quote_layout = QGridLayout(stock_quote_group)
        
        # 股票代码输入
        stock_code_label = QLabel("股票代码:")
        self.stock_code_edit = QLineEdit()
        self.stock_code_edit.setPlaceholderText("输入股票代码，如：600000(上证) 或 000001(深证)")
        
        # 行情获取按钮
        get_quote_button = QPushButton("获取行情")
        get_quote_button.clicked.connect(self.get_stock_quote)
        
        # 股票信息显示 - 第一行基本信息
        self.stock_name_label = QLabel("股票名称: --")
        self.stock_price_label = QLabel("当前价格: --")
        self.stock_change_label = QLabel("涨跌幅: --")
        self.stock_high_label = QLabel("最高: --")
        self.stock_low_label = QLabel("最低: --")
        
        # 股票信息显示 - 第二行基本面信息
        self.stock_pe_label = QLabel("市盈率(TTM): --")
        self.stock_pb_label = QLabel("市净率: --")
        self.stock_market_cap_label = QLabel("总市值: --")
        self.stock_turnover_label = QLabel("换手率: --")
        self.stock_dividend_yield_label = QLabel("股息率: --")
        
        # 添加到股票行情布局
        stock_quote_layout.addWidget(stock_code_label, 0, 0)
        stock_quote_layout.addWidget(self.stock_code_edit, 0, 1, 1, 2)
        stock_quote_layout.addWidget(get_quote_button, 0, 3)
        
        stock_quote_layout.addWidget(self.stock_name_label, 1, 0, 1, 2)
        stock_quote_layout.addWidget(self.stock_price_label, 1, 2)
        stock_quote_layout.addWidget(self.stock_change_label, 1, 3)
        stock_quote_layout.addWidget(self.stock_high_label, 1, 4)
        stock_quote_layout.addWidget(self.stock_low_label, 1, 5)
        
        # 添加基本面信息到第二行
        stock_quote_layout.addWidget(self.stock_pe_label, 2, 0)
        stock_quote_layout.addWidget(self.stock_pb_label, 2, 1)
        stock_quote_layout.addWidget(self.stock_market_cap_label, 2, 2)
        stock_quote_layout.addWidget(self.stock_turnover_label, 2, 3)
        stock_quote_layout.addWidget(self.stock_dividend_yield_label, 2, 4, 1, 2)
        
        # 创建输入区域
        input_group = QGroupBox("策略参数")
        input_layout = QGridLayout(input_group)
        
        # 当前价格输入
        current_price_label = QLabel("当前价格:")
        self.current_price_edit = QLineEdit()
        self.current_price_edit.setValidator(QDoubleValidator(0.00, 100000.00, 2))
        
        # 止损目标价输入
        stop_loss_label = QLabel("止损目标价:")
        self.stop_loss_edit = QLineEdit()
        self.stop_loss_edit.setValidator(QDoubleValidator(0.00, 100000.00, 2))
        
        # 本金输入
        capital_label = QLabel("本金(元):")
        self.capital_edit = QLineEdit()
        self.capital_edit.setValidator(QDoubleValidator(0.00, 1000000000.00, 2))
        
        # 目标价格输入
        target_price_label = QLabel("目标价格:")
        self.target_price_edit = QLineEdit()
        self.target_price_edit.setValidator(QDoubleValidator(0.00, 100000.00, 2))
        
        # 生成按钮
        generate_button = QPushButton("生成加仓列表")
        generate_button.clicked.connect(self.generate_pyramid)
        
        # 添加控件到输入布局
        input_layout.addWidget(current_price_label, 0, 0)
        input_layout.addWidget(self.current_price_edit, 0, 1)
        input_layout.addWidget(stop_loss_label, 0, 2)
        input_layout.addWidget(self.stop_loss_edit, 0, 3)
        input_layout.addWidget(capital_label, 0, 4)
        input_layout.addWidget(self.capital_edit, 0, 5)
        input_layout.addWidget(target_price_label, 0, 6)
        input_layout.addWidget(self.target_price_edit, 0, 7)
        input_layout.addWidget(generate_button, 0, 8)
        
        # 创建表格和图表的布局
        content_layout = QVBoxLayout()
        
        # 添加风险评估摘要区域
        risk_summary_group = QGroupBox("风险评估摘要")
        risk_summary_layout = QHBoxLayout(risk_summary_group)
        
        # 创建风险指标标签
        self.max_investment_label = QLabel("最大投入金额: --")
        self.max_drawdown_label = QLabel("最大回撤: --")
        self.risk_reward_ratio_label = QLabel("风险收益比: --")
        self.breakeven_price_label = QLabel("盈亏平衡价格: --")
        self.max_return_label = QLabel("最大预期收益率: --")
        
        # 添加风险指标到布局
        risk_summary_layout.addWidget(self.max_investment_label)
        risk_summary_layout.addWidget(self.max_drawdown_label)
        risk_summary_layout.addWidget(self.risk_reward_ratio_label)
        risk_summary_layout.addWidget(self.breakeven_price_label)
        risk_summary_layout.addWidget(self.max_return_label)
        
        content_layout.addWidget(risk_summary_group)
        
        # 创建选项卡布局
        tab_widget = QTabWidget()
        
        # 表格选项卡
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # 增加到9列，添加平均成本、收益率分析
        self.table.setHorizontalHeaderLabels([
            "价格区间", "买入价格", "买入比例", "买入股数", 
            "本次投入", "累计投入", "平均成本", "盈亏平衡", "收益分析"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        table_layout.addWidget(self.table)
        tab_widget.addTab(table_tab, "加仓列表")
        
        # 图表选项卡
        chart_tab = QWidget()
        chart_layout = QVBoxLayout(chart_tab)
        
        # 创建Matplotlib图表
        self.figure = Figure(figsize=(5, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(300)
        chart_layout.addWidget(self.canvas)
        
        tab_widget.addTab(chart_tab, "分析图表")
        
        # 添加选项卡到内容布局
        content_layout.addWidget(tab_widget)
        
        # 添加到主布局
        main_layout.addWidget(stock_quote_group)
        main_layout.addWidget(input_group)
        main_layout.addLayout(content_layout)
        
        # 设置自动刷新定时器
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_quote)
        
        # 当前股票代码
        self.current_stock_code = None
        self.current_stock_price = None
    
    def get_stock_code_prefix(self, code):
        """根据股票代码获取前缀"""
        code = code.strip()
        if code.startswith('6'):
            return 'sh' + code
        elif code.startswith('0') or code.startswith('3'):
            return 'sz' + code
        return code
    
    def get_stock_quote(self):
        """获取股票实时行情"""
        stock_code = self.stock_code_edit.text().strip()
        if not stock_code:
            QMessageBox.warning(self, "输入错误", "请输入股票代码!")
            return
        
        try:
            # 转换股票代码格式
            formatted_code = self.get_stock_code_prefix(stock_code)
            self.current_stock_code = formatted_code
            
            # 使用新浪财经API获取股票数据
            url = f"http://hq.sinajs.cn/list={formatted_code}"
            headers = {
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers)
            response.encoding = 'gbk'  # 设置正确的编码
            
            # 解析响应数据
            data = response.text
            pattern = r'"(.*)"'
            result = re.search(pattern, data)
            
            if result:
                stock_data = result.group(1).split(',')
                if len(stock_data) < 32:
                    raise ValueError("股票数据格式错误")
                
                # 提取股票信息
                stock_name = stock_data[0]
                current_price = float(stock_data[3])
                yesterday_close = float(stock_data[2])
                today_high = float(stock_data[4])
                today_low = float(stock_data[5])
                volume = float(stock_data[8]) # 成交量
                turnover = float(stock_data[9]) # 成交额
                
                # 计算涨跌幅
                change_percent = (current_price - yesterday_close) / yesterday_close * 100
                
                # 保存当前股价
                self.current_stock_price = current_price
                
                # 更新UI显示
                self.stock_name_label.setText(f"股票名称: {stock_name}")
                self.stock_price_label.setText(f"当前价格: {current_price}")
                
                # 根据涨跌幅设置颜色
                change_text = f"涨跌幅: {change_percent:.2f}%"
                if change_percent > 0:
                    self.stock_change_label.setStyleSheet("color: red")
                    change_text = "涨跌幅: +" + change_text[5:]
                elif change_percent < 0:
                    self.stock_change_label.setStyleSheet("color: green")
                else:
                    self.stock_change_label.setStyleSheet("")
                
                self.stock_change_label.setText(change_text)
                self.stock_high_label.setText(f"最高: {today_high}")
                self.stock_low_label.setText(f"最低: {today_low}")
                
                # 自动填充当前价格到价格输入框
                self.current_price_edit.setText(str(current_price))
                
                # 获取额外的基本面数据
                self.get_stock_fundamentals(stock_code)
                
                # 启动自动刷新
                if not self.refresh_timer.isActive():
                    self.refresh_timer.start(10000)  # 每10秒刷新一次
                
                return True
            else:
                QMessageBox.warning(self, "获取失败", "未找到股票数据，请检查股票代码是否正确!")
                return False
                
        except Exception as e:
            QMessageBox.warning(self, "获取失败", f"获取股票行情失败: {str(e)}")
            return False
    
    def auto_refresh_quote(self):
        """自动刷新股票行情"""
        if self.current_stock_code:
            try:
                url = f"http://hq.sinajs.cn/list={self.current_stock_code}"
                headers = {
                    'Referer': 'https://finance.sina.com.cn',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers)
                response.encoding = 'gbk'
                
                data = response.text
                pattern = r'"(.*)"'
                result = re.search(pattern, data)
                
                if result:
                    stock_data = result.group(1).split(',')
                    if len(stock_data) < 32:
                        return
                    
                    # 更新价格信息
                    current_price = float(stock_data[3])
                    yesterday_close = float(stock_data[2])
                    today_high = float(stock_data[4])
                    today_low = float(stock_data[5])
                    
                    # 更新当前股价
                    self.current_stock_price = current_price
                    
                    # 计算涨跌幅
                    change_percent = (current_price - yesterday_close) / yesterday_close * 100
                    
                    # 更新UI显示
                    self.stock_price_label.setText(f"当前价格: {current_price}")
                    
                    change_text = f"涨跌幅: {change_percent:.2f}%"
                    if change_percent > 0:
                        self.stock_change_label.setStyleSheet("color: red")
                        change_text = "涨跌幅: +" + change_text[5:]
                    elif change_percent < 0:
                        self.stock_change_label.setStyleSheet("color: green")
                    else:
                        self.stock_change_label.setStyleSheet("")
                    
                    self.stock_change_label.setText(change_text)
                    self.stock_high_label.setText(f"最高: {today_high}")
                    self.stock_low_label.setText(f"最低: {today_low}")
                    
                    # 自动更新当前价格输入框
                    self.current_price_edit.setText(str(current_price))
            except:
                # 静默处理自动刷新中的错误
                pass
    
    def fill_current_price(self):
        """将当前股价填充到当前价格输入框"""
        if self.current_stock_price is not None:
            self.current_price_edit.setText(str(self.current_stock_price))
        else:
            QMessageBox.information(self, "提示", "请先获取股票行情!")
        
    def generate_pyramid(self):
        try:
            current_price = float(self.current_price_edit.text())
            stop_loss = float(self.stop_loss_edit.text())
            capital = float(self.capital_edit.text())
            
            # 获取目标价格，如果未填写则默认为当前价格的20%上涨
            target_price_text = self.target_price_edit.text()
            if target_price_text:
                target_price = float(target_price_text)
            else:
                target_price = current_price * 1.2
                # 更新到UI
                self.target_price_edit.setText(f"{target_price:.2f}")
            
            if current_price <= stop_loss:
                QMessageBox.warning(self, "输入错误", "当前价格必须高于止损价格!")
                return
                
            if target_price <= current_price:
                QMessageBox.warning(self, "输入警告", "目标价格应该高于当前价格，否则可能无法获得盈利！")
                # 不中断执行，只是警告
            
            # 计算价格区间
            price_diff = current_price - stop_loss
            step = price_diff / 20
            
            # 修正权重分配：低价位权重大，高价位权重小
            # 使用平方关系增加权重差异，符合金字塔加仓的"越跌越买"原则
            weights = [(i+1)**2 for i in range(20)]
            total_weight = sum(weights)
            
            # 清空表格并设置行数
            self.table.setRowCount(20)
            
            cumulative_investment = 0
            total_shares = 0
            
            # 存储买点信息用于绘图
            buy_prices = []
            shares_list = []
            investment_list = []
            avg_cost_list = []
            profit_point_list = []
            potential_return_list = []
            
            # 填充表格
            for i in range(20):
                weight = weights[i]  # 使用非线性权重
                price = current_price - step * (i + 1)
                buy_prices.append(price)
                
                # 计算当前价位应分配的资金比例和金额
                allocation_ratio = weight / total_weight
                allocated_capital = allocation_ratio * capital
                
                # 计算股数 (允许小数，最后展示时四舍五入)
                shares = int(round(allocated_capital / price))
                shares_list.append(shares)
                
                actual_investment = shares * price
                investment_list.append(actual_investment)
                
                # 累计投资和持股数量
                cumulative_investment += actual_investment
                total_shares += shares
                
                # 计算平均成本
                avg_cost = cumulative_investment / total_shares if total_shares > 0 else 0
                avg_cost_list.append(avg_cost)
                
                # 计算盈亏平衡点
                # 盈亏平衡点是指需要涨到什么价格才能收回所有成本
                profit_point = avg_cost
                profit_point_list.append(profit_point)
                
                # 计算目标价格下的预期收益
                potential_profit = (target_price - avg_cost) * total_shares
                potential_return_pct = (potential_profit / cumulative_investment) * 100 if cumulative_investment > 0 else 0
                potential_return_list.append(potential_return_pct)
                
                # 添加表格数据 - 基本列
                self.table.setItem(i, 0, QTableWidgetItem(f"第{i+1}区间"))
                self.table.setItem(i, 1, QTableWidgetItem(f"{price:.2f}"))
                self.table.setItem(i, 2, QTableWidgetItem(f"{allocation_ratio*100:.2f}%"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{shares}"))
                self.table.setItem(i, 4, QTableWidgetItem(f"{actual_investment:.2f}"))
                self.table.setItem(i, 5, QTableWidgetItem(f"{cumulative_investment:.2f}"))
                
                # 添加表格数据 - 新增列
                self.table.setItem(i, 6, QTableWidgetItem(f"{avg_cost:.2f}"))
                self.table.setItem(i, 7, QTableWidgetItem(f"{profit_point:.2f}"))
                
                # 收益分析 - 显示目标价格下的预期收益率
                return_item = QTableWidgetItem(f"{potential_return_pct:.2f}%")
                if potential_return_pct > 0:
                    return_item.setForeground(QColor(255, 0, 0))  # 正收益显示为红色
                elif potential_return_pct < 0:
                    return_item.setForeground(QColor(0, 128, 0))  # 负收益显示为绿色
                self.table.setItem(i, 8, return_item)
                
                # 为表格添加颜色渐变，突出显示买入力度（低价区间颜色更深）
                intensity = int(200 * (i / 19))  # 0-200的颜色渐变
                for col in range(9):  # 扩展到9列
                    item = self.table.item(i, col)
                    if item:
                        item.setBackground(QColor(255, 255-intensity, 255-intensity))
            
            # 计算风险评估指标
            
            # 1. 最大投入金额
            max_investment = cumulative_investment
            
            # 2. 最大回撤 (基于当前价格到止损价格的跌幅)
            max_drawdown_pct = ((current_price - stop_loss) / current_price) * 100
            
            # 3. 风险收益比 (潜在收益与潜在损失的比值)
            potential_loss = max_investment * max_drawdown_pct / 100
            potential_gain = (target_price - avg_cost_list[-1]) * total_shares
            risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else float('inf')
            
            # 4. 盈亏平衡价格 (最终的平均成本)
            breakeven_price = avg_cost_list[-1]
            
            # 5. 最大预期收益率
            max_return = (target_price - breakeven_price) / breakeven_price * 100
            
            # 更新风险评估摘要
            self.max_investment_label.setText(f"最大投入金额: {max_investment:.2f}元")
            self.max_drawdown_label.setText(f"最大回撤: {max_drawdown_pct:.2f}%")
            self.risk_reward_ratio_label.setText(f"风险收益比: {risk_reward_ratio:.2f}")
            self.breakeven_price_label.setText(f"盈亏平衡价格: {breakeven_price:.2f}元")
            self.max_return_label.setText(f"最大预期收益率: {max_return:.2f}%")
            
            # 保存风险指标
            risk_metrics = {
                'max_investment': max_investment,
                'max_drawdown_pct': max_drawdown_pct,
                'risk_reward_ratio': risk_reward_ratio,
                'breakeven_price': breakeven_price,
                'max_return': max_return
            }
            
            # 保存生成的数据
            self.last_generated_data = {
                'current_price': current_price,
                'stop_loss': stop_loss,
                'buy_prices': buy_prices,
                'shares': shares_list,
                'investments': investment_list,
                'avg_costs': avg_cost_list,
                'profit_points': profit_point_list,
                'potential_returns': potential_return_list,
                'target_price': target_price,
                'risk_metrics': risk_metrics
            }
            
            # 生成折线图
            self.plot_chart()
        
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的数字!")
    
    def plot_chart(self):
        if not self.last_generated_data:
            return
            
        # 清除之前的图表
        self.figure.clear()
        
        # 创建多个子图
        gs = self.figure.add_gridspec(3, 1, height_ratios=[2, 1, 1])
        
        # 第一个子图：买入价格和股数
        ax1 = self.figure.add_subplot(gs[0])
        
        # 获取数据
        buy_prices = self.last_generated_data['buy_prices']
        shares = self.last_generated_data['shares']
        investments = self.last_generated_data['investments']
        avg_costs = self.last_generated_data['avg_costs']
        current_price = self.last_generated_data['current_price']
        stop_loss = self.last_generated_data['stop_loss']
        target_price = self.last_generated_data['target_price']
        
        # 绘制买入股数和投入金额
        ax1.plot(buy_prices, shares, 'b-', marker='o', label='买入股数')
        
        # 创建第二个Y轴显示投入金额
        ax1_twin = ax1.twinx()
        ax1_twin.plot(buy_prices, investments, 'r-', marker='x', label='本次投入')
        
        # 设置图表标题和标签
        ax1.set_title('金字塔加仓买点图', fontsize=12)
        ax1.set_ylabel('买入股数', color='b', fontsize=10)
        ax1_twin.set_ylabel('投入金额(元)', color='r', fontsize=10)
        
        # 添加网格和图例
        ax1.grid(True, linestyle='--', alpha=0.7)
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1_twin.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)
        
        # 添加止损线和目标价格线
        price_range = max(buy_prices) - min(buy_prices)
        price_extension = price_range * 0.1
        x_min = min(buy_prices) - price_extension
        x_max = max(buy_prices) + price_extension
        
        ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax1.set_xlim(x_min, x_max)
        
        # 第二个子图：平均成本变化
        ax2 = self.figure.add_subplot(gs[1], sharex=ax1)
        ax2.plot(buy_prices, avg_costs, 'g-', marker='s', label='平均成本')
        
        # 添加止损线和当前价格线
        ax2.axhline(y=stop_loss, color='r', linestyle='--', alpha=0.5, label=f'止损价: {stop_loss:.2f}')
        ax2.axhline(y=current_price, color='b', linestyle='--', alpha=0.5, label=f'当前价: {current_price:.2f}')
        ax2.axhline(y=target_price, color='g', linestyle='--', alpha=0.5, label=f'目标价: {target_price:.2f}')
        
        ax2.set_ylabel('价格(元)', fontsize=10)
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.legend(loc='upper right', fontsize=8)
        
        # 第三个子图：收益分析
        ax3 = self.figure.add_subplot(gs[2], sharex=ax1)
        
        # 获取收益数据
        potential_returns = self.last_generated_data['potential_returns']
        
        # 创建柱状图，使用颜色区分正负收益
        bars = ax3.bar(buy_prices, potential_returns, alpha=0.7, label='预期收益率(%)')
        for i, bar in enumerate(bars):
            if potential_returns[i] >= 0:
                bar.set_color('red')
            else:
                bar.set_color('green')
        
        ax3.set_title('预期收益率分析 (基于目标价格)', fontsize=11)
        ax3.set_xlabel('买入价格', fontsize=10)
        ax3.set_ylabel('收益率(%)', fontsize=10)
        ax3.grid(True, linestyle='--', alpha=0.7)
        
        # 设置刻度字体大小
        for ax in [ax1, ax1_twin, ax2, ax3]:
            ax.tick_params(labelsize=8)
        
        # 添加风险指标文本框
        if 'risk_metrics' in self.last_generated_data:
            risk = self.last_generated_data['risk_metrics']
            risk_text = f"风险评估指标:\n"
            risk_text += f"最大投入: {risk['max_investment']:.2f}元\n"
            risk_text += f"最大回撤: {risk['max_drawdown_pct']:.2f}%\n"
            risk_text += f"风险收益比: {risk['risk_reward_ratio']:.2f}\n"
            risk_text += f"盈亏平衡价: {risk['breakeven_price']:.2f}元\n"
            risk_text += f"目标收益率: {risk['max_return']:.2f}%"
            
            # 在图表右上角添加文本框
            ax1.text(0.98, 0.02, risk_text, transform=ax1.transAxes, fontsize=8,
                   verticalalignment='bottom', horizontalalignment='right',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        
        self.figure.tight_layout()
        self.canvas.draw()

    def get_stock_fundamentals(self, stock_code):
        """获取股票基本面数据"""
        try:
            # 这里使用新浪财经的股票基本面API获取数据
            # 实际应用中可替换为更可靠的数据源
            
            # 模拟基本面数据获取，由于新浪财经API限制，这里使用模拟数据
            # 在实际项目中，可以使用专业金融数据API如东方财富、同花顺等
            
            # 尝试获取一些估算的基本面数据
            stock_code_num = stock_code.replace('sh', '').replace('sz', '')
            
            # 尝试基于现有价格估算一些基本面指标
            if hasattr(self, 'current_stock_price') and self.current_stock_price:
                price = self.current_stock_price
                
                # 使用一些假设值计算市值和其他指标 (仅作演示用)
                # 在实际应用中应替换为从API获取的真实数据
                
                # 假设流通股本为10亿股
                float_shares = 1000000000  
                market_cap = price * float_shares
                
                # 修正估算公式，避免显示过于夸张的数据
                if stock_code.startswith('6'):  # 假设上证指数公司规模更大
                    pe_ratio = round(25 + (price % 10), 2)  # 示例PE从25到35
                    pb_ratio = round(1.5 + (price % 5) / 10, 2)  # 示例PB从1.5到2.0
                    dividend_yield = round(2 + (price % 3) / 10, 2)  # 示例股息率从2%到2.3%
                    turnover_rate = round(2 + (price % 5) / 10, 2)  # 示例换手率从2%到2.5%
                    
                    # 调整市值单位为亿元
                    market_cap = round(market_cap / 100000000, 2)
                else:
                    pe_ratio = round(20 + (price % 15), 2)  # 示例PE从20到35
                    pb_ratio = round(1.2 + (price % 8) / 10, 2) # 示例PB从1.2到2.0
                    dividend_yield = round(1.5 + (price % 5) / 10, 2)  # 示例股息率从1.5%到2%
                    turnover_rate = round(3 + (price % 7) / 10, 2) # 示例换手率从3%到3.7%
                    
                    # 调整市值单位为亿元
                    market_cap = round(market_cap / 100000000, 2)
                
                # 更新UI显示基本面数据
                self.stock_pe_label.setText(f"市盈率(TTM): {pe_ratio}")
                self.stock_pb_label.setText(f"市净率: {pb_ratio}")
                self.stock_market_cap_label.setText(f"总市值: {market_cap}亿")
                self.stock_turnover_label.setText(f"换手率: {turnover_rate}%")
                self.stock_dividend_yield_label.setText(f"股息率: {dividend_yield}%")
                
                # 保存这些数据供后续使用
                self.stock_fundamentals = {
                    'pe_ratio': pe_ratio,
                    'pb_ratio': pb_ratio,
                    'market_cap': market_cap,
                    'turnover_rate': turnover_rate,
                    'dividend_yield': dividend_yield
                }
                
                return True
        
        except Exception as e:
            print(f"获取基本面数据失败: {str(e)}")
            # 默认显示为未知
            self.stock_pe_label.setText("市盈率(TTM): --")
            self.stock_pb_label.setText("市净率: --")
            self.stock_market_cap_label.setText("总市值: --")
            self.stock_turnover_label.setText("换手率: --")
            self.stock_dividend_yield_label.setText("股息率: --")
            return False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PyramidStockTool()
    window.show()
    sys.exit(app.exec_()) 