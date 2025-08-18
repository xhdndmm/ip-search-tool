import sys
import json
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QLabel, QLineEdit, QPushButton, QTextEdit, QFrame, QGroupBox
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt6.QtCore import Qt, QSize

class IPQueryTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IP查询工具")
        self.setGeometry(300, 300, 800, 600)
        self.setMinimumSize(700, 500)
        
        # 设置应用图标
        self.setWindowIcon(QIcon(self.create_icon()))
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QGroupBox {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 1ex;
                color: #ecf0f1;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #3498db;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 8px;
                color: #ecf0f1;
                font-size: 16px;
                selection-background-color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QTextEdit {
                background-color: #34495e;
                border: 2px solid #3498db;
                border-radius: 5px;
                color: #ecf0f1;
                font-size: 14px;
                padding: 10px;
            }
        """)
        
        # 创建主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("IP地理位置查询工具")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #3498db;")
        main_layout.addWidget(title_label)
        
        # 输入区域
        input_group = QGroupBox("查询设置")
        input_layout = QVBoxLayout()
        
        input_hbox = QHBoxLayout()
        ip_label = QLabel("IP地址:")
        ip_label.setFont(QFont("Arial", 12))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("输入IP地址（留空查询本机IP）")
        self.ip_input.setFont(QFont("Arial", 12))
        input_hbox.addWidget(ip_label)
        input_hbox.addWidget(self.ip_input)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.query_button = QPushButton("查询IP")
        self.query_button.setFixedHeight(45)
        self.query_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.query_button.clicked.connect(self.query_ip)
        button_layout.addWidget(self.query_button)
        button_layout.addStretch()
        
        input_layout.addLayout(input_hbox)
        input_layout.addLayout(button_layout)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # 结果区域
        result_group = QGroupBox("查询结果")
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont("Consolas", 12))
        result_layout.addWidget(self.result_text)
        
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group, 1)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        # 初始化查询本机IP
        #self.query_own_ip()
    
    def create_icon(self):
        # 创建一个简单的程序图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))  # 透明背景
        
        # 绘制一个简单的网络图标
        from PyQt6.QtGui import QPainter, QPen
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制地球
        painter.setPen(QPen(QColor(52, 152, 219), 3))
        painter.drawEllipse(10, 10, 44, 44)
        
        # 绘制经纬线
        painter.drawArc(10, 10, 44, 44, 0, 180 * 16)
        painter.drawArc(10, 20, 44, 24, 45 * 16, 90 * 16)
        painter.drawArc(10, 30, 44, 4, 135 * 16, 90 * 16)
        
        # 绘制节点
        painter.setBrush(QColor(231, 76, 60))
        painter.drawEllipse(28, 28, 8, 8)
        
        painter.end()
        return pixmap
    
    def query_own_ip(self):
        """查询本机IP并显示结果"""
        self.statusBar().showMessage("正在查询本机IP...")
        QApplication.processEvents()  # 更新UI
        
        try:
            response = requests.get("https://api.ip.sb/geoip")
            response.raise_for_status()
            data = response.json()
            self.display_results(data, "本机IP信息")
            self.statusBar().showMessage("本机IP查询成功", 3000)
        except Exception as e:
            self.result_text.setText(f"查询本机IP失败: {str(e)}")
            self.statusBar().showMessage("查询失败", 3000)
    
    def query_ip(self):
        """查询指定IP"""
        ip = self.ip_input.text().strip()
        
        if not ip:
            self.query_own_ip()
            return
        
        self.statusBar().showMessage(f"正在查询IP: {ip}...")
        QApplication.processEvents()  # 更新UI
        
        try:
            response = requests.get(f"https://api.ip.sb/geoip/{ip}")
            response.raise_for_status()
            data = response.json()
            self.display_results(data, f"IP: {ip} 的查询结果")
            self.statusBar().showMessage("查询成功", 3000)
        except Exception as e:
            self.result_text.setText(f"查询失败: {str(e)}")
            self.statusBar().showMessage("查询失败", 3000)
    
    def display_results(self, data, title):
        """格式化显示查询结果"""
        if not data:
            self.result_text.setText("未获取到有效数据")
            return
        
        # 创建格式化输出
        result = f"<h2 style='color:#3498db; text-align:center;'>{title}</h2>"
        result += "<table style='width:100%; border-collapse:collapse; margin-top:20px;'>"
        
        # 定义字段映射和排序
        fields = [
            ("ip", "IP地址"),
            ("country", "国家"),
            ("country_code", "国家代码"),
            ("region", "地区"),
            ("region_code", "地区代码"),
            ("city", "城市"),
            ("latitude", "纬度"),
            ("longitude", "经度"),
            ("isp", "互联网服务提供商"),
            ("organization", "组织"),
            ("asn", "ASN"),
            ("asn_organization", "ASN组织"),
            ("continent_code", "大洲代码"),
            ("timezone", "时区"),
            ("offset", "时区偏移(秒)")
        ]
        
        # 添加数据行
        for key, label in fields:
            if key in data:
                value = data[key]
                if key in ["latitude", "longitude"]:
                    value = f"{value:.6f}"
                result += f"""
                <tr>
                    <td style='padding:8px; border-bottom:1px solid #3498db; width:30%; color:#3498db;'>{label}</td>
                    <td style='padding:8px; border-bottom:1px solid #3498db;'>{value}</td>
                </tr>
                """
        
        result += "</table>"
        
        # 添加地图链接
        if "latitude" in data and "longitude" in data:
            lat = data["latitude"]
            lon = data["longitude"]
            map_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=12/{lat}/{lon}"
            result += f"<p style='text-align:center; margin-top:20px;'><a href='{map_link}' style='color:#1abc9c;'>查看地理位置 (OpenStreetMap)</a></p>"
        
        self.result_text.setHtml(result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IPQueryTool()
    window.show()
    sys.exit(app.exec())