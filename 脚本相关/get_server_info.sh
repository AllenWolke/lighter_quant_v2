#!/bin/bash
# Ubuntu服务器信息获取脚本
# 用于生成SSH隧道连接命令

clear
echo "============================================"
echo "  Ubuntu服务器连接信息"
echo "============================================"
echo ""

# 1. 用户名
USERNAME=$(whoami)
echo "当前用户名: $USERNAME"
echo ""

# 2. 所有IP地址
echo "服务器IP地址:"
ip addr show | grep "inet " | grep -v 127.0.0.1 | while read -r line; do
    IP=$(echo $line | awk '{print $2}' | cut -d/ -f1)
    INTERFACE=$(echo $line | awk '{print $NF}')
    echo "  - $IP ($INTERFACE)"
done
echo ""

# 3. 公网IP（如果有）
echo "检查公网IP..."
PUBLIC_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || echo "无法获取")
if [ "$PUBLIC_IP" != "无法获取" ]; then
    echo "  公网IP: $PUBLIC_IP"
else
    echo "  公网IP: 未检测到（可能在内网）"
fi
echo ""

# 4. 主机名
echo "主机名: $(hostname)"
echo ""

# 5. 系统信息
echo "系统版本: $(lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo ""

# 6. 生成SSH隧道命令
echo "============================================"
echo "  SSH隧道命令（复制到本地电脑执行）"
echo "============================================"

# 获取第一个非localhost的IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "方式1: 使用内网IP（局域网访问）"
echo "----------------------------------------------"
echo "ssh -L 3000:localhost:3000 -L 8000:localhost:8000 $USERNAME@$LOCAL_IP"
echo ""

if [ "$PUBLIC_IP" != "无法获取" ] && [ "$PUBLIC_IP" != "$LOCAL_IP" ]; then
    echo "方式2: 使用公网IP（外网访问）"
    echo "----------------------------------------------"
    echo "ssh -L 3000:localhost:3000 -L 8000:localhost:8000 $USERNAME@$PUBLIC_IP"
    echo ""
fi

echo "============================================"
echo "  直接浏览器访问（需开放防火墙）"
echo "============================================"
echo ""
echo "本地访问:"
echo "  http://localhost:3000"
echo ""
echo "远程访问:"
echo "  http://$LOCAL_IP:3000"
if [ "$PUBLIC_IP" != "无法获取" ] && [ "$PUBLIC_IP" != "$LOCAL_IP" ]; then
    echo "  http://$PUBLIC_IP:3000"
fi
echo ""

echo "============================================"
echo "  开放防火墙端口（如需远程访问）"
echo "============================================"
echo ""
echo "sudo ufw allow 3000/tcp"
echo "sudo ufw allow 8000/tcp"
echo "sudo ufw reload"
echo ""

# 7. 检查Web服务状态
echo "============================================"
echo "  Web服务状态"
echo "============================================"
echo ""

if command -v netstat &> /dev/null; then
    if netstat -tln 2>/dev/null | grep -q ":3000"; then
        echo "✓ Web前端运行中 (端口3000)"
    else
        echo "✗ Web前端未运行"
        echo "  启动: cd ~/lighter_quantification_v2 && ./start_all_services.sh"
    fi

    if netstat -tln 2>/dev/null | grep -q ":8000"; then
        echo "✓ Web后端运行中 (端口8000)"
    else
        echo "✗ Web后端未运行"
    fi
else
    if ss -tln 2>/dev/null | grep -q ":3000"; then
        echo "✓ Web前端运行中 (端口3000)"
    else
        echo "✗ Web前端未运行"
    fi

    if ss -tln 2>/dev/null | grep -q ":8000"; then
        echo "✓ Web后端运行中 (端口8000)"
    else
        echo "✗ Web后端未运行"
    fi
fi

echo ""

# 8. 使用说明
echo "============================================"
echo "  使用步骤"
echo "============================================"
echo ""
echo "1. 复制上面的SSH隧道命令"
echo "2. 在本地电脑（Windows/Mac/Linux）打开终端/PowerShell"
echo "3. 粘贴并执行SSH隧道命令"
echo "4. 输入密码（如果需要）"
echo "5. 保持SSH连接窗口打开"
echo "6. 在本地浏览器打开: http://localhost:3000"
echo "7. 登录 (用户名: admin, 密码: admin)"
echo ""

echo "============================================"
echo "  提示"
echo "============================================"
echo ""
echo "• SSH隧道更安全，推荐使用"
echo "• 直接IP访问需要开放防火墙端口"
echo "• 首次登录后请立即修改默认密码"
echo ""

