from flask import Flask, render_template, jsonify
import time
import random
import threading
import requests
import case
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

test_results = []  # 存储测试结果
progress = 0       # 进度百分比
progress_lock = threading.Lock()  # 添加线程锁

# 运行算例的函数
def run_benchmark(case_id, size):
    global progress
    start_time = time.time()
    a,b,c,d = case.test_case(size)
    time.sleep(a)
    end_time = time.time()
    
    result = {
        "case_id": case_id,
        "size": size,
        "time": round(end_time - start_time, 3),
        "accuracy": round(b, 2),
        "efficiency": round(c, 2),
        "resource_usage": round(d, 2)
    }
    
    with progress_lock:  # 使用线程锁保护共享资源
        test_results.append(result)
        progress += 100 / 15  # 更新为实际的算例数量
    
    if len(test_results) >= 15:
        send_wechat_notification()

def send_wechat_notification():
    webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_WEBHOOK_KEY"
    message = {"msgtype": "text", "text": {"content": "所有算例测试已完成！"}}
    requests.post(webhook_url, json=message)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_tests')
def start_tests():
    global test_results, progress
    test_results = []
    progress = 0
    
    # 创建线程池，max_workers设置最大线程数
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交所有任务到线程池
        futures = []
        for i in range(15):
            size = (i+1)*100
            future = executor.submit(run_benchmark, i+1, size)
            futures.append(future)
        
        # 等待所有任务完成
        for future in futures:
            future.result()  # 这里会等待每个任务完成
    
    return jsonify({"message": "算例测试已启动"})

@app.route('/get_results')
def get_results():
    return jsonify({"progress": progress, "results": test_results})

if __name__ == '__main__':
    app.run(debug=True)