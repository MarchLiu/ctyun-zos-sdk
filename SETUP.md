# CTyun ZOS SDK 设置指南

## 环境配置

在使用CTyun ZOS SDK之前，您需要配置以下环境变量：

### 必需配置

1. **S3_ACCESS_KEY**: 您的CTyun访问密钥ID
2. **S3_SECRET_KEY**: 您的CTyun秘密访问密钥
3. **S3_REGION**: CTyun区域（如：huabei-2, huadong-1, huadong-2, huanan-1, huanan-2）
4. **S3_ENDPOINT**: CTyun ZOS服务端点URL

### 可选配置

5. **S3_BUCKET**: 测试用的存储桶名称
6. **S3_VERIFY_SSL**: SSL验证设置（true/false）
7. **S3_TIMEOUT**: 请求超时时间（秒）

## 配置方法

### 方法1：环境变量（推荐）

在您的shell中设置环境变量：

```bash
export S3_ACCESS_KEY="your_actual_access_key"
export S3_SECRET_KEY="your_actual_secret_key"
export S3_REGION="huabei-2"
export S3_ENDPOINT="https://huabei-2.zos.ctyun.cn"
export S3_BUCKET="your_bucket_name"
```

### 方法2：.env文件

1. 复制配置文件：
```bash
cp config.env.example .env
```

2. 编辑.env文件，填入您的实际值：
```bash
S3_ACCESS_KEY=your_actual_access_key
S3_SECRET_KEY=your_actual_secret_key
S3_REGION=huabei-2
S3_ENDPOINT=https://huabei-2.zos.ctyun.cn
S3_BUCKET=your_bucket_name
S3_VERIFY_SSL=true
S3_TIMEOUT=30
```

## 测试连接

### 1. 基本功能测试

运行基本功能测试（不需要真实连接）：
```bash
python test_basic.py
```

### 2. 真实连接测试

配置好环境变量后，运行真实连接测试：
```bash
python test_real_connection.py
```

### 3. 单元测试

运行完整的测试套件：
```bash
python -m pytest tests/ -v
```

## 使用示例

### 基本使用

```python
import os
from ctyun_zos_sdk import ZOSSession

# 创建会话
session = ZOSSession(
    aws_access_key_id=os.environ["S3_ACCESS_KEY"],
    aws_secret_access_key=os.environ["S3_SECRET_KEY"],
    region_name="huabei-2",
    endpoint_url="https://huabei-2.zos.ctyun.cn"
)

# 获取S3客户端
s3_client = session.client('s3')

# 上传文件
response = s3_client.put_object(
    Bucket="your-bucket",
    Key="example/test.txt",
    Body="Hello, CTyun ZOS!",
    ContentType="text/plain"
)
print(f"Upload successful! ETag: {response['ETag']}")
```

### 异步使用

```python
import asyncio
import os
from ctyun_zos_sdk import AsyncZOSClient

async def main():
    async with AsyncZOSClient(
        access_key=os.environ["S3_ACCESS_KEY"],
        secret_key=os.environ["S3_SECRET_KEY"],
        region="huabei-2",
        endpoint="https://huabei-2.zos.ctyun.cn"
    ) as client:
        
        response = await client.put_object(
            Bucket="your-bucket",
            Key="async-test.txt",
            Body="Async upload content"
        )
        print(f"Upload successful! ETag: {response['ETag']}")

# 运行异步函数
asyncio.run(main())
```

## 故障排除

### 常见错误

1. **ModuleNotFoundError: No module named 'ctyun_zos_sdk'**
   - 确保已安装依赖：`pip install -r requirements-dev.txt`
   - 检查Python路径设置

2. **Missing required configuration**
   - 检查环境变量是否正确设置
   - 确认.env文件格式正确

3. **Access Denied 或 NoSuchBucket**
   - 检查访问密钥是否正确
   - 确认存储桶名称存在
   - 验证区域和端点配置

4. **SSL Certificate errors**
   - 设置 `S3_VERIFY_SSL=false`（仅用于测试）

### 调试模式

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 支持的区域

- `huabei-2` - 华北2
- `huadong-1` - 华东1  
- `huadong-2` - 华东2
- `huanan-1` - 华南1
- `huanan-2` - 华南2

## 获取帮助

如果遇到问题：

1. 检查环境变量配置
2. 运行测试脚本验证基本功能
3. 查看错误日志
4. 参考 `examples/` 目录中的示例代码
5. 检查 `verified/` 目录中的已验证示例
