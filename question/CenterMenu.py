import sys, os
import json, logging
from PyQt6.QtCore import Qt, QObject, pyqtSlot, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QSizePolicy
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from question.base import Questions, question_show

try:
    d3_js = open("question/base/d3.v7.min.js", "r", encoding="utf-8").read()
except FileNotFoundError as e:
    print(f"file not found cwd:{os.getcwd()}")
    raise e

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s')
logger.setLevel(logging.DEBUG)


class NodeData(QObject):
    updateGraph = pyqtSignal(str)
    positionChanged = pyqtSignal(str)

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
        self.node_names = ["A", "B", "C"]
        self.added_tag = []
        self.upper : GraphWindow | None = None
        self._alive = True  # 新增存活标记

    @pyqtSlot(str)
    def handleNodeClick(self, tag : str):
        logger.debug(f"Node clicked! Tag: {tag}")
        opt = tag.split("::")
        if opt[0] == 'menu':
            self.clear()
            self.upper.add_one_tag(opt[1])
        elif opt[0] == "exit":
            self.clear()
            self.upper.send_initial_data()
        else:
            new_window = question_show.HomeWindow(self.upper, tag)
            new_window.show()

        self.refresh_graph()

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

    def refresh_graph(self):
        self.updateGraph.emit(json.dumps({
            "nodes": self.nodes,
            "links": self.links
        }))

    def clear(self):
        self.nodes.clear()
        self.node_names.clear()
        self.links.clear()

    def add_node(self, name : str, tag : str):
        self.nodes.append({"id" : f"id_{tag}", "tag" : tag, "name" : name, "x": 600, "y": 400})
        self.node_names.append(name)

    def has_added(self, name : str):
        return name in self.node_names

    def add_link(self, a : str, b : str):
        self.links.append({"source": f"id_{a}", "target": f"id_{b}"})


class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("目录")
        self.setGeometry(100, 100, 1200, 800)
        self.channel = QWebChannel()

        self.browser = QWebEngineView()
        self.node_data = NodeData()
        self.node_data.upper = self

        self.browser.page().setWebChannel(self.channel)
        self.channel.registerObject("nodeData", self.node_data)

        self.browser.setHtml(self.generate_html())

        container = QWidget()
        layout = QVBoxLayout()
        container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 移除布局边距
        layout.setSpacing(0)  # 移除组件间距
        layout.addWidget(self.browser)
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.centralWidget().setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        self.question_lib = Questions.QuestionsManager().load_lib(r"题型预测/question.json")
        self.browser.loadFinished.connect(self.init_webchannel)
        self.browser.loadFinished.connect(self.resend_data)
        # QTimer.singleShot(1000, self.send_initial_data)
        self.node_data.refresh_graph()

    def send_initial_data(self):
        """生成目录"""
        self.node_data.clear()
        all_tags = set()
        for _, each_ques in self.question_lib.questions_dir.values():
            for tag in each_ques.tags:
                all_tags.add(tag)

        tag0 = None
        for tag in all_tags:
            self.node_data.add_node(tag, f"menu::{tag}")
            if tag0 is not None:
                self.node_data.add_link(f"menu::{tag0}", f"menu::{tag}")
            tag0 = tag

        self.node_data.updateGraph.emit(json.dumps({
            "nodes": self.node_data.nodes,
            "links": self.node_data.links
        }))

        self.node_data.refresh_graph()

    def add_one_tag(self, tag : str):
        same_tag_list = [q for _, q in self.question_lib.questions_dir.values() if tag in q.tags]
        same_tag_list.sort(key=lambda x: {"简单": 1, "中等": 2, "困难": 3, "空": 4}[x.difficulty])

        q1 = Questions.Question()
        q1.question_id = "exit"
        q1.surface = "exit                 "
        for q in same_tag_list:
            self.node_data.add_node(q1.surface[0:min(len(q1.surface), 5)], q1.question_id)
            self.node_data.add_link(q1.question_id, q.question_id)
            q1 = q
        self.node_data.add_node(q1.surface[0:min(len(q1.surface), 5)], q1.question_id)

    def init_webchannel(self):
        """ 窗口尺寸变化时通知前端 """
        self.browser.page().runJavaScript(f"""
            window.dispatchEvent(new CustomEvent('windowResize', {{
                detail: {{ width: {self.width()}, height: {self.height()} }}
            }}));
        """)

    def resend_data(self):
        """ 带状态检查的数据发送 """
        if self.browser.page().webChannel() is not None:
            self.node_data.refresh_graph()
            print("[PY] 数据已重发")
        else:
            print("[PY] 错误：WebChannel未就绪")

    def generate_html(self):
        code =  f"""
        <!DOCTYPE html>
        <html>
        <html style="width:100%; height:100%; margin:0; padding:0;">
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
                
                window.addEventListener('windowResize', (e) => {{
                    const newWidth = e.detail.width;
                    const newHeight = e.detail.height;
    
                    // 更新画布尺寸
                    svg.attr("width", newWidth)
                       .attr("height", newHeight);

                    // 更新力导向参数
                    simulation.force("center", d3.forceCenter(newWidth/2, newHeight/2))
                             .force("x", d3.forceX(newWidth/2).strength(0.05))
                             .force("y", d3.forceY(newHeight/2).strength(0.05))
                             .alpha(0.5).restart();
                }});

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
                    
                    if(window.existingSimulation) {{
                        window.existingSimulation.stop();
                        window.existingSimulation = null;
                    }}

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
                    const width = 1200, height = 800;
                    svg = d3.select("#graph")
                        .append("svg")
                        .attr("width", width)
                        .attr("height", height);

                    // 初始化力导向模拟
                        simulation = d3.forceSimulation()
                            .force("link", d3.forceLink().id(d => d.id).distance(150))
                            .force("charge", d3.forceManyBody().strength(-120))
                            .force("collide", d3.forceCollide().radius(30))
                            .force("center", d3.forceCenter(width/2, height/2))
                            .force("x", d3.forceX(width/2).strength(0.05))
                            .force("y", d3.forceY(height/2).strength(0.05))
                            .alphaDecay(0.05)  // 降低冷却速度
                            .velocityDecay(0.4);  

                    // 绑定位置同步事件
                    window.nodeData.positionChanged.connect(function(data) {{
                        simulation.nodes(JSON.parse(data));
                        simulation.alpha(0.3).restart();
                    }});
                
                    window.existingSimulation = simulation;

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
                        .text(d => d.name)
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
                        const width = 1200, height = 800;
                        nodeGroups.attr("transform", d => `translate(${{d.x}},${{d.y}})`)
                            .each(function(d) {{
                            const node = d3.select(this);
                            const isNearEdge = d.x < 30 || d.x > width-30 || 
                                            d.y < 30 || d.y > height-30;
                            node.attr("fill", isNearEdge ? "red" : "#2196F3");
                        }});
                    }});
                    
                    

                    simulation.alpha(1).restart();
                }}
            </script>
        </body>
        </html>
        """

        # print(code)
        return code


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphWindow()
    window.show()
    # QTimer.singleShot(10000, lambda: window.node_data.updateNodeTag("A", "new_tag"))
    QTimer.singleShot(1000, lambda: window.send_initial_data())
    sys.exit(app.exec())
