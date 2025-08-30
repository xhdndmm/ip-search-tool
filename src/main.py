import sys
import json
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView


class IPQueryTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IP查询工具")
        self.setGeometry(300, 300, 900, 650)
        self.setMinimumSize(800, 800)

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
                padding: 10px 20px;
                font-size: 14px;
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
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

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
        self.query_button.setFixedHeight(40)
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
        result_layout.addWidget(self.result_text, 2)

        # 按钮行：复制结果
        copy_layout = QHBoxLayout()
        copy_layout.addStretch()
        copy_button = QPushButton("复制结果")
        copy_button.clicked.connect(self.copy_results)
        copy_layout.addWidget(copy_button)
        result_layout.addLayout(copy_layout)

        # 地图预览
        self.map_view = QWebEngineView()
        self.map_view.setMinimumHeight(250)
        result_layout.addWidget(self.map_view, 3)

        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group, 1)

        # 底部区域（右下角关于按钮）
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        about_button = QPushButton("关于")
        about_button.clicked.connect(self.show_about)
        bottom_layout.addWidget(about_button)
        main_layout.addLayout(bottom_layout)

        # 状态栏
        self.statusBar().showMessage("就绪")

        # 自定义 UA
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0"
        }

    def create_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))
        from PyQt6.QtGui import QPainter, QPen
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(52, 152, 219), 3))
        painter.drawEllipse(10, 10, 44, 44)
        painter.drawArc(10, 10, 44, 44, 0, 180 * 16)
        painter.drawArc(10, 20, 44, 24, 45 * 16, 90 * 16)
        painter.setBrush(QColor(231, 76, 60))
        painter.drawEllipse(28, 28, 8, 8)
        painter.end()
        return pixmap

    def query_own_ip(self):
        self.statusBar().showMessage("正在查询本机IP...")
        QApplication.processEvents()
        try:
            response = requests.get("https://api.ip.sb/geoip", headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.display_results(data, "本机IP信息")
            self.statusBar().showMessage("本机IP查询成功", 3000)
        except Exception as e:
            self.result_text.setText(f"查询本机IP失败: {str(e)}")
            self.statusBar().showMessage("查询失败", 3000)

    def query_ip(self):
        ip = self.ip_input.text().strip()
        if not ip:
            self.query_own_ip()
            return
        self.statusBar().showMessage(f"正在查询IP: {ip}...")
        QApplication.processEvents()
        try:
            response = requests.get(f"https://api.ip.sb/geoip/{ip}", headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.display_results(data, f"IP: {ip} 的查询结果")
            self.statusBar().showMessage("查询成功", 3000)
        except Exception as e:
            self.result_text.setText(f"查询失败: {str(e)}")
            self.statusBar().showMessage("查询失败", 3000)
    def classify_ip(self, data: dict) -> str:
        isp = (data.get("isp") or "").lower()
        org = (data.get("organization") or "").lower()
        asn_org = (data.get("asn_organization") or "").lower()

        text = f"{isp} {org} {asn_org}"

        # 常见云服务商关键字
        cloud_keywords = ["alibaba", "amazon", "aws", "google", "azure", "microsoft",
                          "digitalocean", "ovh", "linode", "vultr", "hetzner", "gcore", "akamai"]
        mobile_keywords = ["mobile", "wireless", "lte", "4g", "5g", "cmcc", "docomo", "vodafone"]
        residential_keywords = ["telecom", "telecomunicaciones", "broadband", "cable",
                                "comcast", "spectrum", "unicom", "电信", "联通", "移动"]
        edu_keywords = ["university", "college", "school", "教育网", "campus"]

        if any(k in text for k in cloud_keywords):
            return "数据中心 / 云服务"
        elif any(k in text for k in mobile_keywords):
            return "移动网络"
        elif any(k in text for k in edu_keywords):
            return "教育/科研网络"
        elif any(k in text for k in residential_keywords):
            return "家宽/住宅宽带"
        else:
            return "未知/通用网络"

    def display_results(self, data, title):
        if not data:
            self.result_text.setText("未获取到有效数据")
            return

        result = f"<h2 style='color:#3498db; text-align:center;'>{title}</h2>"
        result += "<table style='width:100%; border-collapse:collapse; margin-top:20px;'>"
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
        ip_type = self.classify_ip(data)
        result += f"""
        <tr>
            <td style='padding:8px; border-bottom:1px solid #3498db; width:30%; color:#3498db;'>IP类型</td>
            <td style='padding:8px; border-bottom:1px solid #3498db;'>{ip_type}</td>
        </tr>
        """

        result += "</table>"
        self.result_text.setHtml(result)

        # 更新地图
        if "latitude" in data and "longitude" in data:
            lat = data["latitude"]
            lon = data["longitude"]
            map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={lon-0.05}%2C{lat-0.05}%2C{lon+0.05}%2C{lat+0.05}&layer=mapnik&marker={lat}%2C{lon}"
            self.map_view.setUrl(QUrl(map_url))
        else:
            self.map_view.setHtml("<h3 style='color:white; text-align:center;'>无地图数据</h3>")


    def copy_results(self):
        """复制结果到剪贴板"""
        text = self.result_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "没有可复制的内容！")
            return
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage("结果已复制到剪贴板", 3000)

    def show_about(self):
        QMessageBox.information(
            self,
            "关于",
            "IP-Search-Tool v1.0 \n https://github.com/xhdndmm/ip-search-tool"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IPQueryTool()
    window.show()
    sys.exit(app.exec())