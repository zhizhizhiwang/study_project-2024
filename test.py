import sys
import json
from PyQt6.QtCore import Qt, QObject, pyqtSlot, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel


d3_js = open("d3.v7.min.js", "r", encoding="utf-8").read()


class NodeData(QObject):
    updateGraph = pyqtSignal(str)
    positionChanged = pyqtSignal(str)  # 新增位置变化信号

    def __init__(self):
        super().__init__()
        self.nodes = [
            {"id": "A", "tag": "info_A", "x": 0, "y": 0},
            {"id": "B", "tag": "info_B", "x": 0, "y": 0},
            {"id": "C", "tag": "info_C", "x": 0, "y": 0}
        ]
        self.links = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"}
        ]

    @pyqtSlot(str)
    def handleNodeClick(self, tag):
        print(f"Node clicked! Tag: {tag}")

    @pyqtSlot(str, float, float)  # 新增位置处理槽
    def handlePositionChange(self, node_id, x, y):
        for node in self.nodes:
            if node["id"] == node_id:
                node["x"] = x
                node["y"] = y
        self.positionChanged.emit(json.dumps(self.nodes))

    def updateNodeTag(self, node_id, new_tag):
        print("Python端updateNodeTag被调用")
        for node in self.nodes:
            if node["id"] == node_id:
                node["tag"] = new_tag
        self.updateGraph.emit(json.dumps({
            "nodes": self.nodes,
            "links": self.links
        }))


class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Graph with Dragging")
        self.setGeometry(100, 100, 800, 600)
        self.channel = QWebChannel()

        self.browser = QWebEngineView()
        self.node_data = NodeData()

        self.browser.page().setWebChannel(self.channel)
        self.channel.registerObject("nodeData", self.node_data)

        self.browser.setHtml(self.generate_html())

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        container.setLayout(layout)
        self.setCentralWidget(container)

        QTimer.singleShot(1000, self.send_initial_data)

    def send_initial_data(self):
        self.node_data.updateGraph.emit(json.dumps({
            "nodes": self.node_data.nodes,
            "links": self.node_data.links
        }))

    def generate_html(self):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <script >{d3_js}</script>
            <style>
                .node-group {{
                    cursor: move;
                    transition: transform 0.2s;
                }}
                .node-circle {{
                    fill: #2196F3;
                    transition: r 0.2s;
                }}
                .node-text {{
                    fill: white;
                    font-size: 12px;
                    text-anchor: middle;
                    user-select: none;
                    filter: drop-shadow(1px 1px 1px rgba(0,0,0,0.5));
                }}
                .link {{
                    stroke: #666;
                    stroke-width: 2;
                }}
                svg {{
                    border: 1px solid #eee;
                    background-color: #f9f9f9;
                }}
            </style>
        </head>
        <body>
            <div id="graph"></div>
            <script>
                // 初始化状态标志
                let isChannelReady = false;
                let isD3Ready = false;
                let simulation, svg;
                let webChannelLoaded = false;
                let d3Loaded = false;

                // 错误处理
                window.onerror = function(msg, src, line) {{
                    console.error("[全局错误]", msg, "at", src, "line", line);
                }};

                // D3可用性检查
                document.addEventListener('DOMContentLoaded', () => {{
                    if(typeof d3 !== 'undefined') {{
                        isD3Ready = true;
                    }} else {{
                        console.error('D3.js加载失败');
                    }}
                }});
                
                // Qt WebChannel初始化
                new QWebChannel(qt.webChannelTransport, (channel) => {{
                    console.log('WebChannel初始化完成', channel.objects);
                    window.nodeData = channel.objects.nodeData;
                    console.log('nodeData对象可用性', typeof window.nodeData.updateGraph);
                    webChannelLoaded = true;
                    checkInit();
                }});


                
                if (typeof d3 !== 'undefined') {{
                    console.log('D3.js已加载');
                    d3Loaded = true;
                    checkInit();
                }} else {{
                    console.error('D3.js未加载！');
                    // 可在此处动态加载D3作为备选方案
                }}
                function checkInit() {{
                    console.log('检查初始化状态，webChannelLoaded:', webChannelLoaded, 'd3Loaded:', d3Loaded);
                    if (webChannelLoaded && d3Loaded) {{
                        console.log('全部依赖加载完成，开始初始化');
                        realInitialize();
                    }}
                }}

                // 统一初始化入口
                function realInitialize() {{
                    
                    console.log('开始初始化D3图表');
    
                    // 绑定数据更新信号
                    window.nodeData.updateGraph.connect(function(data) {{
                        console.log('接收到新数据:', data);
                        try {{
                            const graph =
                            JSON.parse(data);
                            updateGraph(graph);
                        }} catch (e) {{
                            console.error('解析数据失败:', e);
                        }}
                    }});


                    // 创建SVG画布
                    const width = 800, height = 600;
                    svg = d3.select("#graph")
                        .append("svg")
                        .attr("width", width)
                        .attr("height", height);

                    // 初始化力导向模拟
                    simulation = d3.forceSimulation()
                        .force("link", d3.forceLink().id(d => d.id).distance(100))
                        .force("charge", d3.forceManyBody().strength(-200))
                        .force("collide", d3.forceCollide().radius(30))
                        .force("center", d3.forceCenter(width/2, height/2));


                    // 绑定位置同步事件
                    window.nodeData.positionChanged.connect(function(data) {{
                        simulation.nodes(JSON.parse(data));
                        simulation.alpha(0.3).restart();
                    }});

                    // 触发初始数据加载
//                  console.log('主动请求初始数据');
//                  window.nodeData.updateGraph.emit(JSON.stringify({{
//                      nodes: {json.dumps(self.node_data.nodes)},
//                      links: {json.dumps(self.node_data.links)}
//                  }}));
              }}

                // 拖拽处理函数
                function dragHandler() {{
                    function dragstart(event, d) {{
                        if (!event.active) simulation.alphaTarget(0.3).restart();
                        d.fx = d.x;
                        d.fy = d.y;
                    }}

                    function dragging(event, d) {{
                        d.fx = event.x;
                        d.fy = event.y;
                        window.nodeData.handlePositionChange(d.id, d.fx, d.fy);
                    }}

                    function dragend(event, d) {{
                        if (!event.active) simulation.alphaTarget(0);
                        d.fx = null;
                        d.fy = null;
                    }}

                    return d3.drag()
                        .on("start", dragstart)
                        .on("drag", dragging)
                        .on("end", dragend);
                }}

                // 图形更新函数
                function updateGraph(graph) {{
                    // 更新连线
                    const links = svg.selectAll(".link")
                        .data(graph.links)
                        .join("line")
                        .attr("class", "link");

                    // 更新节点组
                    const nodeGroups = svg.selectAll(".node-group")
                        .data(graph.nodes, d => d.id)
                        .join("g")
                        .attr("class", "node-group")
                        .call(dragHandler())
                        .on("click", function(event, d) {{  // 新增点击事件
                            console.log("[前端] 节点被点击，Tag:", d.tag);
                            window.nodeData.handleNodeClick(d.tag);
                            event.stopPropagation();
                        }});

                    // 更新圆形节点
                    nodeGroups.selectAll(".node-circle")
                        .data(d => [d])
                        .join("circle")
                        .attr("class", "node-circle")
                        .attr("r", 30)
                        .on("mouseover", function() {{
                            d3.select(this).transition().attr("r", 25);
                        }})
                        .on("mouseout", function() {{
                            d3.select(this).transition().attr("r", 20);
                        }})

                    // 更新节点文字
                    nodeGroups.selectAll(".node-text")
                        .data(d => [d])
                        .join("text")
                        .attr("class", "node-text")
                        .attr("dy", "0.3em")
                        .text(d => d.tag)
                        .style("font-size", d => {{
                            const length = d.tag.length;
                            if (length > 15) return "8px";
                            if (length > 10) return "10px";
                            return "12px";
                        }});

                    // 绑定力导向模拟
                    simulation.nodes(graph.nodes);
                    simulation.force("link").links(graph.links);
                    simulation.force("collide").strength(0.7);

                    simulation.on("tick", () => {{
                        links.attr("x1", d => d.source.x)
                            .attr("y1", d => d.source.y)
                            .attr("x2", d => d.target.x)
                            .attr("y2", d => d.target.y);

                        nodeGroups.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
                    }});

                    simulation.alpha(1).restart();
                }}
            </script>
        </body>
        </html>
        """




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphWindow()
    window.show()
    QTimer.singleShot(3000, lambda: window.node_data.updateNodeTag("A", "new_tag"))
    sys.exit(app.exec())
